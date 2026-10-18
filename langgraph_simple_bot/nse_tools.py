"""NSE India tools: live quotes, corporate announcements, results and index levels.

NSE has no official public API. These use the JSON endpoints behind nseindia.com, which
require browser-like headers and session cookies and may change or rate-limit without notice.
For fundamentals/multiples, the yfinance tools work with the ".NS" suffix (e.g. RELIANCE.NS).
"""
import time

import requests
from langchain_core.tools import tool

BASE = "https://www.nseindia.com"
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) "
                  "Chrome/124.0 Safari/537.36",
    "Accept": "application/json, text/plain, */*",
    "Accept-Language": "en-US,en;q=0.9",
    "Referer": BASE,
}
_session = None
_session_ts = 0.0
SESSION_TTL = 300  # cookies go stale; re-prime every 5 minutes


def _get_session() -> requests.Session:
    global _session, _session_ts
    if _session is None or time.monotonic() - _session_ts > SESSION_TTL:
        _session = requests.Session()
        _session.headers.update(HEADERS)
        _session.get(BASE, timeout=20)  # sets the cookies the API requires
        _session_ts = time.monotonic()
    return _session


def _api(path: str, **params):
    resp = _get_session().get(f"{BASE}/api/{path}", params=params, timeout=20)
    if resp.status_code in (401, 403):  # stale cookies: re-prime once and retry
        global _session
        _session = None
        resp = _get_session().get(f"{BASE}/api/{path}", params=params, timeout=20)
    resp.raise_for_status()
    return resp.json()


def _symbol(s: str) -> str:
    return s.upper().removesuffix(".NS")


@tool
def get_nse_quote(symbol: str) -> dict:
    """Live NSE quote for an equity symbol (e.g. RELIANCE, TCS, HDFCBANK; '.NS' suffix is ok).
    Returns price in INR, day change, day/52-week range, P/E vs sector P/E and industry."""
    d = _api("quote-equity", symbol=_symbol(symbol))
    if not d.get("priceInfo"):
        return {"error": f"No NSE data for '{symbol}'"}
    p, meta = d["priceInfo"], d.get("metadata", {})
    return {
        "symbol": d["info"]["symbol"], "company": d["info"]["companyName"], "currency": "INR",
        "last_price": p["lastPrice"], "change": p["change"], "pct_change": p["pChange"],
        "previous_close": p["previousClose"], "day_low": p["intraDayHighLow"]["min"],
        "day_high": p["intraDayHighLow"]["max"], "week52_low": p["weekHighLow"]["min"],
        "week52_high": p["weekHighLow"]["max"], "pe": meta.get("pdSymbolPe"),
        "sector_pe": meta.get("pdSectorPe"), "industry": meta.get("industry"),
        "as_of": meta.get("lastUpdateTime"),
    }


@tool
def get_nse_announcements(symbol: str, limit: int = 10) -> list[dict]:
    """Recent NSE corporate announcements for a company: results, board meetings, M&A,
    fund raising, SEBI takeover-code disclosures, etc. Includes links to the filing PDFs."""
    rows = _api("corporate-announcements", index="equities", symbol=_symbol(symbol))
    return [
        {"date": r.get("an_dt"), "subject": r.get("desc"), "details": (r.get("attchmntText") or "")[:400],
         "attachment": r.get("attchmntFile")}
        for r in rows[:limit]
    ] or [{"error": f"No announcements for '{symbol}'"}]


@tool
def get_nse_results(symbol: str, limit: int = 5) -> list[dict]:
    """Recent quarterly/annual financial results filed with NSE (amounts as filed, typically
    INR lakhs/crores per the filing's own units)."""
    data = _api("results-comparision", symbol=_symbol(symbol))
    rows = data.get("resCmpData") or []
    keep = ["re_to_dt", "re_desc", "re_net_sale", "re_oth_inc_new", "re_tot_exp", "re_pro_loss_bef_tax",
            "re_tax", "re_net_profit", "re_basic_eps", "re_audited"]
    return [{k: r[k] for k in keep if k in r} for r in rows[:limit]] or [{"error": f"No results for '{symbol}'"}]


@tool
def get_nse_indices(names: list[str] | None = None) -> list[dict]:
    """Current levels, % change, P/E, P/B and dividend yield of NSE indices. Pass names such as
    ['NIFTY 50', 'NIFTY BANK', 'NIFTY IT']; omit for the main broad-market indices."""
    wanted = {n.upper() for n in (names or ["NIFTY 50", "NIFTY NEXT 50", "NIFTY BANK", "NIFTY MIDCAP 100",
                                            "NIFTY SMALLCAP 100", "INDIA VIX"])}
    return [
        {"index": r["index"], "last": r.get("last"), "pct_change": r.get("percentChange"),
         "pe": r.get("pe"), "pb": r.get("pb"), "dividend_yield": r.get("dy"),
         "year_high": r.get("yearHigh"), "year_low": r.get("yearLow")}
        for r in _api("allIndices")["data"] if r["index"].upper() in wanted
    ]


NSE_TOOLS = [get_nse_quote, get_nse_announcements, get_nse_results, get_nse_indices]
