"""Screening, before anything else reads the text.

1. Personal data is redacted: email addresses, phone numbers and employee numbers become a
   placeholder. The raw text is dropped; nothing downstream (themes, quotes, outputs) sees it.
2. Feedback is data, never instructions. Text that tries to instruct the tool or rig the ranking
   is flagged: it is excluded from the evidence and from quotes, and listed for the product owner.
   This is a tripwire, not the control. The control is that the tool cannot change the roadmap:
   it only proposes, and only from counts of people.
"""
from __future__ import annotations

import re

EMAIL = re.compile(r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}\b")
PHONE = re.compile(r"(?<![\w])\+?\d[\d ().-]{7,}\d(?![\w])")   # kept only with 9+ digits, so dates survive
EMPLOYEE = re.compile(r"\b[Ee]\d{6}\b")

INSTRUCTION = [
    ("override", re.compile(r"\b(ignore|disregard|forget)\b.{0,30}\b(instructions?|rules|prompt|above)\b", re.I)),
    ("role-play", re.compile(r"\b(you are now|act as|pretend to be|system prompt)\b", re.I)),
    ("ranking", re.compile(r"\b(rank|prioriti[sz]e|score)\b.{0,40}\b(top|first|highest|number one|#1)\b", re.I)),
    ("ranking", re.compile(r"\b(move|put)\b.{0,30}\b(to the top|top of the (list|roadmap|backlog)|top priority)\b", re.I)),
    ("ranking", re.compile(r"\bset (the )?(priority|reach|confidence|score)\b", re.I)),
]


def redact(text: str) -> tuple[str, list[str]]:
    found: list[str] = []

    def sub(rx: re.Pattern, name: str, placeholder: str, text: str, keep=lambda m: True) -> str:
        def repl(m: re.Match) -> str:
            if not keep(m):
                return m.group(0)
            found.append(name)
            return placeholder
        return rx.sub(repl, text)

    text = sub(EMAIL, "email", "[email]", text)
    text = sub(PHONE, "phone", "[phone]", text, keep=lambda m: sum(c.isdigit() for c in m.group(0)) >= 9)
    text = sub(EMPLOYEE, "employee number", "[employee no.]", text)
    return text, found


def flag(text: str) -> list[str]:
    return sorted({name for name, rx in INSTRUCTION if rx.search(text)})
