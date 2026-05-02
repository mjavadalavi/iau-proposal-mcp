#!/usr/bin/env python3
"""
IAU Isfahan (Khorasgan) Academic Proposal Writer — MCP Server
دستیار هوشمند نوشتن پروپوزال — دانشگاه آزاد اسلامی واحد اصفهان (خوراسگان)
گروه کامپیوتر — کارشناسی ارشد و دکتری
"""
from __future__ import annotations

import logging
import sys

from mcp.server.fastmcp import FastMCP

from proposal_writer_iau_mcp import resources, tools

logging.basicConfig(level=logging.INFO, stream=sys.stderr)

mcp = FastMCP(name="proposal-writer-iau")

tools.register(mcp)
resources.register(mcp)


def main() -> None:
    mcp.run(transport="stdio")


if __name__ == "__main__":
    main()
