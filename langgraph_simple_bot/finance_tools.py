"""Finance tools for the bot: live market data (yfinance) and valuation calculators."""
import yfinance as yf
from langchain_core.tools import tool


@tool
def get_stock_snapshot(ticker: str) -> dict:
    """Get price, market cap, valuation multiples and sector for a ticker (e.g. AAPL)."""
    info = yf.Ticker(ticker).info
    if not info or info.get("regularMarketPrice") is None and info.get("currentPrice") is None:
        return {"error": f"No market data found for '{ticker}'"}
    keys = [
        "shortName", "sector", "industry", "currency", "currentPrice", "marketCap",
        "enterpriseValue", "trailingPE", "forwardPE", "enterpriseToEbitda",
        "enterpriseToRevenue", "totalRevenue", "ebitda", "totalDebt", "totalCash",
        "beta", "fiftyTwoWeekLow", "fiftyTwoWeekHigh",
    ]
    return {k: info.get(k) for k in keys}


@tool
def get_price_history(ticker: str, period: str = "1y") -> dict:
    """Summarise price history. period: 1mo, 3mo, 6mo, 1y, 2y, 5y."""
    hist = yf.Ticker(ticker).history(period=period)
    if hist.empty:
        return {"error": f"No price history for '{ticker}'"}
    start, end = float(hist["Close"].iloc[0]), float(hist["Close"].iloc[-1])
    return {
        "ticker": ticker, "period": period, "start_close": round(start, 2),
        "end_close": round(end, 2), "return_pct": round((end / start - 1) * 100, 2),
        "high": round(float(hist["High"].max()), 2), "low": round(float(hist["Low"].min()), 2),
    }


@tool
def compare_multiples(tickers: list[str]) -> list[dict]:
    """Compare trading multiples (EV/EBITDA, P/E, EV/Revenue) across peer tickers."""
    rows = []
    for t in tickers:
        info = yf.Ticker(t).info or {}
        rows.append({
            "ticker": t, "name": info.get("shortName"), "market_cap": info.get("marketCap"),
            "ev_ebitda": info.get("enterpriseToEbitda"), "pe": info.get("trailingPE"),
            "ev_revenue": info.get("enterpriseToRevenue"),
        })
    return rows


@tool
def dcf_valuation(
    free_cash_flows: list[float], discount_rate: float, terminal_growth: float,
    net_debt: float = 0.0, shares_outstanding: float = 0.0,
) -> dict:
    """Discounted cash flow. free_cash_flows are projected yearly FCFs; rates are decimals
    (0.10 = 10%). Returns enterprise value, equity value and per-share value if shares given."""
    if discount_rate <= terminal_growth:
        return {"error": "discount_rate must exceed terminal_growth"}
    pv = sum(cf / (1 + discount_rate) ** (i + 1) for i, cf in enumerate(free_cash_flows))
    tv = free_cash_flows[-1] * (1 + terminal_growth) / (discount_rate - terminal_growth)
    pv_tv = tv / (1 + discount_rate) ** len(free_cash_flows)
    ev = pv + pv_tv
    out = {"pv_of_fcf": round(pv, 2), "pv_of_terminal_value": round(pv_tv, 2),
           "enterprise_value": round(ev, 2), "equity_value": round(ev - net_debt, 2)}
    if shares_outstanding:
        out["value_per_share"] = round((ev - net_debt) / shares_outstanding, 2)
    return out


@tool
def lbo_returns(
    entry_ebitda: float, entry_multiple: float, exit_multiple: float, debt_pct: float,
    ebitda_growth: float, years: int = 5, debt_paydown_pct: float = 0.5,
) -> dict:
    """Simple LBO returns. debt_pct = share of purchase price funded by debt (0.6 = 60%);
    ebitda_growth is annual (0.08 = 8%); debt_paydown_pct = share of initial debt repaid by exit."""
    price = entry_ebitda * entry_multiple
    debt = price * debt_pct
    equity = price - debt
    exit_ebitda = entry_ebitda * (1 + ebitda_growth) ** years
    exit_debt = debt * (1 - debt_paydown_pct)
    exit_equity = exit_ebitda * exit_multiple - exit_debt
    moic = exit_equity / equity
    return {"purchase_price": round(price, 2), "equity_invested": round(equity, 2),
            "exit_equity": round(exit_equity, 2), "moic": round(moic, 2),
            "irr_pct": round((moic ** (1 / years) - 1) * 100, 2) if moic > 0 else None}


@tool
def accretion_dilution(
    acquirer_net_income: float, acquirer_shares: float, target_net_income: float,
    purchase_price: float, pct_stock: float, acquirer_share_price: float,
    cost_of_debt: float = 0.06, tax_rate: float = 0.25, synergies_pretax: float = 0.0,
) -> dict:
    """Merger EPS accretion/dilution. pct_stock = share of price paid in stock (rest is debt)."""
    new_shares = purchase_price * pct_stock / acquirer_share_price
    interest = purchase_price * (1 - pct_stock) * cost_of_debt * (1 - tax_rate)
    pro_forma_ni = acquirer_net_income + target_net_income + synergies_pretax * (1 - tax_rate) - interest
    pro_forma_eps = pro_forma_ni / (acquirer_shares + new_shares)
    standalone = acquirer_net_income / acquirer_shares
    return {"standalone_eps": round(standalone, 4), "pro_forma_eps": round(pro_forma_eps, 4),
            "accretion_pct": round((pro_forma_eps / standalone - 1) * 100, 2),
            "new_shares_issued": round(new_shares, 2)}


FINANCE_TOOLS = [get_stock_snapshot, get_price_history, compare_multiples,
                 dcf_valuation, lbo_returns, accretion_dilution]
