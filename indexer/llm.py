from __future__ import annotations
import json, os, time, logging
from indexer.ast_parser import ASTNode
from indexer.config import Config

logger = logging.getLogger(__name__)

_RETRY_ATTEMPTS = 3
_RETRY_BASE_DELAY = 2.0

_ANTHROPIC_MODELS = {"claude", "anthropic"}


def _is_anthropic(cfg: Config) -> bool:
    return any(cfg.provider.startswith(p) for p in _ANTHROPIC_MODELS)


def _resolve_api_key(cfg: Config) -> str | None:
    value = cfg.api_key_env
    if not value:
        for env_var in ("ANTHROPIC_API_KEY", "DASHSCOPE_API_KEY", "GROQ_API_KEY", "OPENAI_API_KEY", "GEMINI_API_KEY"):
            key = os.environ.get(env_var)
            if key:
                return key
        return None
    if " " not in value and not value.isupper() and not value.replace("_", "").isupper():
        return value
    return os.environ.get(value)


def _litellm_kwargs(cfg: Config, api_key: str | None) -> dict:
    kwargs = {
        "model": cfg.provider,
        "api_key": api_key,
    }
    if cfg.base_url:
        kwargs["api_base"] = cfg.base_url
    return kwargs


def _litellm_completion(cfg: Config, api_key: str | None, messages: list[dict], max_tokens: int = 1024) -> str:
    import litellm
    import random

    if not api_key:
        logger.warning("LLM call skipped: no API key configured (provider=%s, api_key_env=%s)", cfg.provider, cfg.api_key_env)
        return ""

    for attempt in range(_RETRY_ATTEMPTS):
        try:
            response = litellm.completion(
                **_litellm_kwargs(cfg, api_key),
                messages=messages,
                max_tokens=max_tokens,
            )
            return response.choices[0].message.content
        except Exception as e:
            is_rate_limit = isinstance(e, litellm.RateLimitError)
            is_fatal = isinstance(e, (TypeError, AttributeError, ImportError))
            last_attempt = attempt >= _RETRY_ATTEMPTS - 1
            if last_attempt or is_fatal:
                raise

            if is_rate_limit:
                delay = 5.0 * (5 ** attempt) + random.uniform(0, 2)
            else:
                delay = _RETRY_BASE_DELAY * (2 ** attempt) + random.uniform(0, 1)
            logger.warning("litellm call failed (attempt %d/%d), retrying in %.1fs: %s", attempt + 1, _RETRY_ATTEMPTS, delay, e)
            time.sleep(delay)


def _anthropic_completion(model: str, system: str, user: str, api_key: str) -> str:
    import anthropic
    import random

    bare_model = model.removeprefix("anthropic/")
    client = anthropic.Anthropic(api_key=api_key)

    for attempt in range(_RETRY_ATTEMPTS):
        try:
            response = client.messages.create(
                model=bare_model,
                max_tokens=1024,
                system=system,
                messages=[{"role": "user", "content": user}],
            )
            if not response.content:
                raise ValueError("Empty response from Anthropic")
            text_blocks = [b for b in response.content if getattr(b, "type", None) == "text"]
            if not text_blocks:
                raise ValueError("No text block in Anthropic response")
            return text_blocks[0].text
        except anthropic.RateLimitError as e:
            if attempt >= _RETRY_ATTEMPTS - 1:
                raise
            delay = 5.0 * (5 ** attempt) + random.uniform(0, 2)
            logger.warning("Anthropic API rate limited (attempt %d/%d), retrying in %.1fs: %s", attempt + 1, _RETRY_ATTEMPTS, delay, e)
            time.sleep(delay)
        except Exception as e:
            is_fatal = isinstance(e, (TypeError, AttributeError))
            if attempt >= _RETRY_ATTEMPTS - 1 or is_fatal:
                raise
            delay = _RETRY_BASE_DELAY * (2 ** attempt) + random.uniform(0, 1)
            logger.warning("Anthropic API call failed (attempt %d/%d), retrying in %.1fs: %s", attempt + 1, _RETRY_ATTEMPTS, delay, e)
            time.sleep(delay)


def _should_use_anthropic_sdk(cfg: Config, api_key: str | None) -> bool:
    return _is_anthropic(cfg) and api_key is not None


def _parse_llm_json(raw: str) -> dict | list | None:
    """Parse LLM response as JSON, with recovery for truncation and malformed output."""
    raw = raw.strip().removeprefix("```json").removeprefix("```").removesuffix("```").strip()
    try:
        return json.loads(raw)
    except json.JSONDecodeError:
        pass
    for marker in ("}", "]"):
        pos = len(raw)
        while pos > 0:
            pos = raw.rfind(marker, 0, pos)
            if pos < 0:
                break
            chunk = raw[:pos + 1].rstrip(",").rstrip(";")
            try:
                return json.loads(chunk)
            except (json.JSONDecodeError, ValueError):
                continue
    return None


def describe_nodes_batch(nodes: list[ASTNode], cfg: Config) -> dict[str, str]:
    api_key = _resolve_api_key(cfg)
    use_sdk = _should_use_anthropic_sdk(cfg, api_key)

    prompt_items = [
        {
            "id": n.id,
            "type": n.type,
            "docstring": n.docstring or "",
            "calls": n.calls[:15],
            "line_start": n.line_start,
            "line_end": n.line_end,
        }
        for n in nodes
    ]

    system = (
        "You are a code documentation assistant. "
        "Given a list of code symbols with their type, optional docstring, line range, and list of functions they call, "
        "return a JSON object mapping each symbol ID to a single short description (max 15 words, no period). "
        "Focus on WHAT it does and HOW (e.g. 'Validates Auth0 JWT tokens using JWKS public keys, returns UserClaims'). "
        "For classes, describe the role. For methods, describe the action and key side-effects. "
        "Be specific — avoid generic phrases like 'handles', 'manages', 'initializes'. "
        "Be factual and structural — no opinions, no guidance. "
        "Response must be valid JSON only, no markdown fences."
    )
    user = json.dumps(prompt_items)

    try:
        if use_sdk:
            raw = _anthropic_completion(cfg.provider, system, user, api_key)
        else:
            max_tokens = max(512, len(nodes) * 50)
            raw = _litellm_completion(cfg, api_key, [
                {"role": "system", "content": system},
                {"role": "user", "content": user},
            ], max_tokens=max_tokens)

        if not raw:
            return {n.id: "" for n in nodes}

        result = _parse_llm_json(raw)
        if result is None:
            logger.warning("LLM returned invalid JSON for batch of %d symbols (raw=%s...)", len(nodes), raw[:100])
            return {n.id: "" for n in nodes}

        if isinstance(result, list):
            result = {item["id"]: item.get("description", item.get("desc", "")) for item in result if isinstance(item, dict) and "id" in item}
        return {n.id: result.get(n.id, "") for n in nodes}
    except Exception as e:
        if isinstance(e, (TypeError, AttributeError, ImportError, NameError)):
            raise
        logger.warning("LLM description failed for batch of %d symbols: %s", len(nodes), e)
        return {n.id: "" for n in nodes}


def describe_nodes(batches: list[list[ASTNode]], cfg: Config, max_workers: int = 4) -> dict[str, str]:
    from concurrent.futures import ThreadPoolExecutor, as_completed

    descriptions: dict[str, str] = {}
    with ThreadPoolExecutor(max_workers=max_workers) as pool:
        futures = {pool.submit(describe_nodes_batch, batch, cfg): batch for batch in batches}
        for future in as_completed(futures):
            batch = futures[future]
            try:
                result = future.result()
                descriptions.update(result)
            except Exception as e:
                logger.warning("Batch description failed: %s", e)
                for n in batch:
                    descriptions[n.id] = ""

    return descriptions


def describe_files(file_nodes: dict[str, list[ASTNode]], cfg: Config) -> dict[str, str]:
    api_key = _resolve_api_key(cfg)
    use_sdk = _should_use_anthropic_sdk(cfg, api_key)

    prompt_items = [
        {
            "file": rel_path,
            "top_level_symbols": [
                {"name": n.id.split("::")[-1], "type": n.type, "docstring": n.docstring or ""}
                for n in nodes
                if n.type in ("class", "function")
            ][:12],
        }
        for rel_path, nodes in file_nodes.items()
    ]

    system = (
        "You are a code documentation assistant. "
        "Given a list of source files with their top-level classes and functions, "
        "return a JSON object mapping each file path to a single short description (max 12 words, no period). "
        "Describe the module's responsibility at a system level (e.g. 'Supabase-backed store for agent authentication sessions'). "
        "Be specific — use the symbol names as hints. "
        "Response must be valid JSON only, no markdown fences."
    )
    user = json.dumps(prompt_items)

    try:
        if use_sdk:
            raw = _anthropic_completion(cfg.provider, system, user, api_key)
        else:
            max_tokens = max(512, len(file_nodes) * 40)
            raw = _litellm_completion(cfg, api_key, [
                {"role": "system", "content": system},
                {"role": "user", "content": user},
            ], max_tokens=max_tokens)

        result = _parse_llm_json(raw)
        if result is None:
            logger.warning("LLM file description returned invalid JSON for %d files (raw=%s...)", len(file_nodes), raw[:100])
            return {f: "" for f in file_nodes}
        return {f: result.get(f, "") for f in file_nodes}
    except Exception as e:
        if isinstance(e, (TypeError, AttributeError, ImportError, NameError)):
            raise
        logger.warning("LLM file description failed: %s", e)
        return {f: "" for f in file_nodes}


def deep_enrich_page(
    group_label: str,
    files: list[str],
    nodes: list[ASTNode],
    descriptions: dict[str, str],
    cfg: Config,
) -> dict:
    api_key = _resolve_api_key(cfg)
    use_sdk = _should_use_anthropic_sdk(cfg, api_key)

    symbol_summary = [
        {"id": n.id, "type": n.type, "desc": descriptions.get(n.id, ""), "calls": n.calls[:8]}
        for n in nodes
        if n.type in ("class", "function") or not n.called_by
    ][:30]

    system = (
        "You are a senior engineer writing internal wiki documentation for an AI agent to navigate this codebase. "
        "Be specific, dense, and token-efficient — the reader is an LLM, not a human. "
        "Avoid padding, fluff, or generic statements. Every sentence must carry unique information."
    )
    user = json.dumps({
        "group": group_label,
        "files": files,
        "symbols": symbol_summary,
        "task": (
            "Return a JSON object with exactly three keys:\n"
            "1. 'narrative': A 3-5 sentence paragraph explaining WHY this module exists, "
            "what system-level problem it solves, and how it fits the broader architecture. "
            "Name the key classes and their roles. Be concrete.\n"
            "2. 'data_flows': A list of 2-4 short strings, each describing one end-to-end flow "
            "through this module (e.g. 'client calls X → Y validates → Z writes to DB'). "
            "Only include flows that go through THIS group's code.\n"
            "3. 'constraints': A list of 3-6 non-obvious design facts, edge cases, or invariants "
            "that an engineer MUST know to use this module correctly "
            "(e.g. '1-per-user limit enforced at creation', 'returns None not raises on miss'). "
            "Do NOT state things obvious from the symbol names."
        ),
    })

    empty = {"narrative": "", "data_flows": [], "constraints": []}

    try:
        if use_sdk:
            raw = _anthropic_completion(cfg.provider, system, user, api_key)
        else:
            raw = _litellm_completion(cfg, api_key, [
                {"role": "system", "content": system},
                {"role": "user", "content": user},
            ], max_tokens=2048)

        result = _parse_llm_json(raw)
        if result is None:
            logger.warning("LLM deep enrichment returned invalid JSON for %s", group_label)
            return empty
        return {
            "narrative": result.get("narrative", ""),
            "data_flows": result.get("data_flows", []),
            "constraints": result.get("constraints", []),
        }
    except Exception as e:
        if isinstance(e, (TypeError, AttributeError, ImportError, NameError)):
            raise
        logger.warning("LLM deep enrichment failed: %s", e)
        return empty


def deep_enrich_pages(pages_args: list[tuple], cfg: Config, max_workers: int = 3) -> dict[str, dict]:
    from concurrent.futures import ThreadPoolExecutor, as_completed

    page_enrichments: dict[str, dict] = {}
    with ThreadPoolExecutor(max_workers=max_workers) as pool:
        futures = {}
        for args in pages_args:
            group_label, files, nodes, descriptions = args
            futures[pool.submit(deep_enrich_page, group_label, files, nodes, descriptions, cfg)] = group_label
        for future in as_completed(futures):
            group_label = futures[future]
            try:
                page_enrichments[group_label] = future.result()
            except Exception:
                page_enrichments[group_label] = {"narrative": "", "data_flows": [], "constraints": []}

    return page_enrichments


def deep_enrich_index(
    pages: list[dict],
    cfg: Config,
) -> dict:
    api_key = _resolve_api_key(cfg)
    use_sdk = _should_use_anthropic_sdk(cfg, api_key)

    system = (
        "You are a senior engineer writing a codebase overview for an AI agent. "
        "Be dense and specific. No fluff."
    )
    user = json.dumps({
        "wiki_pages": pages,
        "task": (
            "Return a JSON object with two keys:\n"
            "1. 'overview': 3-4 sentences describing the overall system architecture — "
            "what it does, the main components, and how they connect. Name modules specifically.\n"
            "2. 'flows': A list of 3-5 strings, each a key cross-cutting request flow "
            "spanning multiple modules (e.g. 'Auth0 JWT → TokenValidator → require_auth0_user → route handler'). "
            "These should be the flows an agent most often needs to trace."
        ),
    })

    empty = {"overview": "", "flows": []}

    try:
        if use_sdk:
            raw = _anthropic_completion(cfg.provider, system, user, api_key)
        else:
            raw = _litellm_completion(cfg, api_key, [
                {"role": "system", "content": system},
                {"role": "user", "content": user},
            ])

        result = _parse_llm_json(raw)
        if result is None:
            logger.warning("LLM index enrichment returned invalid JSON (raw=%s...)", raw[:100])
            return empty
        return {
            "overview": result.get("overview", ""),
            "flows": result.get("flows", []),
        }
    except Exception as e:
        if isinstance(e, (TypeError, AttributeError, ImportError, NameError)):
            raise
        logger.warning("LLM index enrichment failed: %s", e)
        return empty


def rewrite_query(query: str, cfg: Config) -> list[str]:
    api_key = _resolve_api_key(cfg)
    if not api_key:
        return [query]

    system = (
        "You are a code search query rewriter. "
        "Given a user's natural language query about a codebase, produce 3-5 alternative search phrases "
        "that would match relevant code symbols, class names, function names, or module descriptions. "
        "Think about: what classes/functions would implement this? What technical terms would the code use? "
        "What related concepts might be relevant? "
        "Return a JSON array of strings only. No markdown fences. No explanation. "
        "Include the original query intent in at least one phrase. "
        "Each phrase should be 2-8 words, focused and specific."
    )
    user = json.dumps({"query": query})

    try:
        use_sdk = _should_use_anthropic_sdk(cfg, api_key)
        if use_sdk:
            raw = _anthropic_completion(cfg.provider, system, user, api_key)
        else:
            raw = _litellm_completion(cfg, api_key, [
                {"role": "system", "content": system},
                {"role": "user", "content": user},
            ], max_tokens=256)

        raw = raw.strip().removeprefix("```json").removeprefix("```").removesuffix("```").strip()
        result = json.loads(raw)
        if isinstance(result, list) and all(isinstance(s, str) for s in result):
            return [query] + [s for s in result if s != query]
        return [query]
    except Exception as e:
        logger.warning("Query rewrite failed: %s", e)
        return [query]


def synthesize_commit_message(changed_files: list[str], descriptions: dict[str, str], cfg: Config) -> str:
    api_key = _resolve_api_key(cfg)
    use_sdk = _should_use_anthropic_sdk(cfg, api_key)

    system = (
        "Write a single git commit message (max 72 chars) summarising the code changes. "
        "No conventional commit prefix. No markdown. Just the message text."
    )
    user = json.dumps({"changed_files": changed_files, "symbols": descriptions})

    try:
        if use_sdk:
            raw = _anthropic_completion(cfg.provider, system, user, api_key)
        else:
            raw = _litellm_completion(cfg, api_key, [
                {"role": "system", "content": system},
                {"role": "user", "content": user},
            ])

        return raw.strip()[:72]
    except Exception as e:
        if isinstance(e, (TypeError, AttributeError, ImportError, NameError)):
            raise
        logger.warning("LLM commit message synthesis failed: %s", e)
        return ""
