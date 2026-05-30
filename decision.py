"""Decision: next_step returns DecisionOutput (answer OR tool_call).

All LLM calls go through LLM gateway V7. No direct provider SDK imports.

The Decision module receives the current goal, memory hits, optional artifact
bytes attached by Perception, and the run history. It picks exactly one of:
  - a tool_call to advance toward the goal
  - an answer (final or synthesis)

Tool selection is guided by the dynamic MCP tool list from agent7.py plus
hardcoded hints so the model uses search_knowledge for indexed corpora and
fetch_urls for batched web fetches.
"""

from __future__ import annotations

import json
from typing import Any

from gateway import LLM, ensure_gateway
from memory import _format_hits
from schemas import DecisionLLMFlat, DecisionOutput, Goal, MemoryItem, ToolCall

_MAX_ATTACHED_BYTES = 12_000
_MAX_HIST_CHARS = 12_000
_MAX_HITS_CHARS = 16_000

SYSTEM = (
    "You are the Decision module of a cognitive agent.\n"
    "Given the current goal, memory hits, run history, and optionally attached "
    "artifact bytes, decide on ONE action: call a tool or emit a final answer.\n\n"
    "Return JSON matching the schema with fields: reasoning, branch, tool_name, "
    "tool_arguments_json, answer_text.\n\n"
    "CORE RULES:\n"
    "1. Memory-first: if memory hits or attached bytes already answer the goal, "
    "return branch='answer' immediately.\n"
    "2. Indexed corpus: when memory descriptors start with [sandbox:corpus/...], "
    "call search_knowledge — do NOT re-index or re-fetch.\n"
    "3. Corpus not indexed: call index_directory('corpus/aws') first, then search_knowledge.\n"
    "4. After search_knowledge returns chunks, synthesize an answer — do not search again.\n"
    "5. Web research: web_search → fetch_urls (batch ≤3 URLs) → answer.\n"
    "6. Never pass artifact handles (starting 'art:') as url/path arguments.\n"
    "7. tool_arguments_json must be valid JSON. web_search requires non-empty 'query'.\n"
    "8. Reasoning prefix: [TOOL_SELECTION], [FINAL_ANSWER_SYNTHESIS], or [INVESTIGATIVE_SEARCH]."
)


def _build_tool_catalog(tools: list[dict]) -> str:
    lines = ["AVAILABLE MCP TOOLS (pick exactly one per turn):"]
    for t in tools:
        name = t.get("name", "")
        desc = (t.get("description") or "")[:160]
        props = t.get("input_schema", {}).get("properties", {})
        params = ", ".join(
            f"{k}: {v.get('type', 'any')}" for k, v in props.items()
        )
        lines.append(f"  {name}({params}): {desc}")
    lines.append("")
    lines.append("TOOL SELECTION HINTS:")
    lines.append(
        "  - search_knowledge: use when memory hits show '[sandbox:corpus/...]' descriptors "
        "(corpus already indexed). Returns full chunk text."
    )
    lines.append(
        "  - index_directory: bulk-index a corpus directory before searching. "
        "Use 'corpus/aws' for the AWS markdown corpus."
    )
    lines.append(
        "  - fetch_urls: batch-fetch up to 3 URLs in one call. Prefer over multiple fetch_url."
    )
    lines.append(
        "  - web_search: live web search. Always include a non-empty 'query' argument."
    )
    return "\n".join(lines)


def next_step(
    goal: Goal,
    hits: list[MemoryItem],
    attached: list[tuple[str, bytes]],
    history: list[dict],
    tools_for_decision: list[dict],
    *,
    user_query: str = "",
    iteration_cap: int = 20,
) -> DecisionOutput:
    ensure_gateway()

    hits_txt = _format_hits(hits, max_hits=24, max_chars=_MAX_HITS_CHARS)
    hist_txt = json.dumps(history[-16:], indent=2, default=str)[:_MAX_HIST_CHARS]
    tool_catalog = _build_tool_catalog(tools_for_decision)

    attached_sections: list[str] = []
    for aid, blob in attached:
        try:
            txt = blob.decode("utf-8", errors="replace")
        except Exception:
            txt = repr(blob[:500])
        attached_sections.append(
            f"==== ATTACHED {aid} ({len(blob)} bytes) ====\n{txt[:_MAX_ATTACHED_BYTES]}"
        )
    attached_block = "\n\n".join(attached_sections) if attached_sections else "None"

    prompt = f"""USER QUERY: {user_query or goal.text}

CURRENT GOAL: id={goal.id!r} text={goal.text!r}

MEMORY HITS (descriptor + content; '[sandbox:corpus/...]' means already indexed):
{hits_txt}

RECENT HISTORY (last 16 events):
{hist_txt}

ATTACHED ARTIFACT BYTES (decoded UTF-8):
{attached_block}

{tool_catalog}

RESPONSE FORMAT — choose exactly one branch:

Tool call:
{{"reasoning": "[TOOL_SELECTION] ...", "branch": "tool", "tool_name": "search_knowledge", "tool_arguments_json": "{{\\"query\\":\\"...\\"}}",  "answer_text": null}}

Final answer:
{{"reasoning": "[FINAL_ANSWER_SYNTHESIS] ...", "branch": "answer", "answer_text": "...", "tool_name": null, "tool_arguments_json": "{{}}"}}

Iteration budget: {iteration_cap} max. Simple lookups: 1-2 turns. Multi-hop web: up to 4 turns.
Do not repeat tool calls that history already shows succeeded with identical arguments.
"""

    schema = DecisionLLMFlat.model_json_schema()
    try:
        reply = LLM().chat(
            prompt=prompt,
            system=SYSTEM,
            auto_route="decision",
            response_format={
                "type": "json_schema",
                "schema": schema,
                "name": "DecisionOutput",
                "strict": True,
            },
            temperature=0.2,
            max_tokens=2048,
        )

        parsed = reply.get("parsed") or {}
        if not parsed:
            raw_text = reply.get("text", "")
            try:
                parsed = json.loads(raw_text)
            except Exception:
                pass

        flat = DecisionLLMFlat.model_validate(parsed)

        if flat.branch == "tool" and flat.tool_name:
            raw_args = (flat.tool_arguments_json or "").strip() or "{}"
            try:
                args: dict[str, Any] = json.loads(raw_args)
                if not isinstance(args, dict):
                    args = {}
            except json.JSONDecodeError:
                args = {}
            # Safety: web_search must have a non-empty query
            if flat.tool_name in {"web_search"} and not str(args.get("query", "")).strip():
                args["query"] = goal.text
            tc = ToolCall(name=flat.tool_name.strip(), arguments=args)
            return DecisionOutput(answer=None, tool_call=tc)

        answer_text = (flat.answer_text or "").strip() or "(no answer produced)"
        return DecisionOutput(answer=answer_text, tool_call=None)

    except Exception as e:
        print(f"[decision] LLM call failed: {e!r}")
        return DecisionOutput(answer=None, tool_call=None)
