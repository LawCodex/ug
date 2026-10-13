#!/usr/bin/env python3
"""Uganda: convert the Constitution and the Acts downloaded by ug_list.py (../../_raw/ug) to Markdown.
Run ug_ocr.py first: most Acts on parliament.go.ug are scanned PDFs (text produced by OCR)."""
import hashlib
import json
import os
import re
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import ug_text as T  # noqa

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
RAW = os.path.join(os.path.dirname(REPO), "_raw", "ug")
RETRIEVED = os.environ.get("LC_RETRIEVED", "2026-10-13")
CONST = {"file": "constitution.pdf",
         "source": "https://www.parliament.go.ug/cmis/views/e138fbaf-95f5-4cbc-ac33-b4678be3577a%253B1.0",
         "archived": "https://web.archive.org/web/20211127060552/https://www.parliament.go.ug/cmis/views/e138fbaf-95f5-4cbc-ac33-b4678be3577a%253B1.0",
         "page": "https://www.parliament.go.ug/documents/1240/constitution"}
STARTS = (r"^BE IT ENACTED\b", r"^ENACTED\b", r"^An Act\b", r"^AN ACT\b", r"^I ASSENT\b")


def clean_title(name):
    t = re.sub(r"\.pdf$", "", name, flags=re.I).strip()
    t = re.sub(r"\s*\((\d|Working Copy)\)$", "", t)
    t = re.sub(r"[-_ ]\d$", "", t)
    t = re.sub(r"_compressed$", "", t)
    t = t.replace("_", " ")
    t = re.sub(r"\s+", " ", t).strip()
    if t.lower() == t or t.upper() == t:
        small = {"and", "of", "the", "for", "to", "in", "on", "a", "an", "by", "with", "or"}
        t = " ".join(w if (i and w.lower() in small) else w[:1].upper() + w[1:].lower() for i, w in enumerate(t.split()))
    t = re.sub(r"(Act|Bill)\.? (\d{4})$", r"\1, \2", t)
    return t


def convert(pdf, meta, title, path, art_word="Section", starts=STARTS, body_from=None):
    if not os.path.exists(pdf + ".text.json"):
        return "not-extracted"  # run ug_ocr.py first
    pages, ocr = T.pdf_text(pdf, "eng")
    if body_from:
        k = next((i for i, p in enumerate(pages) if re.search(body_from, p)), 0)
        pages = pages[k:]
    txt = "\n".join(pages)
    good = [p for p in pages if len(p.strip()) > 150]
    if len(good) < max(1, len(pages) * 0.5) or T.text_quality(txt) < 0.8:
        return "low-quality"
    if ocr:
        meta["note"] = (meta.get("note", "") + " Text obtained by OCR (scanned PDF); may contain recognition errors.").strip()
    lines = [x.upper() if re.match(r"^(Chapter|Part) [A-Z][a-z]+(-[A-Z]?[a-z]+)?\.?$", x) else x for x in T.clean_pages(pages)]
    body = T.structure(T.drop_toc(lines, starts=starts), "en", art_word=art_word)
    T.write_md(path, meta, title, body)
    return "ocr" if ocr else "text"


def main():
    res = {}
    pdf = os.path.join(RAW, "pdf", CONST["file"])
    meta = {"title": "Constitution of the Republic of Uganda, 1995", "identifier": "Constitution of the Republic of Uganda, 1995",
            "type": "constitution", "jurisdiction": "ug", "language": "en", "date": "1995-10-08", "status": "in_force",
            "source": CONST["source"], "archived_source": CONST["archived"], "retrieved": RETRIEVED,
            "note": "Text of the Constitution as originally enacted (1995), as published by the Parliament of Uganda; later amendments (2000, 2005, 2015, 2017, 2018) are not incorporated."}
    res["constitution"] = convert(pdf, meta, meta["title"], os.path.join(REPO, "constitution", "constitution-1995.md"),
                                  art_word="Article", body_from=r"WE THE PEOPLE OF UGANDA")
    seen = set()
    for a in json.load(open(os.path.join(RAW, "acts.json"))):
        a["file"] = re.sub(r"[^A-Za-z0-9]+", "_", a["url"].split("/")[-1])[:60] + ".pdf"  # as in ug_list.py
        pdf = os.path.join(RAW, "pdf", a["file"])
        if not os.path.exists(pdf) or not T.pdf_ok(pdf):
            res[a["url"]] = "missing"
            continue
        h = hashlib.md5(open(pdf, "rb").read()).hexdigest()
        if h in seen:
            res[a["url"]] = "duplicate"
            continue
        seen.add(h)
        title = clean_title(a["name"])
        m = re.search(r"\b(19|20)\d\d\b", title)
        year = m.group(0) if m else str(a["year"])
        meta = {"title": title, "type": "bill" if re.search(r"\bBill\b", title) else "act", "jurisdiction": "ug",
                "language": "en", "year": int(year), "status": "unknown", "source": a["url"], "retrieved": RETRIEVED,
                "note": "As enacted (Acts Supplement to the Uganda Gazette); not consolidated."}
        path = os.path.join(REPO, "acts", year, T.slug(title) + ".md")
        if os.path.exists(path) and path in seen:
            path = path[:-3] + "-" + h[:6] + ".md"
        seen.add(path)
        res[a["url"]] = convert(pdf, meta, title, path)
    json.dump(res, open(os.path.join(RAW, "convert_report.json"), "w"), indent=1)
    from collections import Counter
    print(Counter(res.values()))


if __name__ == "__main__":
    main()
