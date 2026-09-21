# Data Sources and Provenance

| Source | Use | Freshness | Credentials | Provenance stored |
|---|---|---|---|---|
| User CSV | Personal transactions | User-controlled | None | import hash, source, import timestamp |
| Included sample dataset | Demo | Static | None | `demo_synthetic` |
| Included Kaggle dataset | Historical public dataset | Static | None | `historical_public_dataset` |
| yfinance / Yahoo Finance | Quotes and market history | Provider-dependent live/delayed | None | provider, source, retrieval time |
| ddgs | Financial news discovery | Search-time | None | provider, source, retrieval time |
| SEC EDGAR | US public-company submissions and XBRL facts | Filing-time | SEC user agent | source URL, provider, retrieval time |
| FRED | US macroeconomic series | Series-dependent | FRED API key | source URL, provider, retrieval time |

The application does not label static datasets as real-time. Indian market feeds are not scraped or redistributed when exchange licensing would restrict such use.
