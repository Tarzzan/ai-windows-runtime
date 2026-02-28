from __future__ import annotations

import argparse

from compat_runtime.common.io import read_json, write_json
from compat_runtime.schema_validator.engine import validate_against_schema


def validate_artifact(artifact_path: str, schema_path: str) -> dict:
    artifact = read_json(artifact_path)
    schema = read_json(schema_path)
    errors = validate_against_schema(artifact, schema)
    return {
        "artifact_path": artifact_path,
        "schema_path": schema_path,
        "valid": len(errors) == 0,
        "errors": errors,
    }


def main() -> None:
    parser = argparse.ArgumentParser(description="Validate JSON artifact against repository schema")
    parser.add_argument("--input", required=True, help="Artifact JSON path")
    parser.add_argument("--schema", required=True, help="Schema JSON path")
    parser.add_argument("--report", required=False, help="Optional validation report output")
    args = parser.parse_args()

    report = validate_artifact(args.input, args.schema)
    if args.report:
        write_json(args.report, report)

    if not report["valid"]:
        for error in report["errors"]:
            print(error)
        raise SystemExit(1)

    print("validation: ok")


if __name__ == "__main__":
    main()
