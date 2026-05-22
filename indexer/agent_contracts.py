from __future__ import annotations


def agent_capabilities_manifest() -> dict:
    names = [
        "list_repos",
        "search_symbols_tool",
        "locate_from_error_tool",
        "resolve_symbol_tool",
        "impact_analysis_tool",
        "change_plan_tool",
        "change_set_tool",
        "post_edit_verify_tool",
        "coverage_map_tool",
        "index_diff_report_tool",
        "cross_repo_graph_tool",
        "agent_capabilities_manifest_tool",
    ]
    tools = {
        name: {
            "modes": ["local", "remote"] if name != "list_repos" else ["remote"],
            "input_schema": _capability_input_schema(name),
            "output_schema": {"type": "object", "required": _capability_required_output(name)},
            "example": _capability_example(name),
            "next_tools": _capability_next_tools(name),
        }
        for name in names
    }
    return {
        "local_and_remote": True,
        "tools": tools,
        "json_schema": _agent_json_schema(tools),
        "remote_note": "Remote tools that analyze local uncommitted changes require diff/changed_files payloads.",
        "recommended_flow": [
            "list_repos",
            "locate_from_error_tool or search_symbols_tool",
            "resolve_symbol_tool",
            "impact_analysis_tool",
            "change_plan_tool",
            "change_set_tool",
            "post_edit_verify_tool",
        ],
    }


def agent_schema() -> dict:
    manifest = agent_capabilities_manifest()
    return {
        "openapi": "3.1.0",
        "info": {
            "title": "repo-wiki Agent API",
            "version": "1.0.0",
            "description": "Machine-readable contract for local and remote Agent code-location workflows.",
        },
        "paths": {
            endpoint: {
                method: {
                    "summary": tool_name,
                    "requestBody": {
                        "required": method == "post",
                        "content": {
                            "application/json": {
                                "schema": spec["input_schema"],
                                "example": spec["example"],
                            }
                        },
                    },
                    "responses": {
                        "200": {
                            "description": "Agent tool response",
                            "content": {
                                "application/json": {
                                    "schema": spec["output_schema"],
                                }
                            },
                        }
                    },
                }
            }
            for tool_name, endpoint, method, spec in _endpoint_specs(manifest["tools"])
        },
        "components": {
            "schemas": {
                "AgentCapabilities": manifest["json_schema"],
                "AgentToolResponse": {"type": "object", "additionalProperties": True},
            }
        },
    }


def _capability_input_schema(name: str) -> dict:
    schemas = {
        "search_symbols_tool": _object_schema({"query": "string", "repo": "string?", "top_k": "int?", "expand_depth": "int?"}, ["query"]),
        "locate_from_error_tool": _object_schema({"error_text": "string", "repo": "string?", "top_k": "int?"}, ["error_text"]),
        "resolve_symbol_tool": _object_schema({"query": "string", "repo": "string?", "file_hint": "string?", "type_hint": "string?"}, ["query"]),
        "impact_analysis_tool": _object_schema({"symbol_id": "string", "repo": "string?", "max_depth": "int?"}, ["symbol_id"]),
        "change_plan_tool": _object_schema({"goal": "string", "symbol_id": "string", "repo": "string?"}, ["goal", "symbol_id"]),
        "change_set_tool": _object_schema({"goal": "string", "symbol_id": "string?", "diff": "string?", "changed_files": "string[]?", "repo": "string?", "max_results": "int?", "include_details": "bool?"}, ["goal"]),
        "post_edit_verify_tool": _object_schema({"diff": "string?", "changed_files": "string[]?", "repo": "string?"}, []),
        "coverage_map_tool": _object_schema({"symbol_id": "string?", "repo": "string?", "max_results": "int?"}, []),
        "index_diff_report_tool": _object_schema({"before_nodes": "object[]", "after_nodes": "object[]", "repo": "string?"}, []),
        "cross_repo_graph_tool": _object_schema({"repos": "string[]?", "max_results": "int?"}, []),
        "agent_capabilities_manifest_tool": _object_schema({}, []),
        "list_repos": _object_schema({}, []),
    }
    return schemas.get(name, {})


def _capability_required_output(name: str) -> list[str]:
    outputs = {
        "search_symbols_tool": ["results", "total"],
        "locate_from_error_tool": ["candidates", "total"],
        "resolve_symbol_tool": ["status", "candidates"],
        "impact_analysis_tool": ["symbol", "affected_files", "risk_points"],
        "change_plan_tool": ["read_these_files", "edit_targets", "verify_commands"],
        "change_set_tool": ["must_change_files", "related_symbols", "verify_commands"],
        "post_edit_verify_tool": ["changed_files", "changed_symbols", "verify_commands"],
        "coverage_map_tool": ["covered", "tests"],
        "index_diff_report_tool": ["added_symbols", "removed_symbols", "call_graph_changes"],
        "cross_repo_graph_tool": ["edges", "total"],
        "agent_capabilities_manifest_tool": ["tools", "recommended_flow"],
        "list_repos": ["repos"],
    }
    return outputs.get(name, [])


def _capability_example(name: str) -> dict:
    examples = {
        "search_symbols_tool": {"query": "JWT validation", "repo": "backend"},
        "locate_from_error_tool": {"error_text": "POST /login returned 500", "repo": "backend"},
        "resolve_symbol_tool": {"query": "login endpoint", "repo": "backend"},
        "impact_analysis_tool": {"symbol_id": "src/auth.py::validate_token", "repo": "backend"},
        "change_plan_tool": {"goal": "fix token validation", "symbol_id": "src/auth.py::validate_token", "repo": "backend"},
        "change_set_tool": {"goal": "fix token validation", "diff": "diff --git ...", "repo": "backend"},
        "post_edit_verify_tool": {"diff": "diff --git ...", "repo": "backend"},
        "coverage_map_tool": {"symbol_id": "src/auth.py::validate_token", "repo": "backend"},
        "index_diff_report_tool": {"before_nodes": [], "after_nodes": [], "repo": "backend"},
        "cross_repo_graph_tool": {"repos": ["frontend", "backend"]},
        "agent_capabilities_manifest_tool": {"call": "agent_capabilities_manifest_tool()"},
        "list_repos": {"call": "list_repos()"},
    }
    return examples.get(name, {})


def _capability_next_tools(name: str) -> list[str]:
    flow = {
        "list_repos": ["search_symbols_tool", "locate_from_error_tool"],
        "search_symbols_tool": ["resolve_symbol_tool"],
        "locate_from_error_tool": ["resolve_symbol_tool", "impact_analysis_tool"],
        "resolve_symbol_tool": ["impact_analysis_tool", "change_plan_tool"],
        "impact_analysis_tool": ["change_plan_tool", "change_set_tool"],
        "change_plan_tool": ["change_set_tool"],
        "change_set_tool": ["post_edit_verify_tool"],
        "post_edit_verify_tool": ["coverage_map_tool"],
    }
    return flow.get(name, [])


def _object_schema(fields: dict[str, str], required: list[str]) -> dict:
    return {
        "type": "object",
        "properties": {name: _field_schema(spec) for name, spec in fields.items()},
        "required": required,
        "additionalProperties": False,
    }


def _field_schema(spec: str) -> dict:
    nullable = spec.endswith("?")
    base = spec[:-1] if nullable else spec
    schema = {
        "string": {"type": "string"},
        "int": {"type": "integer"},
        "bool": {"type": "boolean"},
        "string[]": {"type": "array", "items": {"type": "string"}},
        "object[]": {"type": "array", "items": {"type": "object", "additionalProperties": True}},
    }.get(base, {"type": "string"})
    if nullable:
        schema = dict(schema)
        schema["nullable"] = True
    return schema


def _agent_json_schema(tools: dict[str, dict]) -> dict:
    return {
        "type": "object",
        "required": ["local_and_remote", "tools", "recommended_flow"],
        "properties": {
            "local_and_remote": {"type": "boolean"},
            "tools": {
                "type": "object",
                "properties": {
                    name: {
                        "type": "object",
                        "required": ["modes", "input_schema", "output_schema", "example"],
                        "properties": {
                            "modes": {"type": "array", "items": {"type": "string"}},
                            "input_schema": spec["input_schema"],
                            "output_schema": spec["output_schema"],
                            "example": {"type": "object", "additionalProperties": True},
                            "next_tools": {"type": "array", "items": {"type": "string"}},
                        },
                    }
                    for name, spec in tools.items()
                },
                "additionalProperties": False,
            },
            "recommended_flow": {"type": "array", "items": {"type": "string"}},
            "remote_note": {"type": "string"},
        },
    }


def _endpoint_specs(tools: dict[str, dict]) -> list[tuple[str, str, str, dict]]:
    endpoints = {
        "list_repos": ("/repos", "get"),
        "search_symbols_tool": ("/search", "post"),
        "locate_from_error_tool": ("/locate-from-error", "post"),
        "resolve_symbol_tool": ("/resolve-symbol", "post"),
        "impact_analysis_tool": ("/impact-analysis", "post"),
        "change_plan_tool": ("/change-plan", "post"),
        "change_set_tool": ("/change-set", "post"),
        "post_edit_verify_tool": ("/post-edit-verify", "post"),
        "coverage_map_tool": ("/coverage-map", "post"),
        "index_diff_report_tool": ("/index-diff-report", "post"),
        "cross_repo_graph_tool": ("/cross-repo-graph", "post"),
        "agent_capabilities_manifest_tool": ("/agent-capabilities", "get"),
    }
    return [
        (name, endpoint, method, tools[name])
        for name, (endpoint, method) in endpoints.items()
        if name in tools
    ]
