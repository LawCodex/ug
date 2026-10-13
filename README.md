# Uganda (UG) — legislation as Markdown

Part of [LawCodex](https://github.com/LawCodex): the legislation of every country as plain Markdown in git.

Legislation of the Republic of Uganda, in **English**, from the **Parliament of Uganda**:

* the **Constitution of the Republic of Uganda, 1995** (text as originally enacted, Parliament of Uganda copy);
* the **Acts of Parliament** listed on parliament.go.ug ("Acts", one page per year, 2005–2024), as enacted
  (Acts Supplements to the Uganda Gazette).

Retrieved 2026-10-13.

<!-- COUNTS -->
| Directory | Files |
|---|---|
| `acts/` | 346 |
| `constitution/` | 1 |
| **Total** | **347** |
<!-- /COUNTS -->

## Structure

```
constitution/constitution-1995.md
acts/<year>/<slug>.md        year = year in the Act's title
```

File names are slugs of the document names on the Parliament website (e.g.
`acts/2015/anti-terrorism-amendment-act-2015.md`). Front matter: `source` is the Parliament document URL
(cmis.parliament.go.ug), `status` is `unknown`, `note` flags text produced by OCR. A few entries published under
"Acts" are Bill texts (`type: bill`).

## Text and OCR

Most Acts published by Parliament are **scanned PDFs**. Their text was produced by OCR (tesseract 5, English,
300 dpi) and is marked in the `note` field; OCR output was kept only when it passed a plausibility check, but it
contains recognition errors and noise from stamps, signatures and the "assent" page. Sections become
`Section N` headings, `PART` headings are kept; marginal notes appear inside the text.

## Sources

| Source | URL | Used for |
|---|---|---|
| Parliament of Uganda — Acts | https://www.parliament.go.ug/acts (files: `https://cmis.parliament.go.ug/cmis/views/<id>`) | Acts |
| Parliament of Uganda — Constitution (Internet Archive copy of the official file) | https://www.parliament.go.ug/documents/1240/constitution → https://web.archive.org/web/20211127060552/https://www.parliament.go.ug/cmis/views/e138fbaf-95f5-4cbc-ac33-b4678be3577a%253B1.0 | Constitution |

`cmis.parliament.go.ug` asks for a crawl delay of 10 seconds (robots.txt), which was respected.

## Not covered / known gaps

* **This is not the full body of Ugandan law.** The consolidated **Laws of Uganda** (revised editions, latest
  2023) are published by the Uganda Law Reform Commission on a paid publications platform; they were not used.
  The ULII (AfricanLII) site was deliberately not used (its terms forbid bulk download).
* The Parliament website lists at most 20 documents per year (2005–2024); Acts beyond those, Acts before 2005 and
  after 2024 are not included. Duplicate uploads are kept once.
* Constitution: the 1995 text; the amendments of 2000, 2005, 2015, 2017 and 2018 are not incorporated (some
  Constitution (Amendment) Acts are among the Acts).
* 6 documents whose OCR output failed the quality check (e.g. Finance Act 2015, Excise Duty (Amendment) Act 2015,
  Business Licences (Miscellaneous Repeals) Act 2015, the Law Revision (Miscellaneous Amendments) Act 2023) and 1
  document that could not be downloaded (Micro Finance Deposit-Taking Institutions (Amendment) Act 2023) are
  missing; 22 duplicate uploads were kept once.
* Statutory instruments and ordinances are not included.

## Copyright

Ugandan Acts and the Constitution are official public texts published by Parliament. The Markdown conversion
(largely OCR) is provided as is, for information; the authoritative texts are those published in the Uganda Gazette.

## Regenerate

```
python3 -m pip install -r scripts/requirements.txt   # plus poppler and tesseract
python3 scripts/ug_list.py --download   # list + PDFs into ../_raw/ug (10 s crawl delay)
python3 scripts/ug_ocr.py               # text extraction / OCR, cached next to the PDFs
python3 scripts/ug_convert.py
python3 scripts/ug_readme.py
```
