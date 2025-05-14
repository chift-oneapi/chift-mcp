import json
import os
import re
from datetime import datetime, \
    timezone

import inflect


class OpenAPIParser:
    __EXCLUDED_OPERATIONS = [
        "banking_get_account_transactions",
        "datastores_create_consumer_datastoredata",
        "syncs_get_syncconsumer",
        "datastores_update_consumer_datastoredata",
        "datastores_delete_consumer_datastoredata",
        "banking_get_account_counterparts",
        "banking_get_accounts",
        "banking_get_financial_institutions",
    ]

    def __init__(self, file_path: str | None = None) -> None:
        self._file_path = file_path or os.path.join(
            os.path.dirname(os.path.abspath(__file__)), "schema", "openapi.json"
        )
        self._openapi_data = None
        self._inflect_engine = inflect.engine()

    def _load_data(self) -> None:
        if self._openapi_data is None:
            with open(self._file_path, encoding="utf-8") as f:
                self._openapi_data = json.load(f)

    def run(self) -> dict:
        self._load_data()
        detailed_info = self._extract_detailed_info()
        enriched_info = self._add_sdk_method_calls(detailed_info)
        self.generate_toolkit(enriched_info)
        return enriched_info

    def _extract_detailed_info(self) -> dict:
        result = {}
        for path, path_data in self._openapi_data.get("paths", {}).items():
            vertical, model = self._extract_vertical_model(path)
            if not vertical or not model:
                continue

            result.setdefault(vertical, {}).setdefault(model, {})

            for http_method, method_data in path_data.items():
                if http_method.lower() not in ["get", "post", "put", "delete", "patch"]:
                    continue
                sdk_method = self._http_to_sdk_method(http_method.lower(), path)
                result[vertical][model][sdk_method] = self._build_method_info(
                    path, http_method, method_data
                )

        return result

    def _build_method_info(self, path: str, http_method: str, method_data: dict) -> dict:
        request_schema = self._extract_request_schema(method_data)
        response_schema = self._extract_response_schema(method_data)
        return {
            "endpoint": path,
            "method": http_method.upper(),
            "description": method_data.get("description", method_data.get("summary", "")),
            "operation_id": method_data.get("operationId", ""),
            "tags": method_data.get("tags", []),
            "parameters": self._extract_parameters(method_data),
            "request_schema": self._clean_schema_refs(request_schema) if request_schema else None,
            "response_schema": self._clean_schema_refs(response_schema)
            if response_schema
            else None,
        }

    @staticmethod
    def _extract_vertical_model(path: str) -> tuple[str | None, str | None]:
        match = re.match(r"/consumers/\{[^}]+\}/([^/]+)/([^/{]+)", path)
        if match:
            vertical, model = match.groups()
            model = model.rstrip("/").split("{")[0].rstrip("/")
            return vertical, model.replace("-", "_")
        if path == "/consumers" or path.startswith("/consumers/{"):
            return "account", "consumer"
        return None, None

    @staticmethod
    def _http_to_sdk_method(http_method: str, path: str) -> str:
        is_collection = "{" not in path.split("/")[-1]
        return {
            "get": "all" if is_collection else "get",
            "post": "create",
            "put": "update",
            "patch": "update",
            "delete": "delete",
        }.get(http_method.lower(), http_method)

    @staticmethod
    def _extract_parameters(method_data: dict) -> dict:
        categorized_params = {"path": [], "query": []}
        for param in method_data.get("parameters", []):
            param_location = param.get("in")
            if param_location in categorized_params:
                schema = param.get("schema", {})
                param_type = OpenAPIParser._resolve_schema_type(schema)
                param_info = {
                    "name": param.get("name"),
                    "required": param.get("required", False),
                    "type": param_type,
                    "format": schema.get("format", ""),
                    "description": param.get("description", ""),
                }
                if "default" in schema:
                    param_info["default"] = schema["default"]
                categorized_params[param_location].append(param_info)
        return categorized_params

    @staticmethod
    def _resolve_schema_type(schema: dict) -> str:
        if schema.get("allOf"):
            ref_item = schema["allOf"][0]
            if "$ref" in ref_item:
                return ref_item["$ref"].split("/")[-1]
        return schema.get("type", "string")

    @staticmethod
    def _extract_request_schema(method_data: dict) -> dict | None:
        return (
            method_data.get("requestBody", {})
            .get("content", {})
            .get("application/json", {})
            .get("schema")
        )

    @staticmethod
    def _extract_response_schema(method_data: dict) -> dict | None:
        for status_code in ["200", "201", "202", "204"]:
            if status_code in method_data.get("responses", {}):
                if status_code == "204":
                    return {"type": "boolean"}
                return (
                    method_data["responses"][status_code]
                    .get("content", {})
                    .get("application/json", {})
                    .get("schema")
                )
        return None

    def _clean_schema_refs(self, schema: dict) -> dict:
        cleaned = schema.copy()
        if "$ref" in cleaned:
            cleaned["type"] = self._transform_class_name(cleaned.pop("$ref"))
        if cleaned.get("type") == "array" and "items" in cleaned:
            cleaned["items"] = self._clean_schema_refs(cleaned["items"])
        if "properties" in cleaned:
            for key, prop in cleaned["properties"].items():
                cleaned["properties"][key] = self._clean_schema_refs(prop)
        return cleaned

    @staticmethod
    def _transform_class_name(ref: str) -> str:
        class_name = ref.split("/")[-1]
        if class_name.startswith("backbone_common__models__"):
            parts = class_name.split("__")
            class_name = "".join(part.title().replace("_", "") for part in parts)
        class_name = "".join(word for word in class_name.replace("-", " ").split())
        if class_name.endswith("_") and "_" in class_name:
            parts = class_name.split("_")
            if len(parts) >= 3:
                return f"{parts[0]}{parts[1]}"
        return class_name

    def _add_sdk_method_calls(self, endpoint_info: dict) -> dict:
        for vertical, models in endpoint_info.items():
            for model, methods in models.items():
                for method_name, details in methods.items():
                    sdk_model = self._to_singular(model.capitalize())
                    details["sdk_call"] = self._generate_call_string(
                        vertical, sdk_model, method_name, details
                    )
        return endpoint_info

    def _to_singular(self, model_name: str) -> str:
        return self._inflect_engine.singular_noun(model_name) or model_name

    @staticmethod
    def _generate_call_string(vertical: str, model: str, method_name: str, details: dict) -> str:
        path_params = details.get("parameters", {}).get("path", [])
        query_params = details.get("parameters", {}).get("query", [])
        has_body = details.get("request_schema") is not None

        call = f"consumer.{vertical}.{model}.{method_name}("
        args = []
        if method_name in ["get", "update", "delete"]:
            id_param = next(
                (
                    p["name"]
                    for p in path_params
                    if p["name"] != "consumer_id" and p["name"].endswith("_id")
                ),
                None,
            )
            if id_param:
                args.append(id_param)

        kwargs = []
        if has_body and method_name in ["create", "update"]:
            kwargs.append("data=data")
        for param in path_params:
            if param["name"] != "consumer_id" and param["name"] not in args:
                kwargs.append(f"{param['name']}={param['name']}")
        if query_params:
            # Use double quotes for parameter names
            params_dict = ", ".join(
                [f'"{param["name"]}": {param["name"]}' for param in query_params]
            )
            kwargs.append(f"params={{{params_dict}}}")

        call += ", ".join(args + kwargs) + ")"
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
                    if operation.get("response_schema"):
                        response_type = self.extract_type(operation["response_schema"])
                        if response_type:
                            types_to_import.update(response_type)

                    # Check request schema
                    if operation.get("request_schema"):
                        request_type = self.extract_type(operation["request_schema"])
                        if request_type:
                            types_to_import.update(request_type)

                    # Check parameter types
                    if operation.get("parameters"):
                        for param_location in ["path", "query"]:
                            if param_location in operation["parameters"]:
                                for param in operation["parameters"][param_location]:
                                    if param.get("type") and not self.is_primitive_type(
                                        param["type"]
                                    ):
                                        types_to_import.add(param["type"])

        return types_to_import

    @staticmethod
    def is_primitive_type(type_name: str) -> bool:
        return type_name in ["string", "integer", "boolean", "number", "array", "object"]

    def extract_type(self, schema: dict) -> set[str]:
        """Extract types from a schema definition"""
        types = set()

        if isinstance(schema, dict):
            # Direct type reference
            if "type" in schema:
                type_str = schema["type"]
                if not self.is_primitive_type(type_str):
                    # Transform backbone_common__models__* format to camel case
                    if type_str.startswith("backbone_common__models__"):
                        parts = type_str.split("__")
                        # Convert to PascalCase format
                        type_str = "".join(part.title().replace("_", "") for part in parts)

                    # Fix for "ProductItem - Input" format - remove spaces and dashes
                    type_str = "".join(word for word in type_str.replace("-", " ").split())

                    # Check if it's a generic type like ChiftPage[Something]
                    match = re.match(r"(\w+)\[([\w\[\]]+)\]", type_str)
                    if match:
                        container, inner = match.groups()
                        combined_type = f"{container}{inner}"
                        types.add(combined_type)
                    else:
                        types.add(type_str)

            # Items in array
            if (
                "items" in schema
                and isinstance(schema["items"], dict)
                and "type" in schema["items"]
            ):
                item_type = schema["items"]["type"]
                if not self.is_primitive_type(item_type):
                    # Transform backbone_common__models__* format to camel case
                    if item_type.startswith("backbone_common__models__"):
                        parts = item_type.split("__")
                        # Convert to PascalCase format
                        item_type = "".join(part.title().replace("_", "") for part in parts)

                    # Fix for "ProductItem - Input" format - remove spaces and dashes
                    item_type = "".join(word for word in item_type.replace("-", " ").split())

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
        header = (
            f"# This file was automatically generated by running `python generator.py`\n"
            f"# Generated on: {datetime.now(tz=timezone.utc).strftime('%Y-%m-%d %H:%M:%S %Z')}\n\n"
        )
        imports = "import chift\nimport inflect\nfrom typing import List, Dict, Any, Optional\n"
        content = header + imports

        if types_to_import:
            content += (
                "from chift.openapi.openapi import " + ", ".join(sorted(types_to_import)) + "\n"
            )

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
                    docstring_params.append(
                        f"        {param['name']} ({param_type}): {param.get('description', '')}\n"
                    )

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
                    sdk_params.append("data=data")

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
                    elif (
                        param_type == "str" or not self.is_primitive_type(param_type)
                    ) and default_value != "None":
                        default_value = f'"{default_value}"'

                    params_with_defaults.append(
                        f"{param['name']}: Optional[{param_type}] = {default_value}"
                    )
                else:
                    params.append(f"{param['name']}: {param_type}")

                docstring_params.append(
                    f"        {param['name']} ({param_type}): {param.get('description', '')}\n"
                )

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
        method += f'    """{description}\n\n'
        method += "".join(docstring_params)
        method += '    """\n'
        method += "    consumer = chift.Consumer.get(chift_id=consumer_id)\n"  # Changed consumer_id to chift_id
        method += f"    return {sdk_call}"

        return method


if __name__ == "__main__":
    parser = OpenAPIParser()
    parser.run()
