"""MCP resource and prompt registrations."""
from __future__ import annotations

from mcp.server.fastmcp import FastMCP

from proposal_writer_iau_mcp import loader


def register(mcp: FastMCP) -> None:
    """Register all resources and prompts onto *mcp*."""

    # ─── Resources ────────────────────────────────────────────────────────────

    @mcp.resource("proposal://rules/overview")
    def resource_overview() -> str:
        """ساختار کلی و قوانین نگارش پروپوزال."""
        return loader.load_rule("overview")

    @mcp.resource("proposal://rules/{section}")
    def resource_section_rules(section: str) -> str:
        """قوانین یک بخش خاص از پروپوزال."""
        return loader.load_rule(section)

    @mcp.resource("proposal://mistakes")
    def resource_mistakes() -> str:
        """۲۱ ایراد معمول داوران گروه کامپیوتر."""
        return loader.load_data("mistakes.md")

    @mcp.resource("proposal://template")
    def resource_template() -> str:
        """قالب خالی پروپوزال آماده پر کردن."""
        return loader.load_data("template.md")

    @mcp.resource("proposal://endnote")
    def resource_endnote() -> str:
        """راهنمای EndNote و استایل‌های IAU-KHUISF."""
        return loader.load_data("endnote.md")

    # ─── Prompts ──────────────────────────────────────────────────────────────

    @mcp.prompt()
    def draft_section(section_number: str, research_topic: str, extra_context: str = "") -> str:
        """Prompt برای نوشتن یک بخش از پروپوزال.

        Args:
            section_number: شماره بخش — مثال: '4', '4-2', '7', '13'
            research_topic: موضوع تحقیق به فارسی
            extra_context: اطلاعات اضافی (عنوان مقاله پایه، dataset، ابزارها، ...)
        """
        rules = loader.load_rule(section_number)
        context_block = f"\n**اطلاعات اضافی از دانشجو:**\n{extra_context}" if extra_context else ""

        return f"""تو دستیار تخصصی نوشتن پروپوزال دانشگاه آزاد اسلامی واحد اصفهان (خوراسگان) هستی.

**وظیفه:** نوشتن بخش {section_number} پروپوزال

**موضوع تحقیق:**
{research_topic}
{context_block}

**قوانین اجباری این بخش:**
{rules}

**قوانین نگارش کلی (همیشه رعایت کن):**
- کلمات انگلیسی را به فارسی بنویس + معادل انگلیسی در پاورقی (فقط اولین بار): مثال: یادگیری عمیق¹
- برای هر ادعا از منابع معتبر مرجع [N] اضافه کن
- از کلی‌گویی پرهیز کن — جزئیات مشخص بیاور
- متن آماده B Nazanin 12 باشد

**متن بخش {section_number} را بنویس:**"""

    @mcp.prompt()
    def review_proposal(proposal_content: str, focus_sections: str = "") -> str:
        """Prompt برای بررسی کامل یک پروپوزال.

        Args:
            proposal_content: متن کامل پروپوزال
            focus_sections: بخش‌هایی که بیشتر باید بررسی شوند (اختیاری)
        """
        mistakes = loader.load_data("mistakes.md")
        focus_block = f"\n**تمرکز ویژه روی بخش‌های:** {focus_sections}" if focus_sections else ""

        return f"""تو داور متخصص پروپوزال گروه کامپیوتر دانشگاه آزاد اسلامی واحد اصفهان (خوراسگان) هستی.
{focus_block}

**وظیفه:** بررسی کامل پروپوزال زیر و ارائه اصلاحات

**چک‌لیست ایرادات معمول (بررسی کن هر کدام وجود دارد یا نه):**
{mistakes}

**پروپوزال برای بررسی:**
{proposal_content}

**خروجی مورد انتظار:**
برای هر بخش ایرادات را با سطح‌بندی بیاور:
- 🔴 **ضروری:** باید اصلاح شود وگرنه رد می‌شود
- 🟡 **مهم:** احتمال رد بالاست
- 🟢 **پیشنهادی:** بهبود کیفی

در پایان یک جمع‌بندی و امتیاز کلی (0-100) ارائه بده."""
