import copy
import json
from pathlib import Path
from typing import Any


def resolve_openapi_refs(openapi_spec: dict[str, Any]) -> dict[str, Any]:
    """
    Parse OpenAPI JSON and resolve all $ref references by replacing them
    with their actual component definitions.

    Handles recursive references properly by tracking visited refs to prevent
    infinite loops.

    Args:
        openapi_spec: The OpenAPI specification dictionary

    Returns:
        A new OpenAPI specification with all $ref references resolved
    """
    # Deep copy to avoid modifying the original
    resolved_spec = copy.deepcopy(openapi_spec)

    # Extract components/schemas for reference resolution
    components_schemas = resolved_spec.get("components", {}).get("schemas", {})

    def resolve_refs_recursive(obj: Any, visited_refs: set[str] | None = None) -> Any:
        """
        Recursively resolve $ref references in the object.

        Args:
            obj: The object to process (can be dict, list, or any value)
            visited_refs: Set of already visited refs to prevent infinite loops

        Returns:
            The object with all $ref references resolved
        """
        if visited_refs is None:
            visited_refs = set()

        if isinstance(obj, dict):
            # Check if this is a $ref object
            if "$ref" in obj and len(obj) == 1:
                ref_path = obj["$ref"]

                # Only handle component schema references
                if ref_path.startswith("#/components/schemas/"):
                    schema_name = ref_path.split("/")[-1]

                    # Prevent infinite recursion
                    if ref_path in visited_refs:
                        # Return a reference marker to indicate circular dependency
                        return {"$circular_ref": ref_path}

                    if schema_name in components_schemas:
                        # Add to visited set
                        new_visited = visited_refs | {ref_path}

                        # Recursively resolve the referenced schema
                        resolved_schema = resolve_refs_recursive(
                            components_schemas[schema_name], new_visited
                        )
                        return resolved_schema
                    else:
                        # Schema not found, keep the reference as is
                        return obj
                else:
                    # Non-component reference, keep as is
                    return obj
            else:
                # Regular dictionary, process all values
                result = {}
                for key, value in obj.items():
                    result[key] = resolve_refs_recursive(value, visited_refs)
                return result

        elif isinstance(obj, list):
            # Process all items in the list
            return [resolve_refs_recursive(item, visited_refs) for item in obj]
        else:
            # Primitive value, return as is
            return obj

    # Resolve references in the entire specification
    resolved_spec = resolve_refs_recursive(resolved_spec)

    return resolved_spec


def load_and_resolve_openapi(file_path: str) -> dict[str, Any]:
    """
    Load OpenAPI JSON file and resolve all $ref references.

    Args:
        file_path: Path to the OpenAPI JSON file

    Returns:
        Resolved OpenAPI specification dictionary
    """
    with open(file_path, encoding="utf-8") as f:
        openapi_spec = json.load(f)

    return resolve_openapi_refs(openapi_spec)


def save_resolved_openapi(resolved_spec: dict[str, Any], output_path: str) -> None:
    """
    Save the resolved OpenAPI specification to a JSON file.

    Args:
        resolved_spec: The resolved OpenAPI specification
        output_path: Path where to save the resolved specification
    """
    with open(output_path, "w") as f:
        json.dump(resolved_spec, f, indent=2, ensure_ascii=False)


if __name__ == "__main__":
    # Example usage
    current_dir = Path(__file__).parent
    input_file = current_dir / "openapi.json"
    output_file = current_dir / "openapi_resolved.json"

    if input_file.exists():
        print(f"Loading OpenAPI spec from {input_file}")
        resolved_spec = load_and_resolve_openapi(str(input_file))

        print(f"Saving resolved spec to {output_file}")
        save_resolved_openapi(resolved_spec, str(output_file))

        print("OpenAPI references resolved successfully!")
    else:
        print(f"OpenAPI file not found: {input_file}")
