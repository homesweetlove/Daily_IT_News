import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
from translate_news import ensure_korean_link, translate_markdown


def fake_translation(text, from_code, to_code):
    assert (from_code, to_code) == ("ko", "en")
    return {
        "요약": "Summary",
        "공식 권고": "Official advisory",
        "취약점 발견": "Vulnerability found",
        "데일리 뉴스": "Daily News",
    }.get(text, "EN: " + text)


class NewsTranslationTests(unittest.TestCase):
    def test_preserves_links_code_and_structure(self):
        text = (
            "# 데일리 뉴스\n\n"
            "## 요약\n\n"
            "- **취약점 발견:** `CVE-2026-12345` "
            "[공식 권고](https://example.com/advisory)\n"
            "<a id=\"source-1\"></a>\n"
            "1. https://example.com/advisory\n"
        )
        result = translate_markdown(text, "2026-10-01", fake_translation)
        self.assertIn("# Daily News", result)
        self.assertIn("## Summary", result)
        self.assertIn("`CVE-2026-12345`", result)
        self.assertIn("[Official advisory](https://example.com/advisory)", result)
        self.assertIn("<a id=\"source-1\"></a>", result)
        self.assertIn("1. https://example.com/advisory", result)
        self.assertIn("<!-- source-sha256: ", result)

    def test_korean_navigation_is_idempotent(self):
        original = "# 제목\n\n본문\n"
        once = ensure_korean_link(original, "2026-10-01")
        self.assertEqual(ensure_korean_link(once, "2026-10-01"), once)
        self.assertIn("en/2026-10-01.md", once)


if __name__ == "__main__":
    unittest.main()
