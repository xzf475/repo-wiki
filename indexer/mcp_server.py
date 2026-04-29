# indexer/mcp_server.py
from __future__ import annotations
import json
from pathlib import Path
from mcp.server.fastmcp import FastMCP
from indexer.config import load_config


def _apply_mcp_auth(mcp: FastMCP, mcp_api_key: str | None) -> None:
    _orig_method = mcp.streamable_http_app

    # Disable MCP's built-in TransportSecurityMiddleware which blocks external hosts
    mcp.settings.transport_security.enable_dns_rebinding_protection = False

    def _patched_method(_self=None):
        app = _orig_method()

        if mcp_api_key:
            from starlette.middleware.base import BaseHTTPMiddleware
            from starlette.responses import JSONResponse

            class _MCPAuthMiddleware(BaseHTTPMiddleware):
                async def dispatch(self, request, call_next):
                    auth = request.headers.get("Authorization", "")
                    token = auth.removeprefix("Bearer ")
                    if not token or token != mcp_api_key:
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
    def search_symbols_tool(query: str, top_k: int = 10, expand_depth: int = 1) -> str:
        """Search code symbols by semantic query. Returns matching symbols with descriptions,
        file locations, and optionally related symbols via call graph expansion.

        Use this when: analyzing a bug report, finding code related to an error message,
        locating where a feature is implemented, or understanding what a module does.

        Args:
            query: Natural language description of what you're looking for (e.g. "JWT token validation", "database connection pool")
            top_k: Number of top results to return (default 10)
            expand_depth: How many hops in the call graph to expand (0=no expansion, 1=direct callers/callees)
        """
        from indexer.retrieval import search_symbols
        hits = search_symbols(query, cfg, repo_root, top_k=top_k, expand_depth=expand_depth)
        if not hits:
            return "No matching symbols found. Try a different query or ensure the repo has been indexed with `repo-wiki run`."

        lines = []
        for h in hits:
            meta = h.get("metadata", {})
            dist = h.get("distance", 0.0)
            lines.append(
                f"**{h['id']}** (distance: {dist:.4f})\n"
                f"  Type: {meta.get('type', '?')} | File: {meta.get('file', '?')} | "
                f"Lines: {meta.get('line_start', '?')}-{meta.get('line_end', '?')}\n"
                f"  {h.get('document', '')}"
            )
        return "\n\n".join(lines)

    @mcp.tool()
    def trace_call_tool(symbol_id: str, direction: str = "down", max_depth: int = 3) -> str:
        """Trace the call graph from a symbol. Follows calls (down) or callers (up) up to max_depth hops.

        Use this when: understanding how a bug propagates through the codebase, tracing an end-to-end
        request flow, finding all callers of a function that needs to be modified, or identifying
        the root cause of an error by tracing upstream.

        Args:
            symbol_id: Component ID in format "path/to/file.py::ClassName.method" or "path/to/file.py::function_name"
            direction: "down" (follow calls this symbol makes) or "up" (follow callers of this symbol)
            max_depth: Maximum hops in the call graph (default 3)
        """
        from indexer.retrieval import trace_call
        nodes = trace_call(symbol_id, cfg, repo_root, direction=direction, max_depth=max_depth)
        if not nodes:
            return f"Symbol '{symbol_id}' not found in vector store. Ensure the repo has been indexed."

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
        from indexer.retrieval import get_source_context
        return get_source_context(file_path, line_start, line_end, repo_root, padding=padding)

    _apply_mcp_auth(mcp, mcp_api_key)
    return mcp


def create_api_server(api_url: str, api_key: str | None = None, mcp_api_key: str | None = None) -> FastMCP:
    import urllib.request
    import urllib.error

    mcp = FastMCP("repo-wiki-rag")

    def _api_get(path: str) -> dict:
        url = f"{api_url.rstrip('/')}{path}"
        headers = {"Accept": "application/json"}
        if api_key:
            headers["Authorization"] = f"Bearer {api_key}"
        req = urllib.request.Request(url, headers=headers)
        try:
            with urllib.request.urlopen(req, timeout=30) as resp:
                return json.loads(resp.read())
        except urllib.error.HTTPError as e:
            return {"error": f"HTTP {e.code}: {e.reason}"}
        except urllib.error.URLError as e:
            return {"error": f"Connection error: {e.reason}"}

    def _api_post(path: str, body: dict | None = None) -> dict:
        url = f"{api_url.rstrip('/')}{path}"
        data = json.dumps(body or {}).encode()
        headers = {"Content-Type": "application/json", "Accept": "application/json"}
        if api_key:
            headers["Authorization"] = f"Bearer {api_key}"
        req = urllib.request.Request(url, data=data, headers=headers)
        try:
            with urllib.request.urlopen(req, timeout=60) as resp:
                return json.loads(resp.read())
        except urllib.error.HTTPError as e:
            return {"error": f"HTTP {e.code}: {e.reason}"}
        except urllib.error.URLError as e:
            return {"error": f"Connection error: {e.reason}"}

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
            commit_tag = f" @{r.get('last_indexed_commit', '')}" if r.get('last_indexed_commit') else ""
            desc = r.get("description", "")
            tags = r.get("tags", [])
            desc_tag = f" — {desc}" if desc else ""
            tags_tag = f"  `{' '.join(f'#{t}' for t in tags)}`" if tags else ""
            lines.append(
                f"- **{r['name']}**{commit_tag}{desc_tag}{tags_tag}\n"
                f"  {r.get('symbol_count', '?')} symbols"
                f"{', has vector DB' if r.get('has_vector_db') else ', no vector DB'}"
            )
        return "\n".join(lines)

    @mcp.tool()
    def search_symbols_tool(query: str, repo: str | None = None, top_k: int = 10, expand_depth: int = 1, rewrite: bool = True) -> str:
        """Search code symbols by semantic query across one or all registered repos.
        Returns matching symbols with descriptions, file locations, and related symbols.

        Use this when: analyzing a bug report, finding code related to an error message,
        locating where a feature is implemented, or understanding what a module does.

        Args:
            query: Natural language description of what you're looking for (e.g. "JWT token validation", "database connection pool")
            repo: Repository name to search in. If omitted, searches across all repos.
            top_k: Number of top results to return (default 10)
            expand_depth: How many hops in the call graph to expand (0=no expansion, 1=direct callers/callees)
            rewrite: Whether to use LLM query rewriting for better recall (default true)
        """
        body = {
            "query": query,
            "top_k": top_k,
            "expand_depth": expand_depth,
            "rewrite": rewrite,
        }
        if repo:
            body["repo"] = repo

        data = _api_post("/search", body)

        if data.get("error"):
            return f"Search error: {data['error']}"

        hits = data.get("results", [])
        if not hits:
            return "No matching symbols found. Try a different query or ensure repos have been indexed."

        rewritten = data.get("rewritten_queries")
        header = f"**Search results** ({data.get('total', len(hits))} hits)"
        if rewritten:
            header += f"\nExpanded queries: {', '.join(rewritten)}"
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
        """Trace the call graph from a symbol. Follows calls (down) or callers (up) up to max_depth hops.

        Use this when: understanding how a bug propagates through the codebase, tracing an end-to-end
        request flow, finding all callers of a function that needs to be modified.

        Args:
            symbol_id: Component ID in format "path/to/file.py::ClassName.method" or "path/to/file.py::function_name"
            repo: Repository name the symbol belongs to
            direction: "down" (follow calls this symbol makes) or "up" (follow callers of this symbol)
            max_depth: Maximum hops in the call graph (default 3)
        """
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

    _apply_mcp_auth(mcp, mcp_api_key)
    return mcp
