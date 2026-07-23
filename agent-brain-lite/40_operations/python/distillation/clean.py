"""Clean raw captured traces (notebook step 2) and scrub PHI/PII.

Raw agent/terminal output is "dirty": ANSI colour codes, rate-limit warnings,
menu chrome, BOM. If left in, the student learns the noise as signal. These
helpers strip that noise and redact obvious identifiers before a trace is
written. They are conservative (favour over-redaction) and are *not* a
substitute for human PHI review before corpus promotion.
"""
from __future__ import annotations

import re

# --- noise patterns (notebook step 2: "clean the data") ----------------------

# ANSI/VT100 escape sequences (colour, cursor moves).
_ANSI = re.compile(r"\x1b\[[0-9;?]*[ -/]*[@-~]")

# OSC hyperlink / title sequences: ESC ] ... BEL or ST.
_OSC = re.compile(r"\x1b\][^\x07\x1b]*(?:\x07|\x1b\\)")

# Box-drawing / menu chrome lines (terminal UI frames).
_BOX_CHARS = "│┃┆┇┊┋║╎╏─━┄┅┈┉═╌╍┌┐└┘├┤┬┴┼╭╮╯╰▔▁█▏▕"
_BOX_LINE = re.compile(rf"^[\s{re.escape(_BOX_CHARS)}]+$")

# Rate-limit / quota warnings emitted by the harness, not by the model.
_RATE_LIMIT = re.compile(
    r"^.*\b("
    r"rate[\s_-]?limit"
    r"|quota (?:exceeded|remaining)"
    r"|retry(?:ing)? after \d+"
    r"|429 too many requests"
    r"|overloaded_error"
    r"|please wait \d+ ?s"
    r").*$",
    re.IGNORECASE,
)

# Spinner / progress chrome and carriage-return redraw artifacts.
_SPINNER = re.compile(r"[⠀-⣿▀-▟⠿⣿◐◓◑◒▉▊▋▌▍▎]{2,}")


def clean_text(text: str) -> str:
    """Strip terminal noise from a raw captured string.

    Removes BOM, ANSI/OSC escapes, spinner glyphs, box-drawing menu lines and
    rate-limit warning lines; collapses runs of blank lines. Preserves the
    substantive prompt/reasoning/output content.
    """
    if not text:
        return ""
    # Strip UTF-8 BOM anywhere it snuck in (guards the same bug the capture
    # hook was patched for).
    text = text.replace("﻿", "")
    text = _OSC.sub("", text)
    text = _ANSI.sub("", text)
    text = _SPINNER.sub("", text)

    kept: list[str] = []
    for raw_line in text.splitlines():
        line = raw_line.rstrip()
        if _RATE_LIMIT.match(line):
            continue
        if line and _BOX_LINE.match(line):
            continue
        kept.append(line)

    # Collapse 3+ blank lines into a single blank line.
    out = "\n".join(kept)
    out = re.sub(r"\n{3,}", "\n\n", out)
    return out.strip()


# --- PHI / PII scrubbing (clinical-workspace requirement) --------------------

_EMAIL = re.compile(r"\b[\w.+-]+@[\w-]+\.[\w.-]+\b")
_PHONE = re.compile(r"(?<!\d)(?:\+?\d[\s().-]?){9,15}\d(?!\d)")
# Standalone long digit runs (MRN, OIB, account, ID). 7+ digits.
_LONG_DIGITS = re.compile(r"(?<!\d)\d{7,}(?!\d)")
# ISO-ish or dotted dates that could be a DOB.
_DATE = re.compile(r"\b\d{1,4}[./-]\d{1,2}[./-]\d{1,4}\b")

_REDACTED = "[REDACTED]"


def scrub_phi(text: str) -> tuple[str, list[str]]:
    """Redact obvious identifiers. Returns (scrubbed_text, hit_categories).

    Conservative first pass only — emails, phone-like runs, long digit IDs
    (MRN/OIB), and dotted dates. A non-empty ``hit_categories`` means the trace
    MUST get human review before it can be promoted to the committed corpus.
    """
    hits: list[str] = []

    def _sub(pattern: re.Pattern[str], label: str, value: str) -> str:
        nonlocal hits
        if pattern.search(value):
            if label not in hits:
                hits.append(label)
            return pattern.sub(_REDACTED, value)
        return value

    scrubbed = text
    scrubbed = _sub(_EMAIL, "email", scrubbed)
    scrubbed = _sub(_PHONE, "phone", scrubbed)
    scrubbed = _sub(_LONG_DIGITS, "long_digits", scrubbed)
    scrubbed = _sub(_DATE, "date", scrubbed)
    return scrubbed, hits
