import importlib
import inspect

from src.constants import CHIFT_METHOD_NAMES


class ChiftMCPMapper:
    def __init__(
        self,
        parsed_openapi: dict,
        modules: list[str],
        methods: set[str] | None = CHIFT_METHOD_NAMES
    ) -> None:
        self._openapi = parsed_openapi
        self._modules = modules
        self._methods = methods
        self._class_methods = {}
        self._tools = []

    @property
    def tools(self) -> list:
        return self._tools


    @staticmethod
    def standard_methods(model_path: str | None = None):
        return {
            "get": {
                "params": ["chift_id:str"],
                "return_type": model_path or "dict",
            },
            "create": {
                "params": [f"data:{model_path}" if model_path else "data:dict"],
                "return_type": model_path or "dict",
            },
            "update": {
                "params": [
                    "chift_id:str",
                    f"data:{model_path}" if model_path else "data:dict",
                ],
                "return_type": model_path or "dict",
            },
            "delete": {
                "params": ["chift_id:str"],
                "return_type": "bool"
            },
            "all": {
                "params": ["limit:int=None"],
                "return_type": f"list[{model_path}]" if model_path else "list[dict]",
            },
        }

    @staticmethod
    def _generate_docstring(method_name: str, model_name: str, api_description: str | None = None) -> str:
        templates = {
            "get": f"Get {model_name} by ID.",
            "create": f"Create a new {model_name}.",
            "update": f"Update an existing {model_name} by ID.",
            "delete": f"Delete {model_name} by ID.",
            "all": f"Get a list of all {model_name} objects.",
        }
        base_docstring = templates.get(method_name, "")
        if api_description:
            return f"{base_docstring}\n\nAPI: {api_description}"
        return base_docstring


    def analyze_models(
        self,
    ) -> "ChiftMCPMapper":
        for module_name in self._modules:
            area = module_name.split(".")[-1]
            module = importlib.import_module(module_name)

            for name, obj in inspect.getmembers(module, inspect.isclass):
                if obj.__module__ == module_name and not name.endswith("Router"):
                    # Get chift_vertical and chift_model
                    chift_vertical = getattr(obj, "chift_vertical", None)
                    chift_model = getattr(obj, "chift_model", None)

                    # Get model class and name
                    model_class = getattr(obj, "model", None)
                    model_path = f"{model_class.__module__}.{model_class.__name__}" if model_class else None
                    model_name = model_class.__name__ if model_class else name

                    # Get model fields if available
                    model_fields = {}
                    if model_class:
                        for field_name, field_type in getattr(model_class, "__annotations__", {}).items():
                            field_type_name = getattr(field_type, "__name__", str(field_type))
                            model_fields[field_name] = field_type_name

                    # Initialize methods dict
                    methods = {}

                    # Standardized method signatures
                    standard_methods = self.standard_methods(model_path=model_path)

                    # Process existing methods
                    for method_name, method_obj in inspect.getmembers(obj, inspect.isfunction):
                        if method_name in self._methods:
                            # Get existing docstring
                            existing_docstring = inspect.getdoc(method_obj) or ""

                            # Get API description if available
                            api_description = ""
                            if chift_vertical and chift_model and chift_vertical in self._openapi:
                                model_key = chift_model.replace("_", "-")
                                if (model_key in self._openapi[chift_vertical] and
                                    method_name in self._openapi[chift_vertical][model_key]):
                                    api_description = self._openapi[chift_vertical][model_key][method_name].get(
                                        "description",
                                        ""
                                        )

                            # Generate docstring
                            docstring = existing_docstring
                            if not existing_docstring:
                                docstring = self._generate_docstring(method_name, model_name, api_description)
                            elif api_description:
                                docstring = f"{existing_docstring}\n\nAPI: {api_description}"

                            # Add method details
                            methods[method_name] = {
                                "params": standard_methods.get(method_name, {}).get("params", []),
                                "return_type": standard_methods.get(method_name, {}).get("return_type", "Any"),
                                "docstring": docstring,
                            }

                    # Fill in standard methods if not present
                    for method_name in self._methods:
                        if method_name not in methods:
                            # Get API description if available
                            api_desc = ""
                            if chift_vertical and chift_model and chift_vertical in self._openapi:
                                model_key = chift_model.replace("_", "-")
                                if (model_key in self._openapi[chift_vertical] and
                                    method_name in self._openapi[chift_vertical][model_key]):
                                    api_desc = self._openapi[chift_vertical][model_key][method_name].get(
                                        "description",
                                        ""
                                        )

                            # Create standard method entry
                            methods[method_name] = {
                                "params": standard_methods.get(method_name, {}).get("params", []),
                                "return_type": standard_methods.get(method_name, {}).get("return_type", "Any"),
                                "docstring": self._generate_docstring(method_name, model_name, api_desc),
                            }

                    # Add class info
                    self._class_methods[f"{area}.{name}"] = {
                        "methods": methods,
                        "model": model_path,
                        "model_fields": model_fields,
                        "chift_vertical": chift_vertical,
                        "chift_model": chift_model,
                    }
        return self

    def create_mcp_tools(self) -> "ChiftMCPMapper":
        for full_class_name, info in self._class_methods.items():
            area, class_name = full_class_name.split(".")
            methods = info["methods"]

            for method_name, method_info in methods.items():
                tool_name = f"{area}_{class_name}_{method_name}"
                params = method_info["params"]
                response_type = method_info["return_type"]
                docstring = method_info.get("docstring", "")

                # Parse parameter details
                param_details = []
                param_list = []

                for param in params:
                    # Split into name, type, and default
                    param_parts = param.split(":")
                    param_name = param_parts[0]

                    if "=" in param_name:
                        param_name, default_value = param_name.split("=", 1)
                        has_default = True
                    else:
                        default_value = None
                        has_default = False

                    param_type = param_parts[1] if len(param_parts) > 1 else "Any"
                    if has_default:
                        param_type = f"{param_type}={default_value}"
                    param_list.append(f"{param_name}={param_name}")

                    # Store detailed parameter info
                    param_details.append({
                        "name": param_name,
                        "type": param_type.split("=")[0],
                        "default": default_value,
                        "required": not has_default,
                    })

                # Generate function code
                func_code = f"consumer.{area}.{class_name}.{method_name}({', '.join(param_list)})"
                description = docstring if docstring else f"Call {area}.{class_name}.{method_name}"

                # Add model fields info for create and update methods
                model_fields = info.get("model_fields", {})
                if model_fields and method_name in ("create", "update"):
                    field_desc = "\n\nModel fields:\n" + "\n".join(
                        f"- {field}: {type_}" for field, type_ in model_fields.items()
                    )
                    description += field_desc

                tool = {
                    "name": tool_name.lower(),
                    "func": func_code,
                    "params": params,
                    "param_details": param_details,
                    "description": description,
                    "response_type": response_type,
                    "method": method_name,
                    "class_name": class_name,
                    "area": area,
                }
                self.tools.append(tool)

        return self
