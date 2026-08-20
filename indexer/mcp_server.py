# indexer/mcp_server.py
from __future__ import annotations
import json
import hmac
import logging
from pathlib import Path
from mcp.server.fastmcp import FastMCP
from indexer.config import load_config

logger = logging.getLogger(__name__)


def _apply_mcp_auth(mcp: FastMCP, mcp_api_key: str | None) -> None:
    _orig_method = mcp.streamable_http_app

    if mcp_api_key:
        mcp.settings.transport_security.enable_dns_rebinding_protection = False
        logger.warning("DNS rebinding protection disabled for MCP server (auth enabled)")

    def _patched_method():
        app = _orig_method()

        if mcp_api_key:
            from starlette.middleware.base import BaseHTTPMiddleware
            from starlette.responses import JSONResponse

            class _MCPAuthMiddleware(BaseHTTPMiddleware):
                async def dispatch(self, request, call_next):
                    auth = request.headers.get("Authorization", "")
                    token = auth[7:] if auth.lower().startswith("bearer ") else auth
                    if not token or not hmac.compare_digest(token, mcp_api_key):
                        return JSONResponse({"error": "unauthorized"}, status_code=401)
                    return await call_next(request)
            app = _MCPAuthMiddleware(app)

        return app

    mcp.streamable_http_app = _patched_method


def create_server(repo_root: Path | None = None, mcp_api_key: str | None = None) -> FastMCP:
    if repo_root is None:
        repo_root = Path.cwd()

    cfg = load_config(repo_root)

    mcp = FastMCP("repo-wiki-rag")

    @mcp.tool()
    def search_symbols_tool(query: str, top_k: int = 10, expand_depth: int = 1, retrieval: str = "preferred") -> str:
        """Search code symbols by semantic query. Returns matching symbols with descriptions,
        file locations, and optionally related symbols via call graph expansion.

        Use this when: analyzing a bug report, finding code related to an error message,
        locating where a feature is implemented, or understanding what a module does.

        Args:
            query: Natural language description of what you're looking for (e.g. "JWT token validation", "database connection pool")
            top_k: Number of top results to return (default 10)
            expand_depth: How many hops in the call graph to expand (0=no expansion, 1=direct callers/callees)
            retrieval: local, preferred, or required dense retrieval
        """
        from indexer.retrieval import search_code
        top_k = max(1, min(top_k, 100))
        expand_depth = max(0, min(expand_depth, 5))
        response = search_code(
            query,
            cfg,
            repo_root,
            top_k=top_k,
            expand_depth=expand_depth,
            retrieval=retrieval,
        )
        hits = response["matches"]
        if not hits:
            return "No matching symbols found. Try a different query or ensure the repo has been indexed with `repo-wiki run`."

        degradation = ", ".join(response.get("degradations", [])) or "none"
        lines = [
            f"Generation {response['generation']} @ {response['tree_id'][:12]} "
            f"({response['retrieval']}; degradation: {degradation})",
            "## Matches",
        ]
        for h in hits:
            meta = h.get("metadata", {})
            score = h.get("score", 0.0)
            lines.append(
                f"**{h['id']}** (score: {score:.4f})\n"
                f"  Type: {meta.get('type', '?')} | File: {meta.get('file', '?')} | "
                f"Lines: {meta.get('line_start', '?')}-{meta.get('line_end', '?')}\n"
                f"  {h.get('document', '')}"
            )
        if response["related"]:
            lines.append("## Related")
            for h in response["related"]:
                meta = h.get("metadata", {})
                lines.append(
                    f"**{h['id']}** ({h.get('relation', 'related')})\n"
                    f"  Type: {meta.get('type', '?')} | File: {meta.get('file', '?')}"
                )
        return "\n\n".join(lines)

    @mcp.tool()
    def trace_call_tool(symbol_id: str, direction: str = "down", max_depth: int = 3) -> str:
        max_depth = max(1, min(max_depth, 8))
        """Trace the call graph from a symbol. Follows calls (down) or callers (up) up to max_depth hops.

        Use this when: understanding how a bug propagates through the codebase, tracing an end-to-end
        request flow, finding all callers of a function that needs to be modified, or identifying
        the root cause of an error by tracing upstream.

        Args:
            symbol_id: Component ID in format "path/to/file.py::ClassName.method" or "path/to/file.py::function_name"
            direction: "down" (follow calls this symbol makes) or "up" (follow callers of this symbol)
            max_depth: Maximum hops in the call graph (default 3)
        """
        if direction not in ("up", "down"):
            return f"Invalid direction '{direction}'. Must be 'up' or 'down'."
        from indexer.retrieval import trace_call
        nodes = trace_call(symbol_id, cfg, repo_root, direction=direction, max_depth=max_depth)
        if not nodes:
            return f"Symbol '{symbol_id}' not found in the current generation. Ensure the repo has been indexed."

        chain = []
        for n in nodes:
            meta = n.get("metadata", {})
            chain.append(
                f"{n['id']}\n"
                f"  File: {meta.get('file', '?')} | Lines: {meta.get('line_start', '?')}-{meta.get('line_end', '?')}\n"
                f"  {n.get('document', '')}"
            )

        header = f"Call trace ({direction}) from {symbol_id}, depth={max_depth}:"
        return header + "\n\n" + "\n→ ".join(chain)

    @mcp.tool()
    def get_source_context_tool(file_path: str, line_start: int, line_end: int, padding: int = 5) -> str:
        """Read source code context around specific lines. Returns the code with line numbers
        and optional padding lines before/after the specified range.

        Use this when: you need to see the actual implementation after locating a symbol via search or trace,
        reviewing the exact code that needs to be modified for a bug fix, or understanding the
        context around an error location.

        Args:
            file_path: Repository-relative file path (e.g. "src/auth/token_validator.py")
            line_start: Start line number
            line_end: End line number
            padding: Extra lines to include before and after the range (default 5)
        """
        if line_start < 1 or line_end < 1 or line_end < line_start:
            return f"Invalid line range: line_start={line_start}, line_end={line_end}. Must be >= 1 and line_end >= line_start."
        if padding < 0 or padding > 50:
            return f"Invalid padding: {padding}. Must be 0-50."
        from indexer.retrieval import get_source_context
        return get_source_context(file_path, line_start, line_end, repo_root, padding=padding)

    @mcp.tool()
    def get_edit_context_tool(symbol_id: str, padding: int = 8) -> str:
        """Return an edit-ready context bundle for a symbol: source, callers, callees,
        sibling symbols, candidate tests, and index freshness.

        Use this before modifying code after a symbol has been located.
        """
        padding = max(0, min(padding, 50))
        from indexer.retrieval import get_edit_context
        context = get_edit_context(symbol_id, cfg, repo_root, padding=padding)
        return json.dumps(context, indent=2)

    @mcp.tool()
    def resolve_symbol_tool(query: str, file_hint: str = "", type_hint: str = "", top_k: int = 10) -> str:
        """Resolve a natural language query or symbol name to a concrete component_id."""
        top_k = max(1, min(top_k, 50))
        from indexer.retrieval import resolve_symbol
        return json.dumps(
            resolve_symbol(query, cfg, repo_root, file_hint=file_hint, type_hint=type_hint, top_k=top_k),
            indent=2,
        )

    @mcp.tool()
    def find_tests_for_symbol_tool(symbol_id: str, max_results: int = 10) -> str:
        """Find likely test files for a symbol based on indexed files, symbol names,
        imports, and test naming conventions.
        """
        max_results = max(1, min(max_results, 50))
        from indexer.retrieval import find_tests_for_symbol
        matches = find_tests_for_symbol(symbol_id, cfg, repo_root, max_results=max_results)
        return json.dumps({"results": matches, "total": len(matches)}, indent=2)

    @mcp.tool()
    def pre_edit_check_tool(symbol_id: str) -> str:
        """Run pre-edit checks for a symbol: index freshness, dirty files, tests, commands, impact hints."""
        from indexer.retrieval import pre_edit_check
        return json.dumps(pre_edit_check(symbol_id, cfg, repo_root), indent=2)

    @mcp.tool()
    def impact_analysis_tool(symbol_id: str, max_depth: int = 2) -> str:
        """Analyze the likely impact of changing a symbol: callers, callees, tests,
        entry points, affected files, risk points, and index freshness.
        """
        max_depth = max(1, min(max_depth, 5))
        from indexer.retrieval import impact_analysis
        return json.dumps(impact_analysis(symbol_id, cfg, repo_root, max_depth=max_depth), indent=2)

    @mcp.tool()
    def change_plan_tool(goal: str, symbol_id: str) -> str:
        """Create an agent-ready modification plan for a goal and target symbol."""
        from indexer.retrieval import change_plan
        return json.dumps(change_plan(goal, symbol_id, cfg, repo_root), indent=2)

    @mcp.tool()
    def diagnose_index_tool() -> str:
        """Diagnose generation integrity, Wiki projection, source files, and freshness."""
        from indexer.retrieval import diagnose_index
        return json.dumps(diagnose_index(repo_root, cfg), indent=2)

    @mcp.tool()
    def agent_protocol_tool(goal: str, symbol_id: str, protocol: str = "codex") -> str:
        """Return compact agent protocol fields: files to read, edit targets,
        verification commands, warnings, and index freshness.
        """
        from indexer.retrieval import agent_protocol_bundle
        return json.dumps(agent_protocol_bundle(goal, symbol_id, cfg, repo_root, protocol=protocol), indent=2)

    @mcp.tool()
    def locate_from_error_tool(error_text: str, top_k: int = 10) -> str:
        """Locate likely code symbols from a stack trace, error log, HTTP path, or exception text."""
        top_k = max(1, min(top_k, 50))
        from indexer.retrieval import locate_from_error
        return json.dumps(locate_from_error(error_text, cfg, repo_root, top_k=top_k), indent=2)

    @mcp.tool()
    def list_entry_points_tool(kind: str = "", max_results: int = 50) -> str:
        """List indexed API/CLI/event/job/webhook entry points."""
        max_results = max(1, min(max_results, 200))
        from indexer.retrieval import list_entry_points
        return json.dumps(list_entry_points(cfg, repo_root, kind=kind, max_results=max_results), indent=2)

    @mcp.tool()
    def post_edit_verify_tool(diff: str = "", changed_files: list[str] | None = None) -> str:
        """Verify local edits before commit. If diff is omitted, reads local git diff."""
        from indexer.retrieval import post_edit_verify
        return json.dumps(post_edit_verify(cfg, repo_root, diff=diff, changed_files=changed_files), indent=2)

    @mcp.tool()
    def change_set_tool(
        goal: str,
        symbol_id: str = "",
        diff: str = "",
        changed_files: list[str] | None = None,
        max_results: int = 50,
        include_details: bool = True,
    ) -> str:
        """Build a must-change set from a goal plus target symbol or diff."""
        max_results = max(1, min(max_results, 500))
        from indexer.retrieval import change_set
        return json.dumps(
            change_set(
                goal,
                cfg,
                repo_root,
                symbol_id=symbol_id,
                diff=diff,
                changed_files=changed_files,
                max_results=max_results,
                include_details=include_details,
            ),
            indent=2,
        )

    @mcp.tool()
    def coverage_map_tool(symbol_id: str = "", max_results: int = 100) -> str:
        """Map source symbols to likely covering tests."""
        max_results = max(1, min(max_results, 500))
        from indexer.retrieval import coverage_map
        return json.dumps(coverage_map(cfg, repo_root, symbol_id=symbol_id, max_results=max_results), indent=2)

    @mcp.tool()
    def index_diff_report_tool(before_nodes: list[dict] | None = None, after_nodes: list[dict] | None = None) -> str:
        """Summarize symbol, entry point, and call graph changes between two index snapshots."""
        from indexer.retrieval import index_diff_report
        return json.dumps(index_diff_report(cfg, repo_root, before_nodes=before_nodes or [], after_nodes=after_nodes or []), indent=2)

    @mcp.tool()
    def cross_repo_graph_tool(max_results: int = 200) -> str:
        """Local mode has one repo, so returns an empty cross-repo graph."""
        max_results = max(1, min(max_results, 1000))
        from indexer.retrieval import cross_repo_graph
        return json.dumps(cross_repo_graph({"local": {"root": repo_root, "config": cfg}}, max_results=max_results), indent=2)

    @mcp.tool()
    def agent_capabilities_manifest_tool() -> str:
        """Return tool capability manifest and recommended Agent flow."""
        from indexer.retrieval import agent_capabilities_manifest
        return json.dumps(agent_capabilities_manifest(), indent=2)

    @mcp.tool()
    def stable_symbol_id_tool(symbol_id: str, symbol_type: str = "", file_path: str = "", source: str = "") -> str:
        """Generate deterministic stable symbol id for rename/move tracking."""
        from indexer.retrieval import stable_symbol_id
        return json.dumps({"stable_symbol_id": stable_symbol_id(symbol_id, symbol_type, file_path, source)}, indent=2)

    @mcp.tool()
    def get_index_status_tool() -> str:
        """Report whether the local index is stale relative to the current workspace."""
        from indexer.retrieval import get_index_status
        return json.dumps(get_index_status(repo_root), indent=2)

    _apply_mcp_auth(mcp, mcp_api_key)
    return mcp


def create_api_server(api_url: str, api_key: str | None = None, mcp_api_key: str | None = None) -> FastMCP:
    if not api_url or not api_url.startswith(("http://", "https://")):
        raise ValueError(f"api_url must start with http:// or https://, got: {api_url!r}")
    import urllib.request
    import urllib.error

    mcp = FastMCP("repo-wiki-rag")

    def _api_request(path: str, method: str = "GET", body: dict | None = None, timeout: int = 30) -> dict:
        url = f"{api_url.rstrip('/')}{path}"
        data = json.dumps(body or {}).encode() if method == "POST" else None
        headers = {"Accept": "application/json"}
        if method == "POST":
            headers["Content-Type"] = "application/json"
        if api_key:
            headers["Authorization"] = f"Bearer {api_key}"
        req = urllib.request.Request(url, data=data, headers=headers, method=method)
        try:
            with urllib.request.urlopen(req, timeout=timeout) as resp:
                return json.loads(resp.read(10 * 1024 * 1024))
        except json.JSONDecodeError:
            return {"error": "Invalid JSON response from API"}
        except urllib.error.HTTPError as e:
            return {"error": f"HTTP {e.code}: {e.reason}"}
        except urllib.error.URLError as e:
            return {"error": f"Connection error: {e.reason}"}

    def _api_get(path: str) -> dict:
        return _api_request(path, method="GET")

    def _api_post(path: str, body: dict | None = None) -> dict:
        return _api_request(path, method="POST", body=body, timeout=60)

    @mcp.tool()
    def list_repos() -> str:
        """List all registered repositories. Returns repo names, descriptions, tags, and basic stats.

        Use this first to discover which repos are available before searching or tracing.
        The description and tags help you understand which repo is relevant to the user's task.
        """
        data = _api_get("/repos")
        repos = data.get("repos", [])
        if not repos:
            return "No repos registered. Use the REST API to register repos first."

        lines = ["**Registered Repositories:**\n"]
        for r in repos:
            generation_tag = f" generations={r.get('generations', {})}" if r.get("generations") else ""
            desc = r.get("description", "")
            tags = r.get("tags", [])
            desc_tag = f" — {desc}" if desc else ""
            tags_tag = f"  `{' '.join(f'#{t}' for t in tags)}`" if tags else ""
            lines.append(
                f"- **{r['name']}**{generation_tag}{desc_tag}{tags_tag}\n"
                f"  {r.get('symbol_count', '?')} symbols"
                f"{', dense ready' if r.get('dense_ready') else ', local retrieval only'}"
            )
        return "\n".join(lines)

    @mcp.tool()
    def search_symbols_tool(query: str, repo: str | None = None, branch: str | None = None, top_k: int = 10, expand_depth: int = 1, retrieval: str = "preferred") -> str:
        """Search code symbols by semantic query across one or all registered repos.
        Returns matching symbols with descriptions, file locations, and related symbols.

        Use this when: analyzing a bug report, finding code related to an error message,
        locating where a feature is implemented, or understanding what a module does.

        Args:
            query: Natural language description of what you're looking for (e.g. "JWT token validation", "database connection pool")
            repo: Repository name to search in. If omitted, searches across all repos.
            branch: Required when the selected repository indexes multiple branches.
            top_k: Number of top results to return (default 10)
            expand_depth: How many hops in the call graph to expand (0=no expansion, 1=direct callers/callees)
            retrieval: local, preferred, or required dense retrieval
        """
        body = {
            "query": query,
            "top_k": top_k,
            "expand_depth": expand_depth,
            "retrieval": retrieval,
        }
        if repo:
            body["repo"] = repo
        if branch:
            body["branch"] = branch

        data = _api_post("/search", body)

        if data.get("error"):
            return f"Search error: {data['error']}"

        hits = data.get("results", [])
        if not hits:
            return "No matching symbols found. Try a different query or ensure repos have been indexed."

        header = f"**Search results** ({data.get('total', len(hits))} hits)"
        metrics = data.get("search_metrics", [])
        if metrics:
            scopes = ", ".join(
                f"{item.get('repo')}:{item.get('branch')}@g{item.get('generation')}"
                for item in metrics
            )
            header += f"\nScopes: {scopes}"
        header += "\n"

        lines = [header]
        for h in hits:
            meta = h.get("metadata", {})
            dist = h.get("distance", 0.0)
            repo_tag = f" [{h.get('repo', '?')}]" if "repo" in h else ""
            lines.append(
                f"**{h['id']}**{repo_tag} (distance: {dist:.4f})\n"
                f"  Type: {meta.get('type', '?')} | File: {meta.get('file', '?')} | "
                f"Lines: {meta.get('line_start', '?')}-{meta.get('line_end', '?')}\n"
                f"  {h.get('document', '')}"
            )
        return "\n\n".join(lines)

    @mcp.tool()
    def trace_call_tool(symbol_id: str, repo: str, direction: str = "down", max_depth: int = 3) -> str:
        max_depth = max(1, min(max_depth, 8))
        """Trace the call graph from a symbol. Follows calls (down) or callers (up) up to max_depth hops.

        Use this when: understanding how a bug propagates through the codebase, tracing an end-to-end
        request flow, finding all callers of a function that needs to be modified.

        Args:
            symbol_id: Component ID in format "path/to/file.py::ClassName.method" or "path/to/file.py::function_name"
            repo: Repository name the symbol belongs to
            direction: "down" (follow calls this symbol makes) or "up" (follow callers of this symbol)
            max_depth: Maximum hops in the call graph (default 3)
        """
        if direction not in ("up", "down"):
            return f"Invalid direction '{direction}'. Must be 'up' or 'down'."
        if not repo:
            return "repo is required"
        body = {
            "symbol_id": symbol_id,
            "repo": repo,
            "direction": direction,
            "max_depth": max_depth,
        }
        data = _api_post("/trace", body)

        if data.get("error"):
            return f"Trace error: {data['error']}"

        nodes = data.get("results", [])
        if not nodes:
            return f"Symbol '{symbol_id}' not found in repo '{repo}'. Ensure the repo has been indexed."

        chain = []
        for n in nodes:
            meta = n.get("metadata", {})
            chain.append(
                f"{n['id']}\n"
                f"  File: {meta.get('file', '?')} | Lines: {meta.get('line_start', '?')}-{meta.get('line_end', '?')}\n"
                f"  {n.get('document', '')}"
            )

        header = f"Call trace ({direction}) from {symbol_id} in {repo}, depth={max_depth}:"
        return header + "\n\n" + "\n→ ".join(chain)

    @mcp.tool()
    def get_source_context_tool(file_path: str, repo: str, line_start: int, line_end: int, padding: int = 5) -> str:
        """Read source code context around specific lines. Returns the code with line numbers
        and optional padding lines before/after the specified range.

        Use this when: you need to see the actual implementation after locating a symbol via search or trace,
        reviewing the exact code that needs to be modified for a bug fix.

        Args:
            file_path: Repository-relative file path (e.g. "src/auth/token_validator.py")
            repo: Repository name the file belongs to
            line_start: Start line number
            line_end: End line number
            padding: Extra lines to include before and after the range (default 5)
        """
        if not repo:
            return "repo is required"
        if line_start < 1 or line_end < 1 or line_end < line_start:
            return f"Invalid line range: line_start={line_start}, line_end={line_end}. Must be >= 1 and line_end >= line_start."
        if padding < 0 or padding > 50:
            return f"Invalid padding: {padding}. Must be 0-50."
        body = {
            "file_path": file_path,
            "repo": repo,
            "line_start": line_start,
            "line_end": line_end,
            "padding": padding,
        }
        data = _api_post("/source", body)

        if data.get("error"):
            return f"Source error: {data['error']}"

        return data.get("source", "No source returned.")

    @mcp.tool()
    def get_edit_context_tool(symbol_id: str, repo: str, padding: int = 8) -> str:
        """Return an edit-ready context bundle for a symbol in a registered repo."""
        if not repo:
            return "repo is required"
        padding = max(0, min(padding, 50))
        data = _api_post("/edit-context", {"symbol_id": symbol_id, "repo": repo, "padding": padding})
        if data.get("error"):
            return f"Edit context error: {data['error']}"
        return json.dumps(data, indent=2)

    @mcp.tool()
    def resolve_symbol_tool(query: str, repo: str, file_hint: str = "", type_hint: str = "", top_k: int = 10) -> str:
        """Resolve a query or symbol name to a concrete component_id in a registered repo."""
        if not repo:
            return "repo is required"
        top_k = max(1, min(top_k, 50))
        data = _api_post(
            "/resolve-symbol",
            {"query": query, "repo": repo, "file_hint": file_hint, "type_hint": type_hint, "top_k": top_k},
        )
        if data.get("error"):
            return f"Resolve symbol error: {data['error']}"
        return json.dumps(data, indent=2)

    @mcp.tool()
    def find_tests_for_symbol_tool(symbol_id: str, repo: str, max_results: int = 10) -> str:
        """Find likely test files for a symbol in a registered repo."""
        if not repo:
            return "repo is required"
        max_results = max(1, min(max_results, 50))
        data = _api_post("/tests-for-symbol", {"symbol_id": symbol_id, "repo": repo, "max_results": max_results})
        if data.get("error"):
            return f"Tests lookup error: {data['error']}"
        return json.dumps(data, indent=2)

    @mcp.tool()
    def pre_edit_check_tool(symbol_id: str, repo: str) -> str:
        """Run pre-edit checks for a symbol in a registered repo."""
        if not repo:
            return "repo is required"
        data = _api_post("/pre-edit-check", {"symbol_id": symbol_id, "repo": repo})
        if data.get("error"):
            return f"Pre-edit check error: {data['error']}"
        return json.dumps(data, indent=2)

    @mcp.tool()
    def impact_analysis_tool(symbol_id: str, repo: str, max_depth: int = 2) -> str:
        """Analyze likely impact of changing a symbol in a registered repo."""
        if not repo:
            return "repo is required"
        max_depth = max(1, min(max_depth, 5))
        data = _api_post("/impact-analysis", {"symbol_id": symbol_id, "repo": repo, "max_depth": max_depth})
        if data.get("error"):
            return f"Impact analysis error: {data['error']}"
        return json.dumps(data, indent=2)

    @mcp.tool()
    def change_plan_tool(goal: str, symbol_id: str, repo: str) -> str:
        """Create an agent-ready modification plan for a registered repo."""
        if not repo:
            return "repo is required"
        data = _api_post("/change-plan", {"goal": goal, "symbol_id": symbol_id, "repo": repo})
        if data.get("error"):
            return f"Change plan error: {data['error']}"
        return json.dumps(data, indent=2)

    @mcp.tool()
    def diagnose_index_tool(repo: str | None = None) -> str:
        """Diagnose index integrity for one or all registered repos."""
        body = {}
        if repo:
            body["repo"] = repo
        data = _api_post("/diagnose-index", body)
        if data.get("error"):
            return f"Diagnose index error: {data['error']}"
        return json.dumps(data, indent=2)

    @mcp.tool()
    def agent_protocol_tool(goal: str, symbol_id: str, repo: str, protocol: str = "codex") -> str:
        """Return compact agent protocol fields for a registered repo."""
        if not repo:
            return "repo is required"
        data = _api_post(
            "/agent-protocol",
            {"goal": goal, "symbol_id": symbol_id, "repo": repo, "protocol": protocol},
        )
        if data.get("error"):
            return f"Agent protocol error: {data['error']}"
        return json.dumps(data, indent=2)

    @mcp.tool()
    def locate_from_error_tool(error_text: str, repo: str | None = None, top_k: int = 10) -> str:
        """Locate likely code symbols from a stack trace, error log, HTTP path, or exception text."""
        top_k = max(1, min(top_k, 50))
        body = {"error_text": error_text, "top_k": top_k}
        if repo:
            body["repo"] = repo
        data = _api_post("/locate-from-error", body)
        if data.get("error"):
            return f"Locate from error error: {data['error']}"
        return json.dumps(data, indent=2)

    @mcp.tool()
    def list_entry_points_tool(repo: str | None = None, kind: str = "", max_results: int = 50) -> str:
        """List indexed API/CLI/event/job/webhook entry points."""
        max_results = max(1, min(max_results, 200))
        body = {"kind": kind, "max_results": max_results}
        if repo:
            body["repo"] = repo
        data = _api_post("/entry-points", body)
        if data.get("error"):
            return f"List entry points error: {data['error']}"
        return json.dumps(data, indent=2)

    @mcp.tool()
    def post_edit_verify_tool(repo: str, diff: str = "", changed_files: list[str] | None = None) -> str:
        """Verify edits before commit. In remote mode pass local diff payload explicitly."""
        if not repo:
            return "repo is required"
        body = {"repo": repo, "diff": diff, "changed_files": changed_files or []}
        data = _api_post("/post-edit-verify", body)
        if data.get("error"):
            return f"Post-edit verify error: {data['error']}"
        return json.dumps(data, indent=2)

    @mcp.tool()
    def change_set_tool(
        repo: str,
        goal: str,
        symbol_id: str = "",
        diff: str = "",
        changed_files: list[str] | None = None,
        max_results: int = 50,
        include_details: bool = True,
    ) -> str:
        """Build a must-change set in remote mode. Pass diff for local uncommitted edits."""
        if not repo:
            return "repo is required"
        max_results = max(1, min(max_results, 500))
        data = _api_post(
            "/change-set",
            {
                "repo": repo,
                "goal": goal,
                "symbol_id": symbol_id,
                "diff": diff,
                "changed_files": changed_files or [],
                "max_results": max_results,
                "include_details": include_details,
            },
        )
        if data.get("error"):
            return f"Change set error: {data['error']}"
        return json.dumps(data, indent=2)

    @mcp.tool()
    def coverage_map_tool(repo: str, symbol_id: str = "", max_results: int = 100) -> str:
        """Map source symbols to likely covering tests in a registered repo."""
        if not repo:
            return "repo is required"
        max_results = max(1, min(max_results, 500))
        data = _api_post("/coverage-map", {"repo": repo, "symbol_id": symbol_id, "max_results": max_results})
        if data.get("error"):
            return f"Coverage map error: {data['error']}"
        return json.dumps(data, indent=2)

    @mcp.tool()
    def index_diff_report_tool(repo: str, before_nodes: list[dict] | None = None, after_nodes: list[dict] | None = None) -> str:
        """Summarize symbol, entry point, and call graph changes between two index snapshots."""
        if not repo:
            return "repo is required"
        data = _api_post("/index-diff-report", {"repo": repo, "before_nodes": before_nodes or [], "after_nodes": after_nodes or []})
        if data.get("error"):
            return f"Index diff report error: {data['error']}"
        return json.dumps(data, indent=2)

    @mcp.tool()
    def cross_repo_graph_tool(repos: list[str] | None = None, max_results: int = 200) -> str:
        """Build cross-repo dependency graph for registered repos."""
        max_results = max(1, min(max_results, 1000))
        data = _api_post("/cross-repo-graph", {"repos": repos or [], "max_results": max_results})
        if data.get("error"):
            return f"Cross-repo graph error: {data['error']}"
        return json.dumps(data, indent=2)

    @mcp.tool()
    def agent_capabilities_manifest_tool() -> str:
        """Return tool capability manifest and recommended Agent flow."""
        data = _api_get("/agent-capabilities")
        if data.get("error"):
            return f"Agent capabilities error: {data['error']}"
        return json.dumps(data, indent=2)

    @mcp.tool()
    def stable_symbol_id_tool(symbol_id: str, symbol_type: str = "", file_path: str = "", source: str = "") -> str:
        """Generate deterministic stable symbol id for rename/move tracking."""
        data = _api_post("/stable-symbol-id", {"symbol_id": symbol_id, "symbol_type": symbol_type, "file_path": file_path, "source": source})
        if data.get("error"):
            return f"Stable symbol id error: {data['error']}"
        return json.dumps(data, indent=2)

    @mcp.tool()
    def get_index_status_tool(repo: str | None = None) -> str:
        """Report whether registered repo indexes are stale relative to current workspace state."""
        body = {}
        if repo:
            body["repo"] = repo
        data = _api_post("/index-status", body)
        if data.get("error"):
            return f"Index status error: {data['error']}"
        return json.dumps(data, indent=2)

    _apply_mcp_auth(mcp, mcp_api_key)
    return mcp
