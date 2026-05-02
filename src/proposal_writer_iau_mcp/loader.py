"""Load static data files bundled with the package."""
from __future__ import annotations

from importlib.resources import files


def _pkg() -> object:
    return files("proposal_writer_iau_mcp")


def load_rule(section: str) -> str:
    """Return the rule markdown for *section* (e.g. '4', '4-5', '13', 'overview')."""
    resource = _pkg() / "data" / "rules" / f"{section}.md"
    try:
        return resource.read_text(encoding="utf-8")
    except (FileNotFoundError, TypeError):
        return f"قوانین بخش «{section}» در پایگاه داده یافت نشد.\nبخش‌های موجود: overview, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14"


def load_data(filename: str) -> str:
    """Return a file from the data/ directory (e.g. 'mistakes.md')."""
    resource = _pkg() / "data" / filename
    try:
        return resource.read_text(encoding="utf-8")
    except (FileNotFoundError, TypeError) as exc:
        raise FileNotFoundError(f"فایل داده '{filename}' یافت نشد.") from exc


def list_sections() -> list[str]:
    """Return available section IDs."""
    return ["overview", "4", "5", "6", "7", "8", "9", "10", "11", "12", "13", "14"]
