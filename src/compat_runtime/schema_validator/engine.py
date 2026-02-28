from __future__ import annotations

from typing import Any


def _path_join(path: str, key: str) -> str:
    return f"{path}.{key}" if path != "$" else f"$.{key}"


def _matches_type(value: Any, expected: str) -> bool:
    if expected == "string":
        return isinstance(value, str)
    if expected == "integer":
        return isinstance(value, int) and not isinstance(value, bool)
    if expected == "number":
        return (isinstance(value, int) or isinstance(value, float)) and not isinstance(value, bool)
    if expected == "boolean":
        return isinstance(value, bool)
    if expected == "object":
        return isinstance(value, dict)
    if expected == "array":
        return isinstance(value, list)
    if expected == "null":
        return value is None
    return True


def _validate_node(value: Any, schema: dict[str, Any], path: str, errors: list[str]) -> None:
    expected_type = schema.get("type")
    expected_types: list[str] = (
        [expected_type] if isinstance(expected_type, str) else list(expected_type or [])
    )

    if expected_types and not any(_matches_type(value, item) for item in expected_types):
        errors.append(
            f"{path}: expected type {'|'.join(expected_types)}, got {type(value).__name__}"
        )
        return

    if isinstance(value, dict):
        required = schema.get("required", [])
        for key in required:
            if key not in value:
                errors.append(f"{_path_join(path, key)}: missing required field")

        properties = schema.get("properties", {})
        if isinstance(properties, dict):
            for key, inner in properties.items():
                if key in value and isinstance(inner, dict):
                    _validate_node(value[key], inner, _path_join(path, key), errors)

    if isinstance(value, list):
        items = schema.get("items")
        if isinstance(items, dict):
            for idx, item in enumerate(value):
                _validate_node(item, items, f"{path}[{idx}]", errors)


def validate_against_schema(payload: Any, schema: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    _validate_node(payload, schema, "$", errors)
    return errors
