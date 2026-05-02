# IAU Proposal Writer MCP

دستیار هوشمند نوشتن پروپوزال — دانشگاه آزاد اسلامی واحد اصفهان (خوراسگان)  
گروه کامپیوتر | کارشناسی ارشد و دکتری

An MCP server that helps graduate students at IAU Isfahan (Khorasgan) write, review, and validate academic research proposals for the Computer Department.

---

## Features

| Tool | Description |
|------|-------------|
| `get_section_rules` | Full rules for any proposal section (4–14) |
| `list_available_sections` | List all sections with descriptions |
| `validate_section` | Score a section 0–100 and list issues |
| `get_common_mistakes` | 21 common reviewer rejections |
| `get_endnote_guide` | EndNote setup with IAU-KHUISF styles |
| `create_proposal` | Create a blank proposal file from template |
| `save_section` | Append a written section to the proposal file |
| `read_proposal` | Read an existing proposal file |
| `list_proposals` | List all proposal `.md` files in a folder |
| `search_papers` | Search Semantic Scholar + arXiv for related papers |
| `build_comparison_table` | Auto-generate Section 4-5 comparison table skeleton |

**Prompts:** `draft_section` · `review_proposal`  
**Resources:** `proposal://rules/{section}` · `proposal://mistakes` · `proposal://template` · `proposal://endnote`

---

## Installation

### macOS / Linux

```bash
# 1. Install via pip (Python 3.11+)
pip install git+https://github.com/mjavadalavi/iau-proposal-mcp.git

# Or clone and install locally
git clone https://github.com/mjavadalavi/iau-proposal-mcp.git
cd iau-proposal-mcp
pip install -e .
```

### Windows

```bat
:: 1. Install via pip (Python 3.11+ required)
pip install git+https://github.com/mjavadalavi/iau-proposal-mcp.git

:: Or clone and install locally
git clone https://github.com/mjavadalavi/iau-proposal-mcp.git
cd iau-proposal-mcp
pip install -e .
```

---

## Add to Claude Desktop

### macOS — one-liner setup

```bash
python3 - <<'EOF'
import json, shutil, pathlib

config_path = pathlib.Path.home() / "Library/Application Support/Claude/claude_desktop_config.json"
config_path.parent.mkdir(parents=True, exist_ok=True)

config = json.loads(config_path.read_text()) if config_path.exists() else {}
config.setdefault("mcpServers", {})["proposal-writer-iau"] = {
    "command": shutil.which("proposal-writer-iau-mcp") or "proposal-writer-iau-mcp"
}

config_path.write_text(json.dumps(config, indent=2, ensure_ascii=False))
print("✅ Added to", config_path)
EOF
```

### Windows — one-liner setup

```bat
python -c "
import json, shutil, pathlib, os
config_path = pathlib.Path(os.environ['APPDATA']) / 'Claude' / 'claude_desktop_config.json'
config_path.parent.mkdir(parents=True, exist_ok=True)
config = json.loads(config_path.read_text('utf-8')) if config_path.exists() else {}
config.setdefault('mcpServers', {})['proposal-writer-iau'] = {'command': shutil.which('proposal-writer-iau-mcp') or 'proposal-writer-iau-mcp'}
config_path.write_text(json.dumps(config, indent=2, ensure_ascii=False), 'utf-8')
print('Done:', config_path)
"
```

### Manual config

Add this to `claude_desktop_config.json` (macOS: `~/Library/Application Support/Claude/`, Windows: `%APPDATA%\Claude\`):

```json
{
  "mcpServers": {
    "proposal-writer-iau": {
      "command": "proposal-writer-iau-mcp"
    }
  }
}
```

Then **restart Claude Desktop**.

---

## Add to Claude Code (CLI)

```bash
# Add to the current project
claude mcp add proposal-writer-iau -- proposal-writer-iau-mcp

# Add globally (available in all projects)
claude mcp add --scope global proposal-writer-iau -- proposal-writer-iau-mcp

# Verify it was added
claude mcp list
```

---

## Add to Codex (OpenAI CLI)

```bash
# Add to ~/.codex/config.toml
python3 - <<'EOF'
import pathlib

config_path = pathlib.Path.home() / ".codex" / "config.toml"
config_path.parent.mkdir(parents=True, exist_ok=True)

entry = """
[[mcp_servers]]
name = "proposal-writer-iau"
command = "proposal-writer-iau-mcp"
"""

existing = config_path.read_text() if config_path.exists() else ""
if "proposal-writer-iau" not in existing:
    config_path.write_text(existing + entry)
    print("✅ Added to", config_path)
else:
    print("Already present in", config_path)
EOF
```

---

## Verify Installation

```bash
# Check the binary is accessible
proposal-writer-iau-mcp --help 2>&1 || echo "binary found at: $(which proposal-writer-iau-mcp)"

# Quick smoke test — list available sections
echo '{"jsonrpc":"2.0","id":1,"method":"tools/call","params":{"name":"list_available_sections","arguments":{}}}' \
  | proposal-writer-iau-mcp
```

---

## Proposal Sections Covered

| # | Section | زیربخش‌ها |
|---|---------|----------|
| 4 | بیان مسأله | 4-1 تا 4-5 (پیشینه تحقیق) |
| 5 | اهمیت موضوع و ضرورت انجام | — |
| 6 | جنبه جدید بودن و نوآوری | — |
| 7 | اهداف تحقیق | هدف اصلی + فرعی |
| 8 | بیان نام بهره‌وران | — |
| 9 | سؤالات تحقیق | اصلی + فرعی |
| 10 | فرضیه‌های تحقیق | قالب اگر…آنگاه |
| 11 | محدودیت‌ها و پیش‌فرض‌ها | — |
| 12 | تعریف واژه‌ها | جدول اصطلاحات |
| 13 | روش‌شناسی | 13-الف تا 13-و |
| 14 | فهرست منابع | EndNote IAU-KHUISF |

---

## Requirements

- Python 3.11+
- `mcp >= 1.0.0`
- `httpx >= 0.27.0` (for paper search)

---

## License

MIT
