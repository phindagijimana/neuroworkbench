"""Optional stdio MCP transport. Calls neuroworkbench.submit only.

Not an agent. No execute tool. No model API.
"""

from __future__ import annotations

from neuroworkbench import __version__
from neuroworkbench.agent import TOOLS, call_tool
from neuroworkbench.mcp_stdio import handle_message as _handle
from neuroworkbench.mcp_stdio import serve

SERVER = "neuroworkbench"


def handle_message(message: dict) -> dict | None:
    return _handle(
        message,
        name=SERVER,
        version=__version__,
        tools=TOOLS,
        call_tool=call_tool,
    )


def main() -> None:
    serve(name=SERVER, version=__version__, tools=TOOLS, call_tool=call_tool)


if __name__ == "__main__":
    main()
