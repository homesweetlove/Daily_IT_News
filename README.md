[![English](https://img.shields.io/badge/README-English-24292f?style=for-the-badge)](./README.md) [![한국어](https://img.shields.io/badge/README-%ED%95%9C%EA%B5%AD%EC%96%B4-24292f?style=for-the-badge)](./README.ko.md)

# Daily IT News

A date-based Markdown archive for **IT, AI, and security issues worth reviewing each day**.

Rather than collecting links only, the archive groups reports covering the same event when possible and records the key facts, why the issue matters, and points to watch or respond to.

## Read the News / 언어 선택

| Date (KST) | English | 한국어 |
| --- | --- | --- |
| 2026-11-16 | [Read in English](news/en/2026-11-16.md) | [한국어로 읽기](news/2026-11-16.md) |
| 2026-11-15 | [Read in English](news/en/2026-11-15.md) | [한국어로 읽기](news/2026-11-15.md) |

- [**Browse English editions**](news/en/) · [**Browse the full Korean archive**](news/)
- **All 50 currently archived Korean issues have matching English editions** (September 18–November 16, 2026). The full bilingual date list is in the [English archive index](news/en/README.md).
- Older English issues were translated automatically and **have not all received professional editing**. Machine translation may distort names, technical terms, or security advice. Consult the linked primary sources before acting on a report.
- A [GitHub Actions translation workflow](.github/workflows/translate-news.yml) generates missing or changed English editions when Korean news files are pushed to `main`. It does not collect or author news automatically. Failed workflows may require manual intervention.

## Repository Structure

```text
Daily_IT_News/
└─ news/
   ├─ 2026-09-18.md
   ├─ ...
   ├─ 2026-11-16.md
   └─ en/
      ├─ 2026-09-18.md
      ├─ ...
      └─ 2026-11-16.md
```

A Korean file is stored as `news/YYYY-MM-DD.md`. Available English translations use `news/en/YYYY-MM-DD.md` with the same KST date. The English edition is a translation of that date's Korean selection, not a separately researched international news roundup.

## Document Format

Each daily document generally includes:

1. Writing time and research scope
2. At-a-glance summary
3. IT issues
4. Security issues
5. Key summary for each issue
6. Why it matters
7. Response / monitoring points
8. Original sources

Company-announced performance, schedules, and figures are separated from independently verified facts whenever possible.

## Purpose

- Quickly review major IT issues missed during the day
- Record security vulnerabilities and real-world attacks
- Track changes in AI, cloud, software, and hardware industries
- Keep a personal archive for looking up issues by date later

## Sources

Each Markdown file includes links to the articles and official materials used.

Because the archive summarizes source reporting and announcements, important decisions or security responses should be based on a fresh review of the **official advisories and original sources** linked in the relevant document.

## Finding a Date

Use:

```text
news/YYYY-MM-DD.md
news/en/YYYY-MM-DD.md
```

Example:

```text
news/2026-11-16.md
news/en/2026-11-16.md
```
