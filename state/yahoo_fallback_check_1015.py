"""Verify Yahoo options-chain fallback for 14:30 forced reprice (Alpaca option quotes dead)."""
import json, urllib.request

def yahoo(url):
    r = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36'})
    with urllib.request.urlopen(r, timeout=30) as resp:
        return json.loads(resp.read())

for sym in ('XLF', 'XLP'):
    try:
        d = yahoo(f'https://query1.finance.yahoo.com/v7/finance/options/{sym}')
        res = d.get('optionChain', {}).get('result', [{}])[0]
        quote = res.get('quote', {})
        opts = res.get('options', [])
        print(f"{sym}: spot {quote.get('regularMarketPrice')} | expiries {len(opts)}")
        if opts:
            calls_puts = opts[0].get('puts', [])
            want = {'XLF': ['XLF260918P00055500', 'XLF260918P00055000'], 'XLP': ['XLP260918P00083000']}[sym]
            for p in calls_puts:
                if p.get('contractSymbol') in want:
                    print(f"   {p.get('contractSymbol')}: bid {p.get('bid')} x ask {p.get('ask')} | last {p.get('lastPrice')} | iv {p.get('impliedVolatility')}")
    except Exception as e:
        print(sym, 'FAIL:', repr(e)[:150])