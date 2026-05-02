"""
Structural validation of proposal sections against IAU Khorasgan rules.
Each check is a named class — no lambdas in data structures.
"""
from __future__ import annotations

import re
from abc import ABC, abstractmethod
from dataclasses import dataclass


# ─── Result type ─────────────────────────────────────────────────────────────

@dataclass(frozen=True)
class CheckResult:
    passed: bool
    message: str
    penalty: int


# ─── Base check ──────────────────────────────────────────────────────────────

class SectionCheck(ABC):
    def __init__(self, message: str, penalty: int) -> None:
        self.message = message
        self.penalty = penalty

    @abstractmethod
    def _passes(self, text: str) -> bool: ...

    def run(self, text: str) -> CheckResult:
        passed = self._passes(text)
        return CheckResult(passed=passed, message=self.message, penalty=0 if passed else self.penalty)


# ─── Concrete check types ─────────────────────────────────────────────────────

class ContainsCheck(SectionCheck):
    """Passes if at least one of the given substrings is present."""
    def __init__(self, message: str, penalty: int, *substrings: str) -> None:
        super().__init__(message, penalty)
        self.substrings = substrings

    def _passes(self, text: str) -> bool:
        return any(s in text for s in self.substrings)


class RegexCheck(SectionCheck):
    """Passes if the pattern matches anywhere in the text."""
    def __init__(self, message: str, penalty: int, pattern: str) -> None:
        super().__init__(message, penalty)
        self._pattern = re.compile(pattern)

    def _passes(self, text: str) -> bool:
        return bool(self._pattern.search(text))


class MinLengthCheck(SectionCheck):
    """Passes if text length ≥ min_length."""
    def __init__(self, message: str, penalty: int, min_length: int) -> None:
        super().__init__(message, penalty)
        self.min_length = min_length

    def _passes(self, text: str) -> bool:
        return len(text) >= self.min_length


class TableCheck(SectionCheck):
    """Passes if the text contains enough pipe characters for a markdown table."""
    def __init__(self, message: str, penalty: int, min_pipes: int = 8) -> None:
        super().__init__(message, penalty)
        self.min_pipes = min_pipes

    def _passes(self, text: str) -> bool:
        return text.count("|") >= self.min_pipes


class MinCountRegexCheck(SectionCheck):
    """Passes if the pattern matches at least min_count times."""
    def __init__(self, message: str, penalty: int, pattern: str, min_count: int) -> None:
        super().__init__(message, penalty)
        self._pattern = re.compile(pattern)
        self.min_count = min_count

    def _passes(self, text: str) -> bool:
        return len(self._pattern.findall(text)) >= self.min_count


# ─── Check registry ───────────────────────────────────────────────────────────

COMMON_CHECKS: list[SectionCheck] = [
    MinLengthCheck("متن خیلی کوتاه است (کمتر از ۲۰۰ کاراکتر)", 30, 200),
]

SECTION_CHECKS: dict[str, list[SectionCheck]] = {
    "4": [
        ContainsCheck("زیربخش 4-1 (تشریح ابعاد) یافت نشد", 15, "4-1"),
        ContainsCheck("زیربخش 4-2 (معرفی دقیق مسئله) یافت نشد", 15, "4-2"),
        ContainsCheck("زیربخش 4-3 (جنبه‌های مجهول) یافت نشد", 10, "4-3"),
        ContainsCheck("زیربخش 4-4 (منظور از تحقیق) یافت نشد", 10, "4-4"),
        ContainsCheck("زیربخش 4-5 (پیشینه تحقیق) یافت نشد", 15, "4-5", "پیشینه"),
    ],
    "4-5": [
        TableCheck("جدول مقایسه کارهای پیشین ندارد", 20),
        ContainsCheck("بعد از جدول جمع‌بندی/نتیجه‌گیری نوشته نشده", 15, "جمع‌بندی", "نتیجه", "خلاصه"),
        RegexCheck("مرجع‌دهی [N] در پیشینه یافت نشد", 15, r"\[\d+\]"),
    ],
    "5": [
        RegexCheck("مرجع‌دهی [N] یافت نشد — برای بخش ۵ اجباری است", 15, r"\[\d+\]"),
    ],
    "7": [
        ContainsCheck("«هدف اصلی» یافت نشد", 20, "هدف اصلی"),
        ContainsCheck("«اهداف فرعی» یافت نشد", 20, "اهداف فرعی"),
    ],
    "9": [
        ContainsCheck("«سوال اصلی» یافت نشد", 20, "سوال اصلی", "سؤال اصلی"),
        ContainsCheck("«سوالات فرعی» یافت نشد", 20, "سوالات فرعی", "سؤالات فرعی"),
    ],
    "10": [
        ContainsCheck("کلیدواژه «اگر» در فرضیه‌ها یافت نشد", 15, "اگر"),
        ContainsCheck("کلیدواژه «آنگاه» یا «انتظار» یافت نشد", 15, "آنگاه", "انتظار می‌رود"),
    ],
    "12": [
        TableCheck("جدول تعریف واژه‌ها یافت نشد", 20),
    ],
    "13": [
        ContainsCheck("زیربخش 13-الف (نوع روش تحقیق) یافت نشد", 10, "13-الف", "الف"),
        ContainsCheck("زیربخش 13-ب (متغیرها) یافت نشد", 10, "13-ب", "متغیر"),
        ContainsCheck("زیربخش 13-ج (گردآوری داده) یافت نشد", 5, "13-ج", "گردآوری"),
        ContainsCheck("زیربخش 13-د (ابزار گردآوری) یافت نشد", 5, "13-د", "ابزار"),
        ContainsCheck("زیربخش 13-هـ (جامعه آماری) یافت نشد", 5, "13-ه", "جامعه آماری", "مجموعه داده"),
        ContainsCheck("زیربخش 13-و (تجزیه و تحلیل) یافت نشد", 10, "13-و", "تجزیه"),
    ],
    "14": [
        RegexCheck("مرجع [N] یافت نشد", 20, r"\[\d+\]"),
        MinCountRegexCheck("کمتر از ۵ مرجع — خیلی کم", 15, r"\[\d+\]", 5),
    ],
}


# ─── Public API ───────────────────────────────────────────────────────────────

@dataclass
class ValidationReport:
    section_number: str
    score: int
    issues: list[str]
    suggestions: list[str]


def validate(section_number: str, content: str) -> ValidationReport:
    """Run all applicable checks and return a ValidationReport."""
    failed: list[CheckResult] = []

    for check in COMMON_CHECKS:
        result = check.run(content)
        if not result.passed:
            failed.append(result)

    for check in SECTION_CHECKS.get(section_number, []):
        result = check.run(content)
        if not result.passed:
            failed.append(result)

    total_penalty = sum(r.penalty for r in failed)
    score = max(0, 100 - total_penalty)

    issues = [r.message for r in failed]
    suggestions = _build_suggestions(section_number, issues)

    return ValidationReport(
        section_number=section_number,
        score=score,
        issues=issues,
        suggestions=suggestions,
    )


def _build_suggestions(section_number: str, issues: list[str]) -> list[str]:
    suggestions: list[str] = []
    if any("مرجع" in i for i in issues):
        suggestions.append("برای هر ادعا از منابع معتبر مرجع [N] اضافه کن")
    if any("جدول" in i for i in issues):
        suggestions.append("جدول مقایسه را با ۴ ستون: مرجع | رویکرد | مزایا | معایب بساز")
    if any("جمع‌بندی" in i or "نتیجه" in i for i in issues):
        suggestions.append("بعد از جدول مقایسه، یک پاراگراف جمع‌بندی بنویس که نشان دهد چرا تحقیق تو هنوز مورد نیاز است")
    if any("کوتاه" in i for i in issues):
        suggestions.append("محتوای بخش را گسترش بده — حداقل ۳-۴ پاراگراف برای بخش‌های اصلی")
    if section_number == "10" and issues:
        suggestions.append("قالب صحیح فرضیه: «اگر [متغیر مستقل X] آنگاه [متغیر وابسته Y بهبود یابد]»")
    return suggestions
