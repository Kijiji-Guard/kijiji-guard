"""
BasePolicy — shared helpers for all Kijiji-Guard HCL policy classes.

hcl2 parse notes (v8.x):
  - Resource type keys are quoted strings:  '"aws_s3_bucket"'
  - Resource name keys are quoted strings:  '"my_bucket"'
  - String attribute values are quoted:     '"af-south-1"'
  - Boolean / int values are native Python: True, 20
  - Tag keys are unquoted; tag values are quoted strings
  - Each block dict may contain __is_block__, __comments__ metadata keys
"""
from __future__ import annotations

import json
import re


def _strip(s: object) -> str:
    """Remove surrounding double-quotes that hcl2 adds to string tokens."""
    if isinstance(s, str) and len(s) >= 2 and s[0] == '"' and s[-1] == '"':
        return s[1:-1]
    return str(s) if not isinstance(s, str) else s


class BasePolicy:
    """Base class for all HCL policy checkers."""

    country:    str = ""
    regulation: str = ""

    def __init__(self, parsed_hcl: dict, filepath: str) -> None:
        self.hcl      = parsed_hcl
        self.filepath = filepath
        self.findings: list[dict] = []

    def run(self) -> list[dict]:
        """Discover and run every check_* method; return accumulated findings."""
        for method_name in sorted(dir(self)):
            if method_name.startswith("check_"):
                getattr(self, method_name)()
        return self.findings

    # ------------------------------------------------------------------ #
    # Finding constructors                                                 #
    # ------------------------------------------------------------------ #

    def passed(self, check_id: str, check_name: str, resource: str,
               regulation: str | None = None, remediation: str = "") -> None:
        self._add("PASSED", check_id, check_name, resource, regulation, remediation)

    def failed(self, check_id: str, check_name: str, resource: str,
               regulation: str | None = None, remediation: str = "") -> None:
        self._add("FAILED", check_id, check_name, resource, regulation, remediation)

    def warned(self, check_id: str, check_name: str, resource: str,
               regulation: str | None = None, remediation: str = "") -> None:
        self._add("WARN", check_id, check_name, resource, regulation, remediation)

    def _add(self, result: str, check_id: str, check_name: str, resource: str,
             regulation: str | None, remediation: str) -> None:
        self.findings.append({
            "check_id":    check_id,
            "check_name":  check_name,
            "result":      result,
            "resource":    resource,
            "file_path":   self.filepath,
            "regulation":  regulation or self.regulation,
            "remediation": remediation,
        })

    # ------------------------------------------------------------------ #
    # HCL helpers                                                          #
    # ------------------------------------------------------------------ #

    def get_resources(self, resource_type: str) -> list[tuple[str, dict]]:
        """
        Return (name, config) tuples for every resource of the given type.

        Handles hcl2 quirks:
          - Keys may be quoted: '"aws_s3_bucket"' must match 'aws_s3_bucket'
          - rtype_val can be a dict or a list wrapping a dict
          - Individual resource config blocks are often wrapped in a list
        """
        results: list[tuple[str, dict]] = []
        for block in self.hcl.get("resource", []):
            for rtype_key, rtype_val in block.items():
                if rtype_key.startswith("_"):
                    continue
                if _strip(rtype_key) != resource_type:
                    continue
                # hcl2 occasionally wraps the name→config dict in a list
                if isinstance(rtype_val, list):
                    rtype_val = rtype_val[0] if rtype_val else {}
                if not isinstance(rtype_val, dict):
                    continue
                for name_key, config in rtype_val.items():
                    if name_key.startswith("_"):
                        continue
                    clean_name = _strip(name_key)
                    # Individual resource configs are wrapped in a list by hcl2
                    if isinstance(config, list):
                        config = config[0] if config else {}
                    if not isinstance(config, dict):
                        config = {}
                    results.append((clean_name, config))
        return results

    def _get_provider_region(self) -> str:
        """Extract the configured region from the first AWS provider block."""
        for block in self.hcl.get("provider", []):
            for key, config in block.items():
                if key.startswith("_"):
                    continue
                if _strip(key) == "aws":
                    if isinstance(config, list):
                        config = config[0] if config else {}
                    if isinstance(config, dict):
                        return _strip(config.get("region", ""))
        return ""

    def _get_tags(self, config: dict) -> dict[str, str]:
        """Return tags as {key: unquoted_value} dict."""
        tags = config.get("tags", {})
        if isinstance(tags, list):
            tags = tags[0] if tags else {}
        if not isinstance(tags, dict):
            return {}
        return {k: _strip(v) for k, v in tags.items() if not k.startswith("_")}

    def _str(self, config: dict, key: str, default: str = "") -> str:
        """Get a config attribute as a plain unquoted string."""
        val = config.get(key, default)
        if isinstance(val, bool):
            return str(val).lower()
        return _strip(val) if val is not None else default

    @staticmethod
    def _has_wildcard_action(policy: object) -> bool:
        """Return True only when an IAM Allow statement has Action: '*'.

        Avoids false positives on resource ARNs like 'arn:aws:s3:::bucket/*'.
        """
        if isinstance(policy, dict):
            data = policy
        elif isinstance(policy, str):
            try:
                data = json.loads(policy)
            except (json.JSONDecodeError, ValueError):
                # Fallback: regex that targets Action field specifically
                return bool(re.search(r'"Action"\s*:\s*(?:"\*"|\[\s*"\*"\s*\])', policy))
        else:
            return False
        for stmt in (data.get("Statement") or []):
            if not isinstance(stmt, dict):
                continue
            if stmt.get("Effect", "Allow") != "Allow":
                continue
            action = stmt.get("Action", [])
            if isinstance(action, str) and action == "*":
                return True
            if isinstance(action, list) and "*" in action:
                return True
        return False

    def _resolve_region(self, config: dict) -> str:
        """
        Resolve the effective region for a resource:
        1. Explicit 'region' attribute on the resource
        2. Provider default region
        3. Tags['Region'] (metadata only, weak signal)
        """
        r = self._str(config, "region")
        if r:
            return r
        r = self._get_provider_region()
        if r:
            return r
        tags = self._get_tags(config)
        return tags.get("Region", tags.get("region", ""))
