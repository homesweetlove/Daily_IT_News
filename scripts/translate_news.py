#!/usr/bin/env python3
"""Publish English translations alongside Korean daily IT news.

The Korean Markdown files are the source of truth. English issues created by
this script carry a source hash so changed Korean issues can be regenerated.
Existing hand-edited English issues without this marker are preserved.
"""

from __future__ import annotations

import argparse
import hashlib
import re
from functools import lru_cache
from pathlib import Path
from typing import Callable

ROOT = Path(__file__).resolve().parents[1]
NEWS = ROOT / "news"
ENGLISH = NEWS / "en"

HANGUL = re.compile(r"[가-힣]")
MARKDOWN_PARTS = re.compile(
    r"(\[[^\]]+\]\([^\n)]*\)|`[^`\n]+`|https?://[^\s)<>]+|<[^>]+>"
    r"|\bCVE-\d{4}-\d+\b|\bGHSA-[\w-]+\b|\b\d+(?:\.\d+){1,3}\b|\*\*|__)"
)
MD_LINK = re.compile(r"^\[([^\]]+)\]\(([^\n)]*)\)$")
PREFIX = re.compile(r"^(\s*(?:(?:#{1,6}|>|-|\*|\+|\d+\.)\s+))")
SOURCE_MARKER = re.compile(r"<!-- source-sha256: ([a-f0-9]{64}) -->")
DAY = re.compile(r"\d{4}-\d{2}-\d{2}\.md$")

GLOSSARY = {
    "한눈에 보는 핵심 요약": "At a Glance",
    "IT 이슈": "IT News",
    "보안 이슈": "Security News",
    "출처": "Sources",
    "핵심 요약": "Key Points",
    "왜 중요한가": "Why It Matters",
    "새 소식": "What's New",
    "대응": "Response",
    "관찰 포인트": "What to Watch",
}


def sha256(content: str) -> str:
    return hashlib.sha256(content.encode("utf-8")).hexdigest()


def make_translator() -> Callable[[str], str]:
    import argostranslate.package
    import argostranslate.translate

    installed = argostranslate.translate.get_installed_languages()
    has_pair = any(
        lang.code == "ko" and any(to.code == "en" for to in lang.translations_to)
        for lang in installed
    )
    if not has_pair:
        argostranslate.package.update_package_index()
        packages = argostranslate.package.get_available_packages()
        model = next(
            (item for item in packages if item.from_code == "ko" and item.to_code == "en"),
            None,
        )
        if model is None:
            raise RuntimeError("No Korean-to-English Argos Translate model is available")
        argostranslate.package.install_from_path(model.download())
    return argostranslate.translate.translate


def markdown_translator(translate: Callable[[str], str]) -> Callable[[str], str]:
    @lru_cache(maxsize=20000)
    def english(text: str) -> str:
        if not HANGUL.search(text):
            return text
        original = text.strip()
        if original in GLOSSARY:
            converted = GLOSSARY[original]
        else:
            converted = translate(original, "ko", "en").strip()
        if not converted:
            raise ValueError(f"Translation was empty for {original[:80]!r}")
        leading = text[: len(text) - len(text.lstrip())]
        trailing = text[len(text.rstrip()) :]
        return leading + converted + trailing

    def translate_line(line: str) -> str:
        if not HANGUL.search(line):
            return line
        prefix = PREFIX.match(line)
        beginning = prefix.group(0) if prefix else ""
        content = line[len(beginning) :]
        parts = MARKDOWN_PARTS.split(content)
        translated = []
        for token in parts:
            match = MD_LINK.fullmatch(token)
            if match:
                translated.append(f"[{english(match.group(1))}]({match.group(2)})")
            elif (
                token.startswith(("http://", "https://", "`", "<"))
                or token in {"**", "__"}
                or re.fullmatch(r"(?:CVE-\d{4}-\d+|GHSA-[\w-]+|\d+(?:\.\d+){1,3})", token)
            ):
                translated.append(token)
            else:
                translated.append(english(token))
        return beginning + "".join(translated)

    return translate_line


def translate_markdown(
    source: str, day: str, translate: Callable[[str, str, str], str]
) -> str:
    line_translator = markdown_translator(translate)
    result = []
    inside_fence = False
    for line in source.splitlines():
        if line.lstrip().startswith(("~~~", "```")):
            inside_fence = not inside_fence
            result.append(line)
        elif inside_fence or line.lstrip().startswith("<a id="):
            result.append(line)
        else:
            result.append(line_translator(line))
    if inside_fence:
        raise ValueError(f"Unclosed code fence in {day}")
    if not result or not result[0].startswith("# "):
        raise ValueError(f"Missing translated title for {day}")
    result.insert(
        1,
        f"\n[한국어 / Korean](../{day}.md) · **English edition**\n"
        "\n> **Translation note:** Automatically translated from the Korean edition. "
        "Consult linked original sources before relying on security guidance.",
    )
    result.insert(0, f"<!-- source-sha256: {sha256(source)} -->")
    return "\n".join(result).rstrip() + "\n"


def ensure_korean_link(source: str, day: str) -> str:
    link = f"en/{day}.md"
    if link in source:
        return source
    lines = source.splitlines()
    if not lines or not lines[0].startswith("# "):
        raise ValueError(f"Missing Korean title in {day}")
    lines.insert(1, f"\n**한국어판** · [Read in English / 영어판]({link})")
    return "\n".join(lines) + ("\n" if source.endswith("\n") else "")


def write_index() -> None:
    days = sorted((p.stem for p in ENGLISH.glob("????-??-??.md")), reverse=True)
    rows = [
        "# Daily IT News — English Archive",
        "",
        "[한국어 전체 목록 / Korean archive](../) · [Repository README](../../README.md)",
        "",
        "English editions preserve the original reporting dates and source links.",
        "Some older issues are automatically translated; technical and security advice",
        "should be checked against the linked primary sources.",
        "",
        "| Date (KST) | English | Korean |",
        "| --- | --- | --- |",
    ]
    rows.extend(
        f"| {day} | [English]({day}.md) | [한국어](../{day}.md) |" for day in days
    )
    (ENGLISH / "README.md").write_text("\n".join(rows) + "\n", encoding="utf-8")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--date", help="Translate one YYYY-MM-DD issue for testing")
    args = parser.parse_args()
    ENGLISH.mkdir(parents=True, exist_ok=True)
    sources = sorted(p for p in NEWS.glob("*.md") if DAY.fullmatch(p.name))
    if args.date:
        sources = [p for p in sources if p.stem == args.date]
        if not sources:
            raise SystemExit(f"Unknown issue date: {args.date}")

    pending: list[tuple[Path, Path, str]] = []
    for src in sources:
        original = src.read_text(encoding="utf-8")
        target = ENGLISH / src.name
        # Hash the post-navigation Korean source. The first translation run
        # must not invalidate its own cached result by adding a language link.
        original = ensure_korean_link(original, src.stem)
        if target.exists():
            marker = SOURCE_MARKER.search(target.read_text(encoding="utf-8")[:200])
            if marker is None or marker.group(1) == sha256(original):
                continue  # Preserve manually edited translations or unchanged originals.
        pending.append((src, target, original))

    if pending:
        translate = make_translator()
        for num, (src, target, original) in enumerate(pending, start=1):
            target.write_text(
                translate_markdown(original, src.stem, translate), encoding="utf-8"
            )
            print(f"[{num}/{len(pending)}] Translated {src.name}", flush=True)

    # Apply language links only for dates with an English edition.
    for src in sources:
        if (ENGLISH / src.name).exists():
            original = src.read_text(encoding="utf-8")
            linked = ensure_korean_link(original, src.stem)
            if original != linked:
                src.write_text(linked, encoding="utf-8")

    write_index()
    print(f"English editions: {len(list(ENGLISH.glob('????-??-??.md')))}")


if __name__ == "__main__":
    main()
