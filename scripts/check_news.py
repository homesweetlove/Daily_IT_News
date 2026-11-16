#!/usr/bin/env python3
"""Check links, source URLs, and structure of bilingual daily news files."""
from pathlib import Path
import re

ROOT = Path(__file__).resolve().parents[1] / "news"
link = re.compile(r"https?://[^\s)<>]+")
days = sorted(ROOT.glob("????-??-??.md"))
missing = []
errors = []
for original in days:
    english = ROOT / "en" / original.name
    if not english.exists():
        missing.append(original.stem)
        continue
    ko = original.read_text(encoding="utf-8")
    en = english.read_text(encoding="utf-8")
    omitted = set(link.findall(ko)) - set(link.findall(en))
    if omitted:
        errors.append(f"{original.stem}: omitted source URLs: {omitted}")
    if f"en/{original.name}" not in ko:
        errors.append(f"{original.stem}: missing Korean-to-English link")
    if f"../{original.name}" not in en:
        errors.append(f"{original.stem}: missing English-to-Korean link")
    if not en.startswith(("# ", "<!-- source-sha256: ")):
        errors.append(f"{original.stem}: unexpected English document start")
    if len(re.findall(r"^### ", ko, re.M)) != len(re.findall(r"^### ", en, re.M)):
        errors.append(f"{original.stem}: issue heading count differs")

if missing:
    errors.append(f"Missing English translations: {', '.join(missing)}")
if errors:
    raise SystemExit("\n".join(errors))
print(f"OK: {len(days)} bilingual issues; source URLs, links and headings match")
