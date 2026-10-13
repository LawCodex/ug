#!/usr/bin/env python3
"""Uganda: list the Acts published by the Parliament of Uganda (parliament.go.ug/acts/acts-<year>)
and download the PDFs (cmis.parliament.go.ug; robots.txt Crawl-delay 10 s is respected).
Writes ../../_raw/ug/acts.json."""
import html
import json
import os
import re
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import ug_text as T  # noqa

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
RAW = os.path.join(os.path.dirname(REPO), "_raw", "ug")
YEARS = range(2005, 2027)


CONST_ARCHIVED = ("https://web.archive.org/web/20211127060552id_/https://www.parliament.go.ug/cmis/views/"
                  "e138fbaf-95f5-4cbc-ac33-b4678be3577a%253B1.0")


def main():
    # Constitution: the Parliament's document is no longer served; Internet Archive copy of the official file
    T.fetch(CONST_ARCHIVED, os.path.join(RAW, "pdf", "constitution.pdf"), delay=3, check_pdf=True)
    acts = []
    for y in YEARS:
        p = os.path.join(RAW, "list", "%d.html" % y)
        T.fetch("https://www.parliament.go.ug/acts/acts-%d" % y, p, delay=10)
        if not os.path.exists(p):
            continue
        t = open(p, encoding="utf-8", errors="replace").read()
        m = re.search(r'<ul class="cmisviews">(.*?)</ul>', t, re.S)
        if not m:
            continue
        for href, name in re.findall(r'<a href="(https://cmis\.parliament\.go\.ug/cmis/views/[^"]+)">([^<]+)</a>', m.group(1)):
            acts.append({"year": y, "url": href, "name": html.unescape(html.unescape(name)).strip()})
    # assented Acts linked from the side block (sites/default/files)
    for y in YEARS:
        t = open(os.path.join(RAW, "list", "%d.html" % y), encoding="utf-8", errors="replace").read() if os.path.exists(os.path.join(RAW, "list", "%d.html" % y)) else ""
        for href, name in re.findall(r'<a href="(/sites/default/files/[^"]+\.pdf)">([^<]+)</a>', t):
            u = "https://www.parliament.go.ug" + href
            if "Act" in name and not any(a["url"] == u for a in acts):
                yy = re.search(r"(20\d\d)", name)
                acts.append({"year": int(yy.group(1)) if yy else None, "url": u, "name": html.unescape(name).strip()})
    json.dump(acts, open(os.path.join(RAW, "acts.json"), "w"), indent=1)
    print(len(acts), "entries")
    if "--download" in sys.argv:
        for a in acts:
            fn = re.sub(r"[^A-Za-z0-9]+", "_", a["url"].split("/")[-1])[:60] + ".pdf"
            a["file"] = fn
            r = T.fetch(a["url"], os.path.join(RAW, "pdf", fn), delay=10, check_pdf=True, tries=2)
            print("ok" if r else "FAIL", a["year"], a["name"], flush=True)
        json.dump(acts, open(os.path.join(RAW, "acts.json"), "w"), indent=1)


if __name__ == "__main__":
    main()
