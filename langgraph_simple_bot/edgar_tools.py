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


# First concept with data wins; companies tag the same line item differently.
XBRL_CONCEPTS = {
    "revenue": ["RevenueFromContractWithCustomerExcludingAssessedTax", "Revenues", "SalesRevenueNet"],
    "operating_income": ["OperatingIncomeLoss"],
    "net_income": ["NetIncomeLoss"],
    "d_and_a": ["DepreciationDepletionAndAmortization", "DepreciationAndAmortization", "Depreciation"],
    "operating_cash_flow": ["NetCashProvidedByUsedInOperatingActivities"],
    "capex": ["PaymentsToAcquirePropertyPlantAndEquipment", "PaymentsToAcquireProductiveAssets"],
    "cash": ["CashAndCashEquivalentsAtCarryingValue"],
    "long_term_debt": ["LongTermDebtNoncurrent", "LongTermDebt"],
    "short_term_debt": ["DebtCurrent", "LongTermDebtCurrent"],
    "equity": ["StockholdersEquity"],
    "shares_outstanding": ["CommonStockSharesOutstanding"],
}


def _annual_series(facts: dict, concepts: list[str]) -> dict:
    """{fiscal_year_end: value} from 10-K facts; full-year durations only for flow items."""
    from datetime import date

    for concept in concepts:
        node = facts.get(concept)
        if not node:
            continue
        unit = "USD" if "USD" in node["units"] else next(iter(node["units"]))
        series = {}
        for f in node["units"][unit]:
            if f.get("form") not in ("10-K", "10-K/A") or f.get("fp") != "FY":
                continue
            if "start" in f and not 350 <= (date.fromisoformat(f["end"]) - date.fromisoformat(f["start"])).days <= 380:
                continue
            series[f["end"]] = f["val"]  # later filings overwrite restated values
        if series:
            return series
    return {}


@tool
def get_sec_financials(ticker: str, years: int = 5) -> dict:
    """Annual financials straight from SEC XBRL filings (USD): revenue, operating income,
    net income, D&A, EBITDA (= operating income + D&A), operating cash flow, capex, free cash
    flow (= CFO - capex), cash, debt, equity, shares. Use to build DCF/LBO inputs."""
    found = _cik(ticker)
    if not found:
        return {"error": f"Unknown ticker '{ticker}'"}
    cik, name = found
    facts = _get(f"https://data.sec.gov/api/xbrl/companyfacts/CIK{cik}.json").json()["facts"].get("us-gaap", {})
    series = {k: _annual_series(facts, v) for k, v in XBRL_CONCEPTS.items()}
    ends = sorted({e for s in series.values() for e in s}, reverse=True)[:years]
    rows = []
    for end in ends:
        r = {k: series[k].get(end) for k in series}
        if r["operating_income"] is not None and r["d_and_a"] is not None:
            r["ebitda"] = r["operating_income"] + r["d_and_a"]
        if r["operating_cash_flow"] is not None and r["capex"] is not None:
            r["free_cash_flow"] = r["operating_cash_flow"] - abs(r["capex"])
        debt = [r["long_term_debt"], r["short_term_debt"]]
        if any(d is not None for d in debt):
            r["total_debt"] = sum(d or 0 for d in debt)
        rows.append({"fiscal_year_end": end, **{k: v for k, v in r.items() if v is not None}})
    return {"company": name, "currency": "USD", "annual": rows} if rows else {"error": "No XBRL data found"}


EDGAR_TOOLS = [list_sec_filings, read_sec_filing, search_sec_filings, get_sec_financials]
