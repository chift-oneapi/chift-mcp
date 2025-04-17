# 🛠️ Chift MCP OpenAPI Tools Generator

This utility automatically generates MCP toolkit methods from the Chift OpenAPI specification.

## ✨ Features
- Parses OpenAPI JSON schema into structured Python methods
- Converts OpenAPI types to Python types with proper typing hints
- Generates complete docstrings with parameter descriptions
- Maps API operations to appropriate SDK method calls
- Excludes unsupported or deprecated operations

## 🚀 Usage

Run the generator from the tools directory:

```bash
cd src/chift_mcp/tools
python generator.py
```

The generator will:
1. Load the OpenAPI schema from `schema/openapi.json`
2. Parse all endpoints and extract method information
3. Generate a `toolkit.py` file in the current directory
4. Output the number of methods generated

## ⚠️ Post-Generation Steps

After running the generator, you **must** complete these steps:

1. Format the generated code:
   ```bash
   uv run poe format
   ```

2. Lint the code to identify issues:
   ```bash
   uv run poe lint
   ```

3. Review the generated `toolkit.py` file for:
   - Invalid SDK method calls
   - Missing or incorrect model imports
   - Type conversion errors
   - Parameter handling issues

4. Test the generated methods with actual API requests

## 🧩 How It Works

### Parsing Process

1. Endpoints are extracted from the OpenAPI paths
2. Vertical and model information is parsed from each path
3. HTTP methods are mapped to SDK method names (get, create, update, etc.)
4. Request and response schemas are cleaned and processed
5. SDK method calls are generated based on endpoint parameters

### Type Handling

- OpenAPI primitive types are converted to Python types:
  - `string` → `str`
  - `integer` → `int`
  - `boolean` → `bool`
  - `number` → `float`
  - `object` → `dict`
  - `array` → `list`

- Complex Chift types are imported from `chift.openapi.openapi`

### Excluded Operations

The generator maintains a list of excluded operations that won't be included in the output:

```python
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
```

If you need to include or exclude specific operations, modify this list in `generator.py`.

## 🔍 Known Limitations

- Downloads are not supported and excluded from generation
- Complex nested types may require manual adjustments
- Operations with binary responses require special handling
- Some generated types may require manual intervention