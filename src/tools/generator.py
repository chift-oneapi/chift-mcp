import json
import os
import re

import inflect


class OpenAPIParser:
    # operation_ids
    __EXCLUDED_OPERATIONS = [
        "banking_get_account_transactions",
        "datastores_create_consumer_datastoredata",
        "syncs_get_syncconsumer",
        "datastores_update_consumer_datastoredata",
        "datastores_delete_consumer_datastoredata",
        "banking_get_account_counterparts",
        "banking_get_accounts",
        "banking_get_financial_institutions",
        "pos_get_product_categories",  # TODO: fix models
        "invoicing_get_invoices",  # TODO: fix models
        "invoicing_post_invoices",  # TODO: fix models
        "invoicing_post_products",  # TODO: fix models
        "ecommerce_get_products",  # TODO: fix models
        "ecommerce_get_product",  # TODO: fix models
        "accounting_create_ledger_account",  # TODO: fix models
        "accounting_create_journal",  # TODO: fix models
    ]

    def __init__(self, file_path: str = None) -> None:
        self._file_path = file_path
        if not self._file_path:
            current_dir = os.path.dirname(os.path.abspath(__file__))
            self._file_path = os.path.join(current_dir, "schema", "openapi.json")

        self._openapi_data = None
        self._inflect_engine = inflect.engine()

    def _load_data(self) -> None:
        """Load OpenAPI data from file if not already loaded."""
        if self._openapi_data is None:
            with open(self._file_path, encoding="utf-8") as f:
                self._openapi_data = json.load(f)

    def get_detailed_endpoint_info(self) -> dict:
        """Get detailed endpoint information for SDK mapping."""
        self._load_data()
        detailed_info = {}

        for path, path_data in self._openapi_data.get("paths", {}).items():
            vertical, model = self._extract_vertical_model(path)
            if not vertical or not model:
                continue

            if vertical not in detailed_info:
                detailed_info[vertical] = {}
            if model not in detailed_info[vertical]:
                detailed_info[vertical][model] = {}

            for http_method, method_data in path_data.items():
                if http_method.lower() not in ["get", "post", "put", "delete", "patch"]:
                    continue

                sdk_method = self._http_to_sdk_method(http_method.lower(), path)
                parameters = self._extract_parameters(method_data)
                request_schema = self._extract_request_schema(method_data)
                cleaned_request_schema = self._clean_schema_refs(request_schema) if request_schema else None
                response_schema = self._extract_response_schema(method_data)
                cleaned_response_schema = self._clean_schema_refs(response_schema) if response_schema else None

                detailed_info[vertical][model][sdk_method] = {
                    "endpoint": path,
                    "method": http_method.upper(),
                    "description": method_data.get("description", method_data.get("summary", "")),
                    "operation_id": method_data.get("operationId", ""),
                    "tags": method_data.get("tags", []),
                    "parameters": parameters,
                    "request_schema": cleaned_request_schema,
                    "response_schema": cleaned_response_schema
                }

        return detailed_info

    @staticmethod
    def _extract_vertical_model(path: str) -> tuple[str, str]:
        """Extract vertical and model from API path."""
        std_pattern = re.compile(r"/consumers/\{[^}]+\}/([^/]+)/([^/{]+)")
        match = std_pattern.match(path)
        if match:
            vertical, model = match.groups()
            model = model.rstrip("/")
            if "{" in model:
                model = model.split("{")[0].rstrip("/")
            return vertical, model.replace("-", "_")

        if path == "/consumers" or path.startswith("/consumers/{"):
            return "account", "consumer"

        return None, None

    @staticmethod
    def _http_to_sdk_method(http_method: str, path: str) -> str:
        """Map HTTP method to SDK method name."""
        is_collection = "{" not in path.split("/")[-1]

        mapping = {
            "get": "all" if is_collection else "get",
            "post": "create",
            "put": "update",
            "patch": "update",
            "delete": "delete"
        }

        return mapping.get(http_method.lower(), http_method)

    @staticmethod
    def _extract_parameters(method_data: dict) -> dict:
        """Extract path and query parameters from method data."""
        categorized_params = {
            "path": [],
            "query": []
        }

        for param in method_data.get("parameters", []):
            param_location = param.get("in")
            if param_location in categorized_params:
                schema = param.get("schema", {})
                param_type = schema.get("type", "string")

                # Check if schema has an allOf field with a $ref
                if "allOf" in schema and isinstance(schema["allOf"], list) and len(schema["allOf"]) > 0:
                    ref_item = schema["allOf"][0]
                    if "$ref" in ref_item:
                        # Extract enum type name from reference
                        ref_path = ref_item["$ref"]
                        ref_parts = ref_path.split("/")
                        param_type = ref_parts[-1]  # Get the last part of the path
                param_info = {
                    "name": param.get("name"),
                    "required": param.get("required", False),
                    "type": param_type,
                    "format": schema.get("format", ""),
                    "description": param.get("description", "")
                }

                if "default" in schema:
                    param_info["default"] = schema["default"]

                categorized_params[param_location].append(param_info)

        return categorized_params

    @staticmethod
    def _extract_request_schema(method_data: dict) -> dict:
        """Extract request body schema if present."""
        if "requestBody" not in method_data:
            return None

        request_body = method_data["requestBody"]
        content = request_body.get("content", {})
        json_content = content.get("application/json", {})

        return json_content.get("schema", {})

    @staticmethod
    def _extract_response_schema(method_data: dict) -> dict:
        """Extract response schema from successful response."""
        if "responses" not in method_data:
            return None

        for status_code in ["200", "201", "202", "204"]:
            if status_code in method_data["responses"]:
                response = method_data["responses"][status_code]
                if status_code == "204":
                    return {
                        "type": "boolean"
                    }

                content = response.get("content", {})
                json_content = content.get("application/json", {})
                return json_content.get("schema", {})

        return None

    @staticmethod
    def _clean_schema_refs(schema: dict) -> dict:
        """Clean schema references to extract class names."""
        cleaned = schema.copy()

        if "$ref" in cleaned:
            ref = cleaned["$ref"]
            class_name = ref.split("/")[-1]

            # Transform backbone_common__models__* format to camel case
            if class_name.startswith("backbone_common__models__"):
                parts = class_name.split("__")
                # Convert to PascalCase format
                transformed_name = "".join(part.title().replace("_", "") for part in parts)
                class_name = transformed_name

            if "_" in class_name and class_name.endswith("_"):
                parts = class_name.split("_")
                if len(parts) >= 3:
                    container = parts[0]
                    generic_type = parts[1]
                    cleaned["type"] = f"{container}{generic_type}"  # Changed from f"{container}[{generic_type}]"
                else:
                    cleaned["type"] = class_name
            else:
                cleaned["type"] = class_name
            del cleaned["$ref"]

        if "type" in cleaned and cleaned["type"] == "array" and "items" in cleaned:
            cleaned["items"] = OpenAPIParser._clean_schema_refs(cleaned["items"])

        if "properties" in cleaned:
            for prop_name, prop_schema in cleaned["properties"].items():
                cleaned["properties"][prop_name] = OpenAPIParser._clean_schema_refs(prop_schema)

        return cleaned

    def _add_sdk_method_calls(self, endpoint_info: dict) -> dict:
        """Add SDK method calls to each endpoint in the parsed OpenAPI specification."""
        for vertical, models in endpoint_info.items():
            for model, methods in models.items():
                for method_name, details in methods.items():
                    sdk_model = model[0].upper() + model[1:]
                    # Convert model name to singular form if it's plural
                    singular_model = self._to_singular(sdk_model)
                    sdk_call = self._generate_call_string(vertical, singular_model, method_name, details)
                    details['sdk_call'] = sdk_call

        return endpoint_info

    def _to_singular(self, model_name: str) -> str:
        """Convert model name to singular form if it's plural."""
        # Special case handling for common irregular plurals or specific model names
        special_cases = {
            "Children": "Child",
            "People": "Person",
            "Men": "Man",
            "Women": "Woman",
            "Teeth": "Tooth",
            "Feet": "Foot",
            "Mice": "Mouse",
            "Geese": "Goose",
            # Add any other special cases as needed
        }

        if model_name in special_cases:
            return special_cases[model_name]

        # Use inflect to get singular form
        singular = self._inflect_engine.singular_noun(model_name)

        # If model_name is already singular, singular_noun returns False
        if singular:
            return singular
        return model_name

    @staticmethod
    def _generate_call_string(vertical: str, model: str, method_name: str, details: dict) -> str:
        """Generate SDK method call string based on endpoint details."""
        path_params = details.get('parameters', {}).get('path', [])
        query_params = details.get('parameters', {}).get('query', [])
        has_request_body = details.get('request_schema') is not None

        call = f"consumer.{vertical}.{model}.{method_name}("

        pos_args = []
        if method_name in ['get', 'update', 'delete']:
            for param in path_params:
                param_name = param.get('name', '')
                if param_name != 'consumer_id' and param_name.endswith('_id'):
                    pos_args.append(param_name)
                    break

        if pos_args:
            call += ", ".join(pos_args)

        kwargs = []

        if has_request_body and method_name in ['create', 'update']:
            kwargs.append("data=data")

        for param in path_params:
            param_name = param.get('name', '')
            if param_name != 'consumer_id' and param_name not in pos_args:
                kwargs.append(f"{param_name}={param_name}")

        if query_params:
            # Use double quotes for parameter names
            params_dict = ", ".join([f'"{param["name"]}": {param["name"]}' for param in query_params])
            kwargs.append(f"params={{{params_dict}}}")

        if kwargs:
            if pos_args:
                call += ", "
            call += ", ".join(kwargs)

        call += ")"
        return call

    def generate_toolkit(self, api_schema: dict) -> None:
        """Generate toolkit.py file with methods for all API endpoints"""

        # Collect all unique types for imports
        types_to_import = self.extract_all_types(api_schema=api_schema)

        # Generate file content
        content = self.generate_file_content(api_schema=api_schema, types_to_import=types_to_import)

        # Write to file
        with open("toolkit.py", "w") as f:
            f.write(content)

        print(f"Generated toolkit.py with {content.count('def ')} methods")

    def extract_all_types(self, api_schema: dict) -> set[str]:
        """Extract all types to import from the API schema"""
        types_to_import = set()

        # Process each endpoint to extract types
        for domain in api_schema.values():
            for resource in domain.values():
                for operation in resource.values():
                    if operation.get("operation_id") in self.__EXCLUDED_OPERATIONS:
                        continue
                    # Check response schema
                    if operation.get('response_schema'):
                        response_type = self.extract_type(operation['response_schema'])
                        if response_type:
                            types_to_import.update(response_type)

                    # Check request schema
                    if operation.get('request_schema'):
                        request_type = self.extract_type(operation['request_schema'])
                        if request_type:
                            types_to_import.update(request_type)

                    # Check parameter types
                    if operation.get('parameters'):
                        for param_location in ['path', 'query']:
                            if param_location in operation['parameters']:
                                for param in operation['parameters'][param_location]:
                                    if param.get('type') and not self.is_primitive_type(param['type']):
                                        types_to_import.add(param['type'])

        return types_to_import

    @staticmethod
    def is_primitive_type(type_name: str) -> bool:
        return type_name in ["string", "integer", "boolean", "number", "array", "object"]

    def extract_type(self, schema: dict) -> set[str]:
        """Extract types from a schema definition"""
        types = set()

        if isinstance(schema, dict):
            # Direct type reference
            if 'type' in schema:
                type_str = schema['type']
                if not self.is_primitive_type(type_str):
                    # Transform backbone_common__models__* format to camel case
                    if type_str.startswith("backbone_common__models__"):
                        parts = type_str.split("__")
                        # Convert to PascalCase format
                        type_str = "".join(part.title().replace("_", "") for part in parts)

                    # Check if it's a generic type like ChiftPage[Something]
                    match = re.match(r'(\w+)\[([\w\[\]]+)\]', type_str)
                    if match:
                        container, inner = match.groups()
                        combined_type = f"{container}{inner}"
                        types.add(combined_type)
                    else:
                        types.add(type_str)

            # Items in array
            if 'items' in schema and isinstance(schema['items'], dict) and 'type' in schema['items']:
                item_type = schema['items']['type']
                if not self.is_primitive_type(item_type):
                    # Transform backbone_common__models__* format to camel case
                    if item_type.startswith("backbone_common__models__"):
                        parts = item_type.split("__")
                        # Convert to PascalCase format
                        item_type = "".join(part.title().replace("_", "") for part in parts)
                    types.add(item_type)

        return types

    @staticmethod
    def get_python_type(openapi_type: str) -> str:
        """Convert OpenAPI type to Python type"""
        type_mapping = {
            "string": "str",
            "integer": "int",
            "boolean": "bool",
            "number": "float",
            "object": "dict",
            "array": "list",
        }
        return type_mapping.get(openapi_type, openapi_type)

    @staticmethod
    def get_return_type(schema: dict) -> str:
        """Get the return type from a response schema"""
        if not schema:
            return "None"

        if "type" in schema:
            type_mapping = {
                "string": "str",
                "integer": "int",
                "boolean": "bool",
                "number": "float",
                "object": "dict",
                "array": "list",
            }
            return type_mapping.get(schema["type"], schema["type"])

        return "Any"

    def generate_file_content(self, api_schema: dict, types_to_import: set[str]) -> str:
        """Generate the full content of the toolkit.py file"""
        # Start with imports
        content = "import chift\nimport inflect\nfrom typing import List, Dict, Any, Optional\n"

        if types_to_import:
            content += "from chift.openapi.openapi import " + ", ".join(sorted(types_to_import)) + "\n"

        content += "\n\n"

        # Generate methods for each endpoint
        for domain_name, domain in api_schema.items():
            for resource_name, resource in domain.items():
                for operation_name, operation in resource.items():
                    method = self.generate_method(operation)
                    if method:  # Only add non-empty methods (not excluded)
                        content += method + "\n\n"

        return content

    def generate_method(self, operation: dict) -> str:
        """Generate a method for a specific endpoint"""
        operation_id = operation.get("operation_id", "unknown_operation")

        # Skip excluded operations
        if operation_id in self.__EXCLUDED_OPERATIONS:
            return ""

        description = operation.get("description", "No description available")

        # Build the method signature
        params = ["consumer_id: str"]
        params_with_defaults = []
        docstring_params = ["    Args:\n        consumer_id (str): The consumer ID\n"]
        sdk_params = []

        # Add path parameters
        if "parameters" in operation and "path" in operation["parameters"]:
            for param in operation["parameters"]["path"]:
                if param["name"] != "consumer_id":  # Skip consumer_id as it's already added
                    param_type = self.get_python_type(openapi_type=param["type"])
                    params.append(f"{param['name']}: {param_type}")
                    docstring_params.append(f"        {param['name']} ({param_type}): {param.get('description', '')}\n")

                    # Add to SDK params
                    if "=" not in operation["sdk_call"]:
                        continue
                    sdk_call_parts = operation["sdk_call"].split("=", 1)[1]
                    if f"{param['name']}=" in sdk_call_parts:
                        sdk_params.append(f"{param['name']}={param['name']}")

        # Add body parameter if needed
        if operation.get("request_schema"):
            if "method" in operation and operation["method"] in ["POST", "PUT", "PATCH"]:
                request_type = self.get_return_type(operation["request_schema"])
                params.append(f"data: {request_type}")
                docstring_params.append(f"        data ({request_type}): The request data\n")

                # Add to SDK params
                if "data=" in operation["sdk_call"]:
                    sdk_params.append(f"data=data")

        # Add query parameters with defaults
        if "parameters" in operation and "query" in operation["parameters"]:
            for param in operation["parameters"]["query"]:
                param_type = self.get_python_type(openapi_type=param["type"])

                # Handle optional parameters with defaults
                if not param.get("required", False):
                    default_value = param.get("default", "None")

                    # Convert default value based on type
                    if param_type == "int" and default_value != "None":
                        default_value = int(default_value)
                    elif param_type == "bool" and default_value != "None":
                        default_value = str(default_value).lower() == "true"
                    elif param_type == "BoolParam" and default_value != "None":
                        default_value = f'"{str(default_value).lower()}"'
                    elif (param_type == "str" or not self.is_primitive_type(
                        param_type
                    )) and default_value != "None":
                        default_value = f'"{default_value}"'

                    params_with_defaults.append(f"{param['name']}: Optional[{param_type}] = {default_value}")
                else:
                    params.append(f"{param['name']}: {param_type}")

                docstring_params.append(f"        {param['name']} ({param_type}): {param.get('description', '')}\n")

        # Combine all parameters
        all_params = params + params_with_defaults
        param_string = ", ".join(all_params)

        # Get return type
        return_type = self.get_return_type(operation.get("response_schema", {}))

        # Build the method body
        sdk_call = operation.get("sdk_call", "").strip()

        # If there are parameters in the SDK call, format them correctly
        params_dict = {}
        if "parameters" in operation and "query" in operation["parameters"]:
            for param in operation["parameters"]["query"]:
                params_dict[param["name"]] = param["name"]

        # Build the method
        method = f"def {operation_id}({param_string}) -> {return_type}:\n"
        method += f"    \"\"\"{description}\n\n"
        method += "".join(docstring_params)
        method += f"    \"\"\"\n"
        method += f"    consumer = chift.Consumer.get(chift_id=consumer_id)\n"  # Changed consumer_id to chift_id
        method += f"    return {sdk_call}"

        return method

    def run(self) -> dict:
        """Parse OpenAPI spec, generate SDK calls, and return enriched data."""
        endpoint_info = self.get_detailed_endpoint_info()
        enriched_info = self._add_sdk_method_calls(endpoint_info)
        self.generate_toolkit(enriched_info)
        return enriched_info


parser = OpenAPIParser()
