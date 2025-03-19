import json
import os
import re



class OpenAPIParser:
    def __init__(self, file_path: str | None = None):
        self._file_path = file_path
        if not self._file_path:
            current_dir = os.path.dirname(os.path.abspath(__file__))
            self._file_path = os.path.join(current_dir, "schema", "openapi.json")

    def parse_openapi_endpoints(self)->dict:
        with open(self._file_path, encoding="utf-8") as f:
            openapi_data = json.load(f)
        endpoints_info = {}
        path_pattern = re.compile(r"/consumers/\{consumer_id\}/([^/]+)/([^/{]+)")
        for path, path_data in openapi_data.get("paths", {}).items():
            match = path_pattern.match(path)
            if not match:
                continue
            vertical, model = match.groups()
            model = model.rstrip("/")
            if "{" in model:
                model = model.split("{")[0].rstrip("/")
            if vertical not in endpoints_info:
                endpoints_info[vertical] = {}

            if model not in endpoints_info[vertical]:
                endpoints_info[vertical][model] = {}

            for method, method_data in path_data.items():
                if method.lower() not in ["get", "post", "put", "delete", "patch"]:
                    continue

                sdk_method = self._http_to_sdk_method(method.lower(), path)

                endpoints_info[vertical][model][sdk_method] = {
                    "endpoint": path,
                    "method": method.upper(),
                    "description": method_data.get(
                        "description", method_data.get("summary", "")
                    ),
                }
        return endpoints_info

    @staticmethod
    def _http_to_sdk_method(http_method: str, path: str)->str:
        mapping = {
            "get": "all" if "{" not in path.split("/")[-1] else "get",
            "post": "create",
            "put": "update",
            "patch": "update",
            "delete": "delete"
        }
        return mapping.get(http_method.lower(), http_method)

