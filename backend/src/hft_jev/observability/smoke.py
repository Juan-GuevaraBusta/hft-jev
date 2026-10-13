"""End-to-end Langfuse tracing check: one synthetic research run through OpenRouter.

Run with `make trace-smoke`. Requires `.env` with Langfuse and OpenRouter keys.
The event below is synthetic demo data (ADR-001 §5): never put real or private data here.
"""

from __future__ import annotations

import os
import sys
import uuid

from dotenv import load_dotenv

# Must run before Langfuse is initialized so the client sees the credentials.
load_dotenv()

from langchain_core.messages import HumanMessage, SystemMessage  # noqa: E402
from langchain_openrouter import ChatOpenRouter  # noqa: E402

from hft_jev.observability import (  # noqa: E402
    init_langfuse,
    langchain_callbacks,
    research_trace,
)

DEFAULT_MODEL = "nvidia/nemotron-3-super-120b-a12b:free"
SYSTEM_PROMPT = (
    "You are an equity research analyst. Summarize the market event in two sentences "
    "and state the likely direction of impact (positive, negative or neutral)."
)
SYNTHETIC_EVENT = (
    "[SYNTHETIC] ACME Corp reports quarterly revenue 12% above consensus and raises "
    "full-year guidance; CFO announces a $2B share buyback."
)


def main() -> int:
    langfuse = init_langfuse()
    if not langfuse.auth_check():
        print("Langfuse auth failed: check LANGFUSE_* variables in .env", file=sys.stderr)
        return 1

    model = os.environ.get("OPENROUTER_MODEL", DEFAULT_MODEL)
    llm = ChatOpenRouter(model=model, temperature=0, max_tokens=400)
    research_id = f"smoke-{uuid.uuid4()}"

    with (
        research_trace(research_id, name="summarize-market-event", tags=["smoke"]),
        langfuse.start_as_current_observation(
            as_type="span", name="summarize-market-event"
        ) as root,
    ):
        root.update(input={"event": SYNTHETIC_EVENT})
        response = llm.invoke(
            [SystemMessage(SYSTEM_PROMPT), HumanMessage(SYNTHETIC_EVENT)],
            config={"callbacks": langchain_callbacks(), "run_name": "generate-summary"},
        )
        root.update(output={"summary": response.text})
        trace_id = langfuse.get_current_trace_id()

    langfuse.flush()
    print(f"research_id={research_id}")
    print(f"trace_url={langfuse.get_trace_url(trace_id=trace_id)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
