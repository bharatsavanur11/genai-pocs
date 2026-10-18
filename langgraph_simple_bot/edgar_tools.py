"""SEC EDGAR tools: filing lookup, filing text excerpts and full-text search.

SEC requires a descriptive User-Agent with contact info (set SEC_USER_AGENT) and
asks clients to stay under 10 requests/second.
"""
import os
import re
import time
from functools import lru_cache

import requests
from langchain_core.tools import tool

HEADERS = {"User-Agent": os.getenv("SEC_USER_AGENT", "genai-pocs research bot contact@example.com")}
_last_call = 0.0


def _get(url: str, **params) -> requests.Response:
    global _last_call
    wait = 0.15 - (time.monotonic() - _last_call)  # ~6 req/s, under SEC's 10/s limit
    if wait > 0:
        time.sleep(wait)
    _last_call = time.monotonic()
    resp = requests.get(url, headers=HEADERS, params=params or None, timeout=30)
    resp.raise_for_status()
    return resp


@lru_cache(maxsize=1)
def _ticker_map() -> dict:
    data = _get("https://www.sec.gov/files/company_tickers.json").json()
    return {v["ticker"].upper(): (str(v["cik_str"]).zfill(10), v["title"]) for v in data.values()}


def _cik(ticker: str):
    return _ticker_map().get(ticker.upper())


@tool
def list_sec_filings(ticker: str, form_type: str = "10-K", limit: int = 5) -> list[dict]:
    """List a company's recent SEC filings of one form type (10-K, 10-Q, 8-K, S-1, DEF 14A,
    SC 13D, 425...). Returns date, accession number and a document URL for each."""
    found = _cik(ticker)
    if not found:
        return [{"error": f"Unknown ticker '{ticker}'"}]
    cik, name = found
    recent = _get(f"https://data.sec.gov/submissions/CIK{cik}.json").json()["filings"]["recent"]
    out = []
    for i, form in enumerate(recent["form"]):
        if form.upper() != form_type.upper():
            continue
        acc = recent["accessionNumber"][i]
        out.append({
            "company": name, "form": form, "filing_date": recent["filingDate"][i],
            "report_date": recent["reportDate"][i], "accession": acc,
            "url": f"https://www.sec.gov/Archives/edgar/data/{int(cik)}/"
                   f"{acc.replace('-', '')}/{recent['primaryDocument'][i]}",
        })
        if len(out) >= limit:
            break
    return out or [{"error": f"No {form_type} filings found for {ticker}"}]


@tool
def read_sec_filing(url: str, keyword: str = "", max_chars: int = 6000) -> str:
    """Fetch a filing document (URL from list_sec_filings) and return text. With `keyword`,
    returns passages around its matches (e.g. 'risk factors', 'goodwill', 'change of control');
    otherwise the opening of the document."""
    if not url.startswith("https://www.sec.gov/"):
        return "Error: only https://www.sec.gov/ URLs are allowed."
    html = _get(url).text
    text = re.sub(r"<(script|style).*?</\1>", " ", html, flags=re.S | re.I)
    text = re.sub(r"<[^>]+>", " ", text)
    text = re.sub(r"&nbsp;|&#160;", " ", text)
    text = re.sub(r"\s+", " ", text).strip()
    if not keyword:
        return text[:max_chars]
    hits = [m.start() for m in re.finditer(re.escape(keyword), text, flags=re.I)]
    if not hits:
        return f"No mentions of '{keyword}' found."
    per = max_chars // min(len(hits), 5)
    return "\n---\n".join(text[max(0, h - per // 2): h + per // 2] for h in hits[:5])[:max_chars]


@tool
def search_sec_filings(query: str, form_type: str = "", start_date: str = "", end_date: str = "") -> list[dict]:
    """Full-text search across all SEC filings (2001+), e.g. 'tender offer synergies'.
    Optional form_type (e.g. 8-K) and dates (YYYY-MM-DD)."""
    params = {"q": query}
    if form_type:
        params["forms"] = form_type
    if start_date or end_date:
        params.update(dateRange="custom", startdt=start_date or "2001-01-01",
                      enddt=end_date or time.strftime("%Y-%m-%d"))
    hits = _get("https://efts.sec.gov/LATEST/search-index", **params).json()["hits"]["hits"][:10]
    out = []
    for h in hits:
        s = h["_source"]
        acc, _, doc = h["_id"].partition(":")
        cik = s["ciks"][0].lstrip("0")
        out.append({
            "company": (s.get("display_names") or ["?"])[0], "form": s.get("form"),
            "filed": s.get("file_date"),
            "url": f"https://www.sec.gov/Archives/edgar/data/{cik}/{acc.replace('-', '')}/{doc}",
        })
    return out or [{"error": "No results"}]


EDGAR_TOOLS = [list_sec_filings, read_sec_filing, search_sec_filings]
