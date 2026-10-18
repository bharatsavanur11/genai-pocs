# LangGraph Simple Bot

A minimal LangGraph chatbot: `START -> chatbot -> END`, with `MemorySaver` for multi-turn memory.

```bash
pip install -r requirements.txt
export OPENAI_API_KEY=...
python bot.py
```

Optional: `OPENAI_MODEL` (default `gpt-4o-mini`).

## Finance bot

`finance_bot.py` adds tools for market data and valuation (`finance_tools.py`) and SEC EDGAR
filing search (`edgar_tools.py`). Set `SEC_USER_AGENT="Your Name your@email.com"` — SEC requires
a contact in the User-Agent.

### Streamlit UI

```bash
streamlit run app.py
```

Enter your OpenAI key (and SEC User-Agent) in the sidebar. Tool calls appear as expandable
panels above each answer. `get_sec_financials` pulls annual revenue, EBITDA, free cash flow,
debt and more from SEC XBRL filings to feed the DCF/LBO tools.

### NSE India

`nse_tools.py` adds `get_nse_quote`, `get_nse_announcements`, `get_nse_results` and
`get_nse_indices`. NSE has no official API: these call the JSON endpoints behind nseindia.com
(browser headers + session cookies), so they can break or be rate-limited without notice, and
NSE blocks many cloud/datacenter IPs. For fundamentals use the yfinance tools with `.NS`
symbols (e.g. `RELIANCE.NS`). For production, consider a licensed feed.
