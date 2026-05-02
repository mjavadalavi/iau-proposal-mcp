"""MCP tool registrations for the proposal writer server."""
from __future__ import annotations

import json
from datetime import datetime
from pathlib import Path

from mcp.server.fastmcp import FastMCP
from pypdf import PdfReader

from proposal_writer_iau_mcp import loader, papers, validator


def _read_pdf(path: Path) -> str:
    reader = PdfReader(str(path))
    pages = [page.extract_text() or "" for page in reader.pages]
    return "\n\n".join(pages)


def register(mcp: FastMCP) -> None:  # noqa: C901
    """Register all tools onto *mcp*."""

    @mcp.tool()
    def get_section_rules(section: str) -> str:
        """دریافت قوانین کامل یک بخش از پروپوزال.

        Args:
            section: شماره بخش — مثال: 'overview', '4', '4-5', '5', '13'
        """
        return loader.load_rule(section)

    @mcp.tool()
    def list_available_sections() -> str:
        """لیست تمام بخش‌هایی که قوانین آن‌ها در پایگاه داده موجود است."""
        sections = loader.list_sections()
        lines = ["بخش‌های موجود:"]
        descriptions = {
            "overview": "ساختار کلی و قوانین نگارش",
            "4": "بیان مسأله اساسی تحقیق (5 زیربخش)",
            "5": "اهمیت موضوع و ضرورت انجام",
            "6": "جنبه جدید بودن و نوآوری",
            "7": "اهداف تحقیق",
            "8": "بیان نام بهره‌وران",
            "9": "سؤالات تحقیق",
            "10": "فرضیه‌های تحقیق",
            "11": "محدودیت‌ها و پیش‌فرض‌ها",
            "12": "تعریف واژه‌ها و اصطلاحات فنی",
            "13": "روش کار و روش‌شناسی (6 زیربخش)",
            "14": "فهرست منابع و EndNote",
        }
        for s in sections:
            desc = descriptions.get(s, "")
            lines.append(f"  • {s}: {desc}")
        return "\n".join(lines)

    @mcp.tool()
    def validate_section(section_number: str, content: str) -> str:
        """بررسی ساختاری یک بخش از پروپوزال بر اساس قوانین دانشگاه.

        Args:
            section_number: شماره بخش — مثال: '4', '4-5', '7', '10', '13'
            content: متن کامل بخش به فارسی
        """
        report = validator.validate(section_number, content)
        result: dict = {
            "section": section_number,
            "score": report.score,
            "issues": report.issues,
            "suggestions": report.suggestions,
            "status": "✅ قبول" if report.score >= 70 else "⚠️ نیاز به اصلاح",
        }
        return json.dumps(result, ensure_ascii=False, indent=2)

    @mcp.tool()
    def get_common_mistakes() -> str:
        """دریافت لیست ۲۱ ایراد معمول داوران گروه کامپیوتر دانشگاه آزاد خوراسگان."""
        return loader.load_data("mistakes.md")

    @mcp.tool()
    def get_endnote_guide() -> str:
        """راهنمای استفاده از EndNote با استایل IAU-KHUISF."""
        return loader.load_data("endnote.md")

    @mcp.tool()
    def create_proposal(directory: str, student_name: str, research_title: str = "") -> str:
        """ایجاد فایل پروپوزال خالی بر اساس قالب دانشگاه.

        Args:
            directory: مسیر پوشه‌ای که فایل در آن ایجاد شود
            student_name: نام خانوادگی دانشجو (برای نام‌گذاری فایل)
            research_title: عنوان پایان‌نامه (اختیاری)
        """
        folder = Path(directory).expanduser()
        folder.mkdir(parents=True, exist_ok=True)

        date_str = datetime.now().strftime("%Y-%m-%d")
        safe_name = student_name.replace(" ", "-")
        filename = f"{safe_name}-PROPOSAL-{date_str}.md"
        filepath = folder / filename

        template = loader.load_data("template.md")
        if research_title:
            template = template.replace("**عنوان پایان‌نامه (فارسی):** ...", f"**عنوان پایان‌نامه (فارسی):** {research_title}")

        filepath.write_text(template, encoding="utf-8")
        return f"✅ فایل پروپوزال ایجاد شد: {filepath}"

    @mcp.tool()
    def save_section(file_path: str, section_number: str, section_title: str, content: str) -> str:
        """ذخیره یک بخش از پروپوزال در فایل markdown.

        Args:
            file_path: مسیر کامل فایل پروپوزال (.md)
            section_number: شماره بخش — مثال: '4', '4-1', '13-الف'
            section_title: عنوان بخش به فارسی
            content: محتوای بخش در قالب markdown
        """
        path = Path(file_path).expanduser()
        if not path.exists():
            path.parent.mkdir(parents=True, exist_ok=True)
            header = (
                "# پروپوزال پایان‌نامه\n\n"
                "**دانشگاه آزاد اسلامی واحد اصفهان (خوراسگان)**  \n"
                "**دانشکده فنی و مهندسی — گروه کامپیوتر**\n\n"
                f"*ایجاد شده: {datetime.now().strftime('%Y-%m-%d %H:%M')}*\n\n---\n"
            )
            path.write_text(header, encoding="utf-8")

        block = f"\n\n## بخش {section_number}: {section_title}\n\n{content}\n"
        with path.open("a", encoding="utf-8") as f:
            f.write(block)

        return f"✅ بخش {section_number} ({section_title}) در '{path.name}' ذخیره شد."

    @mcp.tool()
    def read_proposal(file_path: str) -> str:
        """خواندن محتوای فایل پروپوزال — پشتیبانی از PDF و markdown/txt.

        Args:
            file_path: مسیر کامل فایل پروپوزال (.md / .txt / .pdf)
        """
        path = Path(file_path).expanduser()
        if not path.exists():
            return f"❌ فایل '{file_path}' یافت نشد."
        if path.suffix.lower() == ".pdf":
            return _read_pdf(path)
        return path.read_text(encoding="utf-8")

    @mcp.tool()
    def read_pdf(file_path: str, pages: str = "") -> str:
        """استخراج متن از فایل PDF — مقاله، کتاب، یا پروپوزال اسکن‌شده.

        Args:
            file_path: مسیر کامل فایل PDF
            pages: بازه صفحات — مثال: '1-5' یا '3' (خالی = همه صفحات)
        """
        path = Path(file_path).expanduser()
        if not path.exists():
            return f"❌ فایل '{file_path}' یافت نشد."
        if path.suffix.lower() != ".pdf":
            return f"❌ فایل باید PDF باشد (پسوند: {path.suffix})"

        reader = PdfReader(str(path))
        total = len(reader.pages)

        if pages:
            try:
                if "-" in pages:
                    start, end = pages.split("-", 1)
                    indices = range(int(start) - 1, min(int(end), total))
                else:
                    indices = range(int(pages) - 1, int(pages))
            except ValueError:
                return "❌ فرمت صفحات اشتباه است — مثال: '1-5' یا '3'"
        else:
            indices = range(total)

        extracted = []
        for i in indices:
            text = reader.pages[i].extract_text() or ""
            extracted.append(f"── صفحه {i + 1} ──\n{text}")

        header = f"📄 {path.name}  |  {total} صفحه\n\n"
        return header + "\n\n".join(extracted)

    @mcp.tool()
    def search_papers(
        topic: str,
        keywords: str = "",
        year_from: int = 2019,
        limit: int = 10,
        source: str = "both",
    ) -> str:
        """جستجوی مقالات علمی معتبر از Semantic Scholar و arXiv.

        Args:
            topic: موضوع اصلی تحقیق — مثال: 'federated learning intrusion detection'
            keywords: کلیدواژه‌های اضافی جداشده با فاصله
            year_from: از چه سالی به بعد — پیش‌فرض ۲۰۱۹
            limit: تعداد مقاله برای هر منبع — پیش‌فرض ۱۰
            source: منبع جستجو — 'semantic_scholar' | 'arxiv' | 'both'
        """
        query = f"{topic} {keywords}".strip()
        results: list[papers.Paper] = []
        errors: list[str] = []

        if source in ("semantic_scholar", "both"):
            try:
                results += papers.search_semantic_scholar(query, year_from, limit)
            except Exception as exc:
                errors.append(f"Semantic Scholar: {exc}")

        if source in ("arxiv", "both"):
            try:
                results += papers.search_arxiv(query, year_from, limit)
            except Exception as exc:
                errors.append(f"arXiv: {exc}")

        if not results and errors:
            return "❌ خطا در جستجو:\n" + "\n".join(errors)

        output: list[dict] = [
            {
                "عنوان": p.title,
                "نویسندگان": ", ".join(p.authors) + (" و دیگران" if len(p.authors) == 3 else ""),
                "سال": p.year,
                "خلاصه": p.abstract,
                "لینک": p.url,
                "PDF رایگان": p.open_access_pdf or "ندارد",
                "منبع": p.source,
            }
            for p in results
        ]
        return json.dumps(output, ensure_ascii=False, indent=2)

    @mcp.tool()
    def build_comparison_table(
        topic: str,
        keywords: str = "",
        year_from: int = 2019,
        limit: int = 8,
    ) -> str:
        """ساخت جدول مقایسه کارهای پیشین آماده برای بخش 4-5 پروپوزال.

        مقالات را از Semantic Scholar و arXiv جستجو می‌کند و
        یک جدول markdown با ستون‌های استاندارد IAU برمی‌گرداند.

        Args:
            topic: موضوع اصلی تحقیق به انگلیسی
            keywords: کلیدواژه‌های اضافی
            year_from: از چه سالی — پیش‌فرض ۲۰۱۹
            limit: تعداد مقاله — پیش‌فرض ۸
        """
        query = f"{topic} {keywords}".strip()
        found: list[papers.Paper] = []

        try:
            found += papers.search_semantic_scholar(query, year_from, limit // 2 + 1)
        except Exception:
            pass

        try:
            found += papers.search_arxiv(query, year_from, limit // 2 + 1)
        except Exception:
            pass

        if not found:
            return "❌ هیچ مقاله‌ای یافت نشد. کلیدواژه‌ها را تغییر دهید."

        seen: set[str] = set()
        unique: list[papers.Paper] = []
        for p in found:
            key = p.title.lower()[:60]
            if key not in seen:
                seen.add(key)
                unique.append(p)

        unique = unique[:limit]

        lines = [
            "## جدول مقایسه کارهای پیشین (بخش 4-5)\n",
            "| مرجع | رویکرد/روش | مزایا | معایب/محدودیت |",
            "|------|-----------|-------|--------------|",
        ]
        for i, p in enumerate(unique, 1):
            authors_short = p.authors[0].split()[-1] if p.authors else "نامشخص"
            year_str = str(p.year) if p.year else "؟"
            ref = f"[{i}] {authors_short} ({year_str})"
            approach = (p.title[:60] + "...") if len(p.title) > 60 else p.title
            lines.append(f"| {ref} | {approach} | — | — |")

        lines += [
            "",
            "> **⚠️ یادداشت:** ستون‌های «مزایا» و «معایب» را با خواندن مقاله پر کنید.",
            "",
            "### منابع",
        ]
        for i, p in enumerate(unique, 1):
            lines.append(f"[{i}] {', '.join(p.authors) or 'نامشخص'} ({p.year or '؟'}). {p.title}. {p.url}")

        return "\n".join(lines)

    @mcp.tool()
    def list_proposals(directory: str) -> str:
        """لیست فایل‌های پروپوزال (*.md) در یک پوشه.

        Args:
            directory: مسیر پوشه
        """
        folder = Path(directory).expanduser()
        if not folder.exists():
            return f"❌ پوشه '{directory}' وجود ندارد."

        files = sorted(folder.glob("*.md"))
        if not files:
            return "هیچ فایل پروپوزال (.md) در این پوشه یافت نشد."

        lines = [f"فایل‌های پروپوزال در '{folder}':"]
        for f in files:
            size_kb = f.stat().st_size // 1024
            lines.append(f"  • {f.name} ({size_kb} KB)")
        return "\n".join(lines)
