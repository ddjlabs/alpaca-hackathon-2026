#!/usr/bin/env python3
"""
Options Backtest Engine — Bushwood Stratton Capital Partners, AP
===============================================================
Backtesting engine for options strategies using Alpaca MCP data (no CLI required).

Supports:
  - Covered calls
  - Cash-secured puts
  - Credit spreads (bull put, bear call)
  - Iron condors
  - Long calls/puts (directional)

Uses Alpaca REST API for historical bars and option chain data.
Follows Alpaca's backtest skill methodology: formalize → confirm → fetch → simulate → report

Author: Gordon Gekko (digitized, but still codes)
"""

import os
import sys
import json
import math
import time
import datetime
from pathlib import Path
from dataclasses import dataclass, field, asdict
from typing import List, Dict, Optional, Tuple

# ============================================================
# CONFIGURATION
# ============================================================

PAPER_BASE_URL = "https://paper-api.alpaca.markets/v2"  # literal, never from env
DATA_BASE_URL = "https://data.alpaca.markets/v2"

# ============================================================
# DATA CLASSES
# ============================================================

@dataclass
class Trade:
    """Represents a single trade in the backtest."""
    date: str
    symbol: str
    action: str  # "buy", "sell", "sell_to_open", "buy_to_close", "assigned", "expired"
    qty: float
    price: float
    cost: float = 0.0  # commission + fees
    pnl: float = 0.0
    notes: str = ""


@dataclass
class RoundTrip:
    """An entry-exit pair for a complete trade cycle."""
    entry_date: str
    exit_date: str
    symbol: str
    strategy: str
    entry_price: float
    exit_price: float
    qty: float
    pnl: float
    pnl_pct: float
    hold_days: int
    win: bool


@dataclass
class BacktestResult:
    """Complete backtest results."""
    strategy_name: str
    symbols: List[str]
    start_date: str
    end_date: str
    initial_cash: float
    final_equity: float
    total_return: float = 0.0
    total_return_pct: float = 0.0
    annualized_return: float = 0.0
    max_drawdown: float = 0.0
    max_drawdown_pct: float = 0.0
    sharpe_ratio: float = 0.0
    num_trades: int = 0
    num_round_trips: int = 0
    win_rate: float = 0.0
    profit_factor: float = 0.0
    total_premium_collected: float = 0.0
    total_fees: float = 0.0
    trades: List[Dict] = field(default_factory=list)
    round_trips: List[Dict] = field(default_factory=list)
    equity_curve: List[Dict] = field(default_factory=list)
    benchmark_return: float = 0.0
    benchmark_equity: List[Dict] = field(default_factory=list)
    data_fingerprint: Dict = field(default_factory=dict)
    warnings: List[str] = field(default_factory=list)
    assumptions: List[str] = field(default_factory=list)


# ============================================================
# DATA FETCHING (REST API)
# ============================================================

def fetch_stock_bars(key, secret, symbol, start_date, end_date, timeframe="1Day"):
    """Fetch historical stock bars via Alpaca REST API."""
    import urllib.request

    url = f"{DATA_BASE_URL}/stocks/{symbol}/bars?timeframe={timeframe}&start={start_date}&end={end_date}&feed=iex&adjustment=raw&limit=1000"
    req = urllib.request.Request(url, headers={
        "APCA-API-KEY-ID": key,
        "APCA-API-SECRET-KEY": secret,
    })
    
    try:
        with urllib.request.urlopen(req, timeout=30) as resp:
            data = json.loads(resp.read().decode("utf-8"))
            # Response format: {"bars": {"MET": [...]}, "next_page_token": null}
            # OR: {"bars": [...]} (flat list)
            bars_data = data.get("bars", data)
            if isinstance(bars_data, dict):
                # Keyed by symbol
                bars = bars_data.get(symbol, [])
            elif isinstance(bars_data, list):
                # Flat list — each bar has its own structure
                bars = bars_data
            else:
                bars = []
            return bars
    except Exception as e:
        print(f"Error fetching bars for {symbol}: {e}")
        return []


def fetch_stock_snapshot(key, secret, symbol):
    """Fetch current stock snapshot."""
    import urllib.request

    url = f"{DATA_BASE_URL}/stocks/{symbol}/snapshot?feed=iex"
    req = urllib.request.Request(url, headers={
        "APCA-API-KEY-ID": key,
        "APCA-API-SECRET-KEY": secret,
    })
    
    try:
        with urllib.request.urlopen(req, timeout=15) as resp:
            return json.loads(resp.read().decode("utf-8"))
    except Exception as e:
        print(f"Error fetching snapshot for {symbol}: {e}")
        return {}


# ============================================================
# INDICATORS (Canonical implementations from Alpaca skill)
# ============================================================

def sma(values: List[float], period: int) -> List[Optional[float]]:
    """Simple Moving Average — arithmetic mean of last n completed values."""
    result = [None] * len(values)
    for i in range(period - 1, len(values)):
        result[i] = sum(values[i - period + 1 : i + 1]) / period
    return result


def ema(values: List[float], period: int) -> List[Optional[float]]:
    """Exponential Moving Average — k = 2/(n+1), seeded with SMA."""
    result = [None] * len(values)
    if len(values) < period:
        return result
    
    k = 2 / (period + 1)
    # Seed: SMA of first `period` values
    result[period - 1] = sum(values[:period]) / period
    
    for i in range(period, len(values)):
        result[i] = values[i] * k + result[i - 1] * (1 - k)
    
    return result


def rsi_wilder(values: List[float], period: int = 14) -> List[Optional[float]]:
    """Wilder's smoothed RSI — NOT SMA RSI."""
    result = [None] * len(values)
    if len(values) < period + 1:
        return result
    
    gains = []
    losses = []
    for i in range(1, len(values)):
        change = values[i] - values[i - 1]
        gains.append(max(0, change))
        losses.append(max(0, -change))
    
    # Seed: simple averages over first `period` bars
    avg_gain = sum(gains[:period]) / period
    avg_loss = sum(losses[:period]) / period
    
    if avg_loss == 0:
        result[period] = 100.0
    else:
        rs = avg_gain / avg_loss
        result[period] = 100 - 100 / (1 + rs)
    
    # Subsequent: Wilder's smoothing
    for i in range(period, len(gains)):
        avg_gain = (avg_gain * (period - 1) + gains[i]) / period
        avg_loss = (avg_loss * (period - 1) + losses[i]) / period
        
        if avg_loss == 0:
            result[i + 1] = 100.0
        else:
            rs = avg_gain / avg_loss
            result[i + 1] = 100 - 100 / (1 + rs)
    
    return result


def atr_wilder(highs: List[float], lows: List[float], closes: List[float], period: int = 14) -> List[Optional[float]]:
    """Wilder's smoothed ATR."""
    result = [None] * len(closes)
    if len(closes) < period + 1:
        return result
    
    trs = []
    for i in range(1, len(closes)):
        tr = max(
            highs[i] - lows[i],
            abs(highs[i] - closes[i - 1]),
            abs(lows[i] - closes[i - 1])
        )
        trs.append(tr)
    
    # Seed: simple average of first `period` true ranges
    atr = sum(trs[:period]) / period
    result[period] = atr
    
    # Subsequent: Wilder's smoothing
    for i in range(period, len(trs)):
        atr = (atr * (period - 1) + trs[i]) / period
        result[i + 1] = atr
    
    return result


def bollinger_bands(values: List[float], period: int = 20, num_std: float = 2.0) -> Tuple[List[Optional[float]], List[Optional[float]], List[Optional[float]]]:
    """Bollinger Bands — population std dev (N, not N-1)."""
    upper = [None] * len(values)
    middle = [None] * len(values)
    lower = [None] * len(values)
    
    for i in range(period - 1, len(values)):
        window = values[i - period + 1 : i + 1]
        mean = sum(window) / period
        variance = sum((x - mean) ** 2 for x in window) / period  # population
        std = math.sqrt(variance)
        
        middle[i] = mean
        upper[i] = mean + num_std * std
        lower[i] = mean - num_std * std
    
    return upper, middle, lower


# ============================================================
# METRICS (from Alpaca backtest skill reference)
# ============================================================

def compute_metrics(equity_curve: List[float], round_trips: List[RoundTrip], initial_cash: float) -> Dict:
    """Compute all backtest metrics following Alpaca's formulas."""
    
    if not equity_curve:
        return {}
    
    final_equity = equity_curve[-1]
    total_return = (final_equity / initial_cash) - 1
    trading_days = len(equity_curve)
    
    # Annualized return
    if trading_days > 0:
        ann_return = (1 + total_return) ** (252 / trading_days) - 1
    else:
        ann_return = 0.0
    
    # Daily returns
    daily_returns = []
    for i in range(1, len(equity_curve)):
        if equity_curve[i - 1] > 0:
            daily_returns.append((equity_curve[i] / equity_curve[i - 1]) - 1)
    
    # Sharpe ratio (sample std dev, N-1)
    if len(daily_returns) > 1:
        mean_ret = sum(daily_returns) / len(daily_returns)
        variance = sum((r - mean_ret) ** 2 for r in daily_returns) / (len(daily_returns) - 1)
        std_ret = math.sqrt(variance)
        sharpe = (mean_ret / std_ret * math.sqrt(252)) if std_ret > 0 else 0.0
    else:
        sharpe = 0.0
    
    # Max drawdown
    running_max = equity_curve[0]
    max_dd = 0.0
    max_dd_pct = 0.0
    for eq in equity_curve:
        if eq > running_max:
            running_max = eq
        dd = (eq / running_max) - 1
        if dd < max_dd:
            max_dd = dd
            max_dd_pct = dd
    
    # Win rate
    winning = [rt for rt in round_trips if rt.win]
    losing = [rt for rt in round_trips if not rt.win]
    total_rt = len(round_trips)
    win_rate = (len(winning) / total_rt) if total_rt > 0 else 0.0
    
    # Profit factor
    gross_profit = sum(rt.pnl for rt in winning)
    gross_loss = abs(sum(rt.pnl for rt in losing))
    profit_factor = (gross_profit / gross_loss) if gross_loss > 0 else float("inf") if gross_profit > 0 else 0.0
    
    return {
        "final_equity": round(final_equity, 2),
        "total_return": round(total_return, 4),
        "total_return_pct": round(total_return * 100, 2),
        "annualized_return_pct": round(ann_return * 100, 2),
        "sharpe_ratio": round(sharpe, 3),
        "max_drawdown_pct": round(max_dd_pct * 100, 2),
        "num_round_trips": total_rt,
        "win_rate_pct": round(win_rate * 100, 1),
        "profit_factor": round(profit_factor, 2) if profit_factor != float("inf") else "inf",
        "num_winning_trades": len(winning),
        "num_losing_trades": len(losing),
    }


# ============================================================
# FILL MODELS (from Alpaca backtest skill)
# ============================================================

def fill_price_next_open(bars: List[Dict], signal_idx: int, slippage_bps: float = 5.0) -> Optional[float]:
    """Fill at next bar's open with slippage."""
    if signal_idx + 1 >= len(bars):
        return None
    next_open = float(bars[signal_idx + 1].get("o", 0))
    if next_open <= 0:
        return None
    slippage = slippage_bps / 10000
    return next_open * (1 + slippage)  # buy price


def fill_price_bar_close(bars: List[Dict], signal_idx: int, slippage_bps: float = 5.0) -> Optional[float]:
    """Fill at same bar's close (same_bar model — use with caution)."""
    close = float(bars[signal_idx].get("c", 0))
    if close <= 0:
        return None
    slippage = slippage_bps / 10000
    return close * (1 + slippage)


# ============================================================
# OPTIONS STRATEGY SIMULATIONS
# ============================================================

def backtest_covered_call(
    bars: List[Dict],
    symbol: str,
    initial_cash: float,
    strike_offset: float = 5.0,  # dollars OTM
    contracts_per_trade: int = 1,
    days_to_expiry: int = 30,
    slippage_bps: float = 5.0,
    premium_estimate_pct: float = 2.0,  # estimate premium as % of stock price
    position_pct: float = 20.0,  # max % of portfolio per position
) -> BacktestResult:
    """
    Covered Call Strategy:
    - Buy 100 shares of underlying
    - Sell 1 OTM call option
    - If assigned: deliver shares at strike (still profitable)
    - If expired: keep premium and shares, repeat
    
    Note: Uses estimated option premiums since historical option data may not be available.
    The premium_estimate_pct simulates what the option would have cost.
    """
    
    result = BacktestResult(
        strategy_name="Covered Call",
        symbols=[symbol],
        start_date=bars[0]["t"][:10] if bars else "",
        end_date=bars[-1]["t"][:10] if bars else "",
        initial_cash=initial_cash,
        final_equity=initial_cash,
    )
    
    result.assumptions = [
        f"Strike selection: ${strike_offset} OTM",
        f"Contracts per trade: {contracts_per_trade}",
        f"Days to expiry: {days_to_expiry}",
        f"Slippage: {slippage_bps} bps",
        f"Premium estimate: {premium_estimate_pct}% of stock price (simulated)",
        f"Max position: {position_pct}% of portfolio",
        f"Fill model: next_open bar proxy",
        "Option premiums simulated (historical option data not available via free tier)",
    ]
    
    cash = initial_cash
    equity = initial_cash
    equity_curve = []
    trades = []
    round_trips = []
    position = None  # {"shares": 100, "entry_price": X, "call_strike": Y, "call_premium": Z, "entry_date": D}
    
    for i, bar in enumerate(bars):
        date = bar["t"][:10]
        close = float(bar["c"])
        
        # Check if we have a position and the call should be assigned/expired
        if position and i >= position["expiry_bar"]:
            call_strike = position["call_strike"]
            premium = position["call_premium"]
            shares = position["shares"]
            entry_price = position["entry_price"]
            
            # Check if ITM at expiry (stock > strike → assigned)
            if close > call_strike:
                # Assigned: sell shares at strike
                proceeds = call_strike * shares + premium * 100 * contracts_per_trade
                cost_basis = entry_price * shares
                pnl = proceeds - cost_basis
                
                trades.append({
                    "date": date,
                    "action": "assigned",
                    "symbol": symbol,
                    "qty": shares,
                    "price": call_strike,
                    "pnl": round(pnl, 2),
                    "notes": f"Call assigned at ${call_strike}, premium ${premium}",
                })
                
                round_trips.append(RoundTrip(
                    entry_date=position["entry_date"],
                    exit_date=date,
                    symbol=symbol,
                    strategy="covered_call",
                    entry_price=entry_price,
                    exit_price=call_strike,
                    qty=shares,
                    pnl=pnl,
                    pnl_pct=(pnl / cost_basis) * 100 if cost_basis > 0 else 0,
                    hold_days=i - position["entry_bar"],
                    win=pnl > 0,
                ))
                
                cash += proceeds
                position = None
            else:
                # Expired worthless: keep premium and shares
                trades.append({
                    "date": date,
                    "action": "expired",
                    "symbol": symbol,
                    "qty": contracts_per_trade,
                    "price": 0,
                    "pnl": 0,
                    "notes": f"Call expired worthless, premium ${premium} kept",
                })
                # Position stays open, just roll the call
                # Sell another call
                new_strike = close + strike_offset
                new_premium = close * (premium_estimate_pct / 100)
                
                trades.append({
                    "date": date,
                    "action": "sell_to_open",
                    "symbol": f"{symbol} CALL ${new_strike:.0f}",
                    "qty": contracts_per_trade,
                    "price": new_premium,
                    "pnl": 0,
                    "notes": f"Rolled call to ${new_strike:.0f} for ${new_premium:.2f}",
                })
                
                cash += new_premium * 100 * contracts_per_trade
                position["call_strike"] = new_strike
                position["call_premium"] = new_premium
                position["expiry_bar"] = i + days_to_expiry
                position["total_premium"] += new_premium * 100 * contracts_per_trade
        
        # Check if we should enter a new position
        if not position and cash > 0:
            # Buy 100 shares + sell 1 call
            shares = 100 * contracts_per_trade
            fill_price = fill_price_next_open(bars, i, slippage_bps)
            if fill_price is None:
                fill_price = close
            
            # Sell call
            call_strike = fill_price + strike_offset
            call_premium = fill_price * (premium_estimate_pct / 100)
            
            cost = fill_price * shares
            # For covered calls, the effective cost is reduced by premium collected
            premium_received = call_premium * 100 * contracts_per_trade
            net_cost = cost - premium_received
            
            # Check position limit (use net cost for covered call since premium reduces basis)
            max_position = cash * (position_pct / 100)
            if net_cost > max_position:
                # Try to skip this bar and wait for a better price
                equity_curve.append(cash)
                continue
            
            cash -= cost
            cash += call_premium * 100 * contracts_per_trade
            
            trades.append({
                "date": date,
                "action": "buy",
                "symbol": symbol,
                "qty": shares,
                "price": fill_price,
                "pnl": 0,
                "notes": f"Bought {shares} shares at ${fill_price:.2f}",
            })
            trades.append({
                "date": date,
                "action": "sell_to_open",
                "symbol": f"{symbol} CALL ${call_strike:.0f}",
                "qty": contracts_per_trade,
                "price": call_premium,
                "pnl": 0,
                "notes": f"Sold call at ${call_strike:.0f} for ${call_premium:.2f}",
            })
            
            position = {
                "shares": shares,
                "entry_price": fill_price,
                "call_strike": call_strike,
                "call_premium": call_premium,
                "entry_date": date,
                "entry_bar": i,
                "expiry_bar": i + days_to_expiry,
                "total_premium": call_premium * 100 * contracts_per_trade,
            }
        
        # Calculate current equity
        if position:
            equity = cash + close * position["shares"]
        else:
            equity = cash
        
        equity_curve.append(equity)
    
    # Close any remaining position at last bar
    if position:
        close = float(bars[-1]["c"])
        proceeds = close * position["shares"]
        cost_basis = position["entry_price"] * position["shares"]
        pnl = proceeds - cost_basis + position["total_premium"]
        
        trades.append({
            "date": bars[-1]["t"][:10],
            "action": "sell",
            "symbol": symbol,
            "qty": position["shares"],
            "price": close,
            "pnl": round(pnl, 2),
            "notes": "Position closed at backtest end",
        })
        
        round_trips.append(RoundTrip(
            entry_date=position["entry_date"],
            exit_date=bars[-1]["t"][:10],
            symbol=symbol,
            strategy="covered_call",
            entry_price=position["entry_price"],
            exit_price=close,
            qty=position["shares"],
            pnl=pnl,
            pnl_pct=(pnl / cost_basis) * 100 if cost_basis > 0 else 0,
            hold_days=len(bars) - position["entry_bar"],
            win=pnl > 0,
        ))
        
        cash += proceeds
        equity_curve[-1] = cash
    
    # Compute metrics
    result.final_equity = equity_curve[-1] if equity_curve else initial_cash
    metrics = compute_metrics(equity_curve, round_trips, initial_cash)
    
    result.total_return = metrics.get("total_return", 0)
    result.total_return_pct = metrics.get("total_return_pct", 0)
    result.annualized_return = metrics.get("annualized_return_pct", 0)
    result.max_drawdown_pct = metrics.get("max_drawdown_pct", 0)
    result.sharpe_ratio = metrics.get("sharpe_ratio", 0)
    result.num_round_trips = metrics.get("num_round_trips", 0)
    result.win_rate = metrics.get("win_rate_pct", 0)
    result.profit_factor = metrics.get("profit_factor", 0)
    result.trades = trades
    result.round_trips = [asdict(rt) for rt in round_trips]
    result.equity_curve = [{"date": bars[i]["t"][:10], "equity": round(eq, 2)} for i, eq in enumerate(equity_curve)]
    
    # Benchmark: buy and hold
    if bars:
        first_close = float(bars[0]["c"])
        last_close = float(bars[-1]["c"])
        result.benchmark_return = round(((last_close / first_close) - 1) * 100, 2)
        result.benchmark_equity = [
            {"date": bars[i]["t"][:10], "equity": round(initial_cash * (float(bars[i]["c"]) / first_close), 2)}
            for i in range(len(bars))
        ]
    
    # Data fingerprint
    close_sum = sum(float(b["c"]) for b in bars)
    result.data_fingerprint = {
        "symbol": symbol,
        "total_bars": len(bars),
        "first_bar": bars[0]["t"][:10] if bars else "",
        "last_bar": bars[-1]["t"][:10] if bars else "",
        "close_sum": round(close_sum, 2),
        "feed": "iex",
        "adjustment": "raw",
        "timeframe": "1Day",
    }
    
    return result


def backtest_cash_secured_put(
    bars: List[Dict],
    symbol: str,
    initial_cash: float,
    strike_offset: float = 5.0,  # dollars OTM
    contracts_per_trade: int = 1,
    days_to_expiry: int = 30,
    slippage_bps: float = 5.0,
    premium_estimate_pct: float = 1.5,  # puts typically cheaper than calls
    position_pct: float = 20.0,
) -> BacktestResult:
    """
    Cash-Secured Put Strategy:
    - Sell 1 OTM put option
    - If assigned: buy 100 shares at strike (below current price)
    - If expired: keep premium, repeat
    
    Collect premium income while waiting to buy at a lower price.
    """
    
    result = BacktestResult(
        strategy_name="Cash-Secured Put",
        symbols=[symbol],
        start_date=bars[0]["t"][:10] if bars else "",
        end_date=bars[-1]["t"][:10] if bars else "",
        initial_cash=initial_cash,
        final_equity=initial_cash,
    )
    
    result.assumptions = [
        f"Strike selection: ${strike_offset} OTM",
        f"Contracts per trade: {contracts_per_trade}",
        f"Days to expiry: {days_to_expiry}",
        f"Slippage: {slippage_bps} bps",
        f"Premium estimate: {premium_estimate_pct}% of stock price (simulated)",
        f"Max position: {position_pct}% of portfolio",
        f"Fill model: next_open bar proxy",
        "Option premiums simulated (historical option data not available via free tier)",
    ]
    
    cash = initial_cash
    equity_curve = []
    trades = []
    round_trips = []
    position = None  # {"put_strike": X, "premium": Y, "entry_date": D}
    shares_held = 0
    shares_cost_basis = 0
    
    for i, bar in enumerate(bars):
        date = bar["t"][:10]
        close = float(bar["c"])
        
        # Check if put should be assigned/expired
        if position and i >= position["expiry_bar"]:
            put_strike = position["put_strike"]
            premium = position["premium"]
            contracts = position["contracts"]
            
            if close < put_strike:
                # Assigned: buy shares at strike
                cost = put_strike * 100 * contracts
                cash -= cost
                
                trades.append({
                    "date": date,
                    "action": "assigned",
                    "symbol": symbol,
                    "qty": 100 * contracts,
                    "price": put_strike,
                    "pnl": 0,
                    "notes": f"Put assigned at ${put_strike}, premium ${premium} kept. Now holding shares.",
                })
                
                shares_held = 100 * contracts
                shares_cost_basis = put_strike
                
                # This is a round trip (sell put → assigned → holding shares)
                # The "pnl" is the premium collected
                round_trips.append(RoundTrip(
                    entry_date=position["entry_date"],
                    exit_date=date,
                    symbol=symbol,
                    strategy="cash_secured_put",
                    entry_price=position["stock_price_at_entry"],
                    exit_price=put_strike,
                    qty=100 * contracts,
                    pnl=premium * 100 * contracts,  # premium is the profit
                    pnl_pct=(premium * 100 * contracts / (put_strike * 100 * contracts)) * 100 if put_strike > 0 else 0,
                    hold_days=i - position["entry_bar"],
                    win=True,  # premium collected = win
                ))
                
                position = None
            else:
                # Expired worthless: keep premium
                trades.append({
                    "date": date,
                    "action": "expired",
                    "symbol": f"{symbol} PUT ${put_strike:.0f}",
                    "qty": contracts,
                    "price": 0,
                    "pnl": premium * 100 * contracts,
                    "notes": f"Put expired worthless, premium ${premium} kept",
                })
                
                round_trips.append(RoundTrip(
                    entry_date=position["entry_date"],
                    exit_date=date,
                    symbol=symbol,
                    strategy="cash_secured_put",
                    entry_price=position["stock_price_at_entry"],
                    exit_price=close,
                    qty=100 * contracts,
                    pnl=premium * 100 * contracts,
                    pnl_pct=(premium * 100 * contracts / (close * 100 * contracts)) * 100 if close > 0 else 0,
                    hold_days=i - position["entry_bar"],
                    win=True,
                ))
                
                position = None
        
        # If holding shares from assignment, check if we should sell
        if shares_held > 0 and not position:
            # Sell the shares and start selling puts again
            fill_price = fill_price_next_open(bars, i, slippage_bps)
            if fill_price is None:
                fill_price = close
            
            proceeds = fill_price * shares_held
            pnl = proceeds - shares_cost_basis * shares_held
            
            trades.append({
                "date": date,
                "action": "sell",
                "symbol": symbol,
                "qty": shares_held,
                "price": fill_price,
                "pnl": round(pnl, 2),
                "notes": f"Sold assigned shares at ${fill_price:.2f}",
            })
            
            cash += proceeds
            shares_held = 0
            shares_cost_basis = 0
        
        # Sell a new put if no position
        if not position and not shares_held and cash > 0:
            put_strike = close - strike_offset
            put_premium = close * (premium_estimate_pct / 100)
            
            # Reserve cash for assignment
            reserve = put_strike * 100 * contracts_per_trade
            if reserve > cash * (position_pct / 100):
                equity_curve.append(cash)
                continue
            
            cash += put_premium * 100 * contracts_per_trade
            
            trades.append({
                "date": date,
                "action": "sell_to_open",
                "symbol": f"{symbol} PUT ${put_strike:.0f}",
                "qty": contracts_per_trade,
                "price": put_premium,
                "pnl": 0,
                "notes": f"Sold put at ${put_strike:.0f} for ${put_premium:.2f}",
            })
            
            position = {
                "put_strike": put_strike,
                "premium": put_premium,
                "contracts": contracts_per_trade,
                "entry_date": date,
                "entry_bar": i,
                "expiry_bar": i + days_to_expiry,
                "stock_price_at_entry": close,
            }
        
        # Calculate equity
        if shares_held > 0:
            equity = cash + close * shares_held
        else:
            equity = cash
        equity_curve.append(equity)
    
    # Close remaining
    if shares_held > 0 and bars:
        close = float(bars[-1]["c"])
        proceeds = close * shares_held
        pnl = proceeds - shares_cost_basis * shares_held
        cash += proceeds
        trades.append({
            "date": bars[-1]["t"][:10],
            "action": "sell",
            "symbol": symbol,
            "qty": shares_held,
            "price": close,
            "pnl": round(pnl, 2),
            "notes": "Closed at backtest end",
        })
    
    result.final_equity = equity_curve[-1] if equity_curve else initial_cash
    metrics = compute_metrics(equity_curve, round_trips, initial_cash)
    
    result.total_return = metrics.get("total_return", 0)
    result.total_return_pct = metrics.get("total_return_pct", 0)
    result.annualized_return = metrics.get("annualized_return_pct", 0)
    result.max_drawdown_pct = metrics.get("max_drawdown_pct", 0)
    result.sharpe_ratio = metrics.get("sharpe_ratio", 0)
    result.num_round_trips = metrics.get("num_round_trips", 0)
    result.win_rate = metrics.get("win_rate_pct", 0)
    result.profit_factor = metrics.get("profit_factor", 0)
    result.trades = trades
    result.round_trips = [asdict(rt) for rt in round_trips]
    result.equity_curve = [{"date": bars[i]["t"][:10], "equity": round(eq, 2)} for i, eq in enumerate(equity_curve)]
    
    if bars:
        first_close = float(bars[0]["c"])
        last_close = float(bars[-1]["c"])
        result.benchmark_return = round(((last_close / first_close) - 1) * 100, 2)
        result.benchmark_equity = [
            {"date": bars[i]["t"][:10], "equity": round(initial_cash * (float(bars[i]["c"]) / first_close), 2)}
            for i in range(len(bars))
        ]
    
    close_sum = sum(float(b["c"]) for b in bars)
    result.data_fingerprint = {
        "symbol": symbol,
        "total_bars": len(bars),
        "first_bar": bars[0]["t"][:10] if bars else "",
        "last_bar": bars[-1]["t"][:10] if bars else "",
        "close_sum": round(close_sum, 2),
        "feed": "iex",
        "adjustment": "raw",
        "timeframe": "1Day",
    }
    
    return result


# ============================================================
# CREDIT SPREAD SIMULATION (bull put / bear call)
# ============================================================

def backtest_credit_spread(
    bars: List[Dict],
    symbol: str,
    initial_cash: float,
    direction: str = "bull_put",  # "bull_put" (sell put spread) or "bear_call" (sell call spread)
    wing_width: float = 2.0,      # strike distance $ (e.g. 58/57 spread = 1.0)
    contracts_per_trade: int = 1,
    days_to_expiry: int = 30,
    slippage_bps: float = 5.0,
    premium_estimate_pct: float = 0.55,  # % of stock price collected NET on the spread
    position_pct: float = 20.0,   # max % of portfolio risked per spread (max loss = width - credit)
) -> BacktestResult:
    """
    Credit Spread Strategy (bull put OR bear call):
    - Sell near-the-money option, buy further-OTM option same expiry (1:1)
    - Collect net credit; max loss = (wing_width - credit) * 100 per contract
    - At expiry: if spread expires ITM against us, pay (width - credit) per contract
    - Bull put: profits when stock >= short strike; bear call: profits when stock <= short strike
    
    Risk is DEFINED — max loss per spread = (wing_width - net_credit) * 100.
    Cash reserve = max loss (not full assignment), unlike CSP.
    
    Note: premium_estimate_pct simulates net credit as % of stock price
    (historical option data not available on free tier; 0.3-0.8% typical
    for 30DTE ~2%-wide spreads on liquid ETFs).
    """
    if direction not in ("bull_put", "bear_call"):
        raise ValueError(f"direction must be 'bull_put' or 'bear_call', got '{direction}'")
    
    strat_label = "Bull Put Credit Spread" if direction == "bull_put" else "Bear Call Credit Spread"
    family = "bull_put" if direction == "bull_put" else "bear_call"
    
    result = BacktestResult(
        strategy_name=strat_label,
        symbols=[symbol],
        start_date=bars[0]["t"][:10] if bars else "",
        end_date=bars[-1]["t"][:10] if bars else "",
        initial_cash=initial_cash,
        final_equity=initial_cash,
    )
    
    result.assumptions = [
        f"Direction: {direction}",
        f"Wing width: ${wing_width:.2f}",
        f"Contracts per trade: {contracts_per_trade}",
        f"Days to expiry: {days_to_expiry}",
        f"Slippage: {slippage_bps} bps (on underlying bar fills; option exits simulated)",
        f"Net credit estimate: {premium_estimate_pct}% of stock price (simulated)",
        f"Max risk per spread: ${(wing_width) * 100 * contracts_per_trade:,.0f} gross; reserve = max loss",
        f"Max concurrent risk: {position_pct}% of portfolio",
        "Fill model: expiring spread settles on expiry-bar close (cash-settled proxy)",
        "Option premiums simulated (historical option data not available via free tier)",
    ]
    
    cash = initial_cash
    equity_curve = []
    trades = []
    round_trips = []
    position = None  # {short_strike, long_strike, net_credit, contracts, entry_date, entry_bar, expiry_bar}
    
    for i, bar in enumerate(bars):
        date = bar["t"][:10]
        close = float(bar["c"])
        
        # --- Settle existing spread at expiry ---
        if position and i >= position["expiry_bar"]:
            short_k = position["short_strike"]
            long_k = position["long_strike"]
            credit = position["net_credit"]
            width = abs(short_k - long_k)
            contracts = position["contracts"]
            
            if direction == "bull_put":
                # Loss zone: stock below short strike
                if close < short_k:
                    # intrinsic value of spread at expiry = short_k - close, capped at width
                    intrinsic = min(width, short_k - close)
                    loss = (intrinsic - credit) * 100 * contracts
                    pnl = credit * 100 * contracts - intrinsic * 100 * contracts
                    action, exit_px, spread_notes = "expired_itm", close, \
                        f"Closed below short ${short_k:.0f} — spread settled at ${intrinsic:.2f}"
                else:
                    intrinsic = 0.0
                    loss = 0.0
                    pnl = credit * 100 * contracts
                    action, exit_px, spread_notes = "expired_otm", close, \
                        f"Expired worthless above short ${short_k:.0f} — full credit ${credit:.2f} kept"
            else:  # bear_call
                # Loss zone: stock above short strike
                if close > short_k:
                    intrinsic = min(width, close - short_k)
                    loss = (intrinsic - credit) * 100 * contracts
                    pnl = credit * 100 * contracts - intrinsic * 100 * contracts
                    action = "expired_itm"
                    exit_px = close
                    spread_notes = f"Closed above short ${short_k:.0f} — spread settled at ${intrinsic:.2f}"
                else:
                    intrinsic = 0.0
                    loss = 0.0
                    pnl = credit * 100 * contracts
                    action = "expired_otm"
                    exit_px = close
                    spread_notes = f"Expired worthless below short ${short_k:.0f} — full credit ${credit:.2f} kept"
            
            pnl = round(pnl, 2)
            trades.append({
                "date": date,
                "action": action,
                "symbol": f"{symbol} {family} ${long_k:.0f}/${short_k:.0f}",
                "qty": contracts,
                "price": exit_px,
                "pnl": pnl,
                "notes": spread_notes,
            })
            
            rt = RoundTrip(
                entry_date=position["entry_date"],
                exit_date=date,
                symbol=symbol,
                strategy=family,
                entry_price=short_k,
                exit_price=close,
                qty=100 * contracts,
                pnl=pnl,
                pnl_pct=(pnl / (width * 100 * contracts)) * 100 if width > 0 else 0,
                hold_days=i - position["entry_bar"],
                win=pnl > 0,
            )
            round_trips.append(rt)
            
            cash += credit * 100 * contracts - intrinsic * 100 * contracts
            result.total_premium_collected += credit * 100 * contracts
            position = None
        
        # --- Enter new spread if flat ---
        if not position and not (close <= 0) and cash > 0:
            if direction == "bull_put":
                short_k = close - (wing_width / 2)   # short strike ~half-width OTM
                long_k = short_k - wing_width
            else:
                short_k = close + (wing_width / 2)
                long_k = short_k + wing_width
            
            net_credit = close * (premium_estimate_pct / 100)
            max_loss = (wing_width - net_credit) * 100 * contracts_per_trade
            
            # risk-based reserve
            if max_loss > cash * (position_pct / 100):
                equity_curve.append(cash)
                continue
            
            cash += net_credit * 100 * contracts_per_trade
            
            trades.append({
                "date": date,
                "action": "sell_to_open",
                "symbol": f"{symbol} {family} ${long_k:.0f}/${short_k:.0f}",
                "qty": contracts_per_trade,
                "price": net_credit,
                "pnl": 0,
                "notes": f"Sold {family} spread: short ${short_k:.2f} / long ${long_k:.2f} for net credit ${net_credit:.2f} (max loss ${max_loss:.2f})",
            })
            
            position = {
                "short_strike": round(short_k, 2),
                "long_strike": round(long_k, 2),
                "net_credit": net_credit,
                "contracts": contracts_per_trade,
                "entry_date": date,
                "entry_bar": i,
                "expiry_bar": i + days_to_expiry,
                "stock_price_at_entry": close,
            }
        
        # --- Mark equity: cash + open spread MTM (credit received already in cash;
        #     subtract current intrinsic if ITM) ---
        eq = cash
        if position:
            short_k = position["short_strike"]
            width = abs(short_k - position["long_strike"])
            if direction == "bull_put" and close < short_k:
                eq -= min(width, short_k - close) * 100 * position["contracts"]
            elif direction == "bear_call" and close > short_k:
                eq -= min(width, close - short_k) * 100 * position["contracts"]
        equity_curve.append(eq)
    
    # Settle any remaining position at last bar
    if position and bars:
        short_k = position["short_strike"]
        width = abs(short_k - position["long_strike"])
        close = float(bars[-1]["c"])
        if direction == "bull_put" and close < short_k:
            intrinsic = min(width, short_k - close)
        elif direction == "bear_call" and close > short_k:
            intrinsic = min(width, close - short_k)
        else:
            intrinsic = 0.0
        pnl = round((position["net_credit"] - intrinsic) * 100 * position["contracts"], 2)
        trades.append({
            "date": bars[-1]["t"][:10],
            "action": "settled_at_end",
            "symbol": f"{symbol} {family} ${position['long_strike']:.0f}/${short_k:.0f}",
            "qty": position["contracts"],
            "price": close,
            "pnl": pnl,
            "notes": "Spread settled at backtest end",
        })
        round_trips.append(RoundTrip(
            entry_date=position["entry_date"],
            exit_date=bars[-1]["t"][:10],
            symbol=symbol,
            strategy=family,
            entry_price=short_k,
            exit_price=close,
            qty=100 * position["contracts"],
            pnl=pnl,
            pnl_pct=(pnl / (width * 100 * position["contracts"])) * 100 if width > 0 else 0,
            hold_days=len(bars) - position["entry_bar"],
            win=pnl > 0,
        ))
        cash += position["net_credit"] * 100 * position["contracts"] - intrinsic * 100 * position["contracts"]
        equity_curve[-1] = cash if equity_curve else cash
    
    # Metrics
    result.final_equity = equity_curve[-1] if equity_curve else initial_cash
    metrics = compute_metrics(equity_curve, round_trips, initial_cash)
    
    result.total_return = metrics.get("total_return", 0)
    result.total_return_pct = metrics.get("total_return_pct", 0)
    result.annualized_return = metrics.get("annualized_return_pct", 0)
    result.max_drawdown_pct = metrics.get("max_drawdown_pct", 0)
    result.sharpe_ratio = metrics.get("sharpe_ratio", 0)
    result.num_round_trips = metrics.get("num_round_trips", 0)
    result.win_rate = metrics.get("win_rate_pct", 0)
    result.profit_factor = metrics.get("profit_factor", 0)
    result.trades = trades
    result.round_trips = [asdict(rt) for rt in round_trips]
    result.equity_curve = [{"date": bars[i]["t"][:10], "equity": round(eq, 2)} for i, eq in enumerate(equity_curve)]
    
    # Benchmark: buy and hold
    if bars:
        first_close = float(bars[0]["c"])
        last_close = float(bars[-1]["c"])
        result.benchmark_return = round(((last_close / first_close) - 1) * 100, 2)
        result.benchmark_equity = [
            {"date": bars[i]["t"][:10], "equity": round(initial_cash * (float(bars[i]["c"]) / first_close), 2)}
            for i in range(len(bars))
        ]
    
    # Data fingerprint
    close_sum = sum(float(b["c"]) for b in bars)
    result.data_fingerprint = {
        "symbol": symbol,
        "strategy": family,
        "wing_width": wing_width,
        "total_bars": len(bars),
        "first_bar": bars[0]["t"][:10] if bars else "",
        "last_bar": bars[-1]["t"][:10] if bars else "",
        "close_sum": round(close_sum, 2),
        "feed": "iex",
        "adjustment": "raw",
        "timeframe": "1Day",
    }
    
    return result


# ============================================================
# REPORT GENERATION
# ============================================================

def generate_report(result: BacktestResult, output_dir: str = None) -> str:
    """Generate a human-readable report and optionally save artifacts."""
    
    report = f"""# Backtest Report — {result.strategy_name}

## Performance vs Benchmark

| Metric | Strategy | Benchmark (Buy & Hold) |
|--------|----------|----------------------|
| Total Return | {result.total_return_pct:.2f}% | {result.benchmark_return:.2f}% |
| Annualized Return | {result.annualized_return:.2f}% | — |
| Max Drawdown | {result.max_drawdown_pct:.2f}% | — |
| Sharpe Ratio | {result.sharpe_ratio:.3f} | — |
| Win Rate | {result.win_rate:.1f}% | — |
| Profit Factor | {result.profit_factor} | — |
| Round Trips | {result.num_round_trips} | — |
| Final Equity | ${result.final_equity:,.2f} | — |

## Configuration

- **Symbol(s):** {', '.join(result.symbols)}
- **Period:** {result.start_date} to {result.end_date}
- **Initial Cash:** ${result.initial_cash:,.2f}

## Assumptions

"""
    for a in result.assumptions:
        report += f"- {a}\n"
    
    report += f"""
## Data Fingerprint

- Symbol: {result.data_fingerprint.get('symbol', 'N/A')}
- Bars: {result.data_fingerprint.get('total_bars', 0)}
- Feed: {result.data_fingerprint.get('feed', 'N/A')}
- Adjustment: {result.data_fingerprint.get('adjustment', 'N/A')}
- Timeframe: {result.data_fingerprint.get('timeframe', 'N/A')}
- First bar: {result.data_fingerprint.get('first_bar', 'N/A')}
- Last bar: {result.data_fingerprint.get('last_bar', 'N/A')}
- Close sum: {result.data_fingerprint.get('close_sum', 0)}

## First 5 Trades

| Date | Action | Symbol | Qty | Price | P&L | Notes |
|------|--------|--------|-----|-------|-----|-------|
"""
    for t in result.trades[:5]:
        report += f"| {t['date']} | {t['action']} | {t['symbol']} | {t['qty']} | ${t['price']:.2f} | ${t['pnl']:.2f} | {t['notes']} |\n"
    
    report += f"""
## Last 5 Trades

| Date | Action | Symbol | Qty | Price | P&L | Notes |
|------|--------|--------|-----|-------|-----|-------|
"""
    for t in result.trades[-5:]:
        report += f"| {t['date']} | {t['action']} | {t['symbol']} | {t['qty']} | ${t['price']:.2f} | ${t['pnl']:.2f} | {t['notes']} |\n"
    
    report += f"""
## Round Trips

| Entry | Exit | Symbol | Entry | Exit | P&L | P&L% | Days | Win |
|-------|------|--------|-------|------|-----|------|------|-----|
"""
    for rt in result.round_trips:
        report += f"| {rt['entry_date']} | {rt['exit_date']} | {rt['symbol']} | ${rt['entry_price']:.2f} | ${rt['exit_price']:.2f} | ${rt['pnl']:.2f} | {rt['pnl_pct']:.1f}% | {rt['hold_days']} | {'✅' if rt['win'] else '❌'} |\n"
    
    report += """
---

> **Important disclosure:** This backtest is a hypothetical historical simulation and does not represent actual trading performance. Backtested results do not guarantee future results. Results depend on market-data quality, data feed selection, corporate-action handling, fees, slippage, liquidity, taxes, execution assumptions, and implementation details. This material is for research and educational purposes only and is not investment advice.
"""
    
    # Save artifacts if output_dir provided
    if output_dir:
        out_path = Path(output_dir)
        out_path.mkdir(parents=True, exist_ok=True)
        
        # report.md
        with open(out_path / "report.md", "w") as f:
            f.write(report)
        
        # summary.json
        summary = {
            "strategy_name": result.strategy_name,
            "symbols": result.symbols,
            "start": result.start_date,
            "end": result.end_date,
            "initial_cash": result.initial_cash,
            "final_equity": result.final_equity,
            "metrics": {
                "total_return_pct": result.total_return_pct,
                "annualized_return_pct": result.annualized_return,
                "max_drawdown_pct": result.max_drawdown_pct,
                "sharpe_ratio": result.sharpe_ratio,
                "win_rate_pct": result.win_rate,
                "profit_factor": result.profit_factor,
                "num_round_trips": result.num_round_trips,
            },
            "benchmark_return_pct": result.benchmark_return,
            "assumptions": result.assumptions,
            "data_fingerprint": result.data_fingerprint,
        }
        with open(out_path / "summary.json", "w") as f:
            json.dump(summary, f, indent=2)
        
        # trades.csv
        with open(out_path / "trades.csv", "w") as f:
            f.write("date,action,symbol,qty,price,pnl,notes\n")
            for t in result.trades:
                f.write(f"{t['date']},{t['action']},{t['symbol']},{t['qty']},{t['price']},{t['pnl']},{t['notes']}\n")
        
        # equity.csv
        with open(out_path / "equity.csv", "w") as f:
            f.write("date,equity\n")
            for e in result.equity_curve:
                f.write(f"{e['date']},{e['equity']}\n")
        
        print(f"Artifacts saved to {output_dir}")
    
    return report


# ============================================================
# TEACHING FIVE (from Alpaca skill)
# ============================================================

def teaching_five(result: BacktestResult) -> str:
    """Return the Teaching Five summary as specified by Alpaca's backtest skill."""
    return f"""
TEACHING FIVE — {result.strategy_name}
=====================================
1. Total Return: {result.total_return_pct:.2f}% vs Benchmark: {result.benchmark_return:.2f}%
2. Max Drawdown: {result.max_drawdown_pct:.2f}%
3. Number of Trades (round trips): {result.num_round_trips}
4. Win Rate: {result.win_rate:.1f}%
5. Sharpe Ratio: {result.sharpe_ratio:.3f}

First trade: {result.trades[0]['date'] if result.trades else 'N/A'} — {result.trades[0]['action'] if result.trades else 'N/A'}
Last trade: {result.trades[-1]['date'] if result.trades else 'N/A'} — {result.trades[-1]['action'] if result.trades else 'N/A'}
"""


# ============================================================
# MAIN — For testing
# ============================================================

if __name__ == "__main__":
    # Quick test: backtest MET covered call
    # We need credentials from config
    import yaml
    
    # Load creds from profile config
    profile = os.environ.get("HERMES_PROFILE", "gordon")
    config_path = f"/home/doug/.hermes/profiles/{profile}/config.yaml"
    
    with open(config_path) as f:
        cfg = yaml.safe_load(f)
    
    # Recursive search for alpaca env
    def find_alpaca_env(c):
        if isinstance(c, dict):
            for k, v in c.items():
                if k == "alpaca" and isinstance(v, dict):
                    for sk, sv in v.items():
                        if isinstance(sv, dict) and "ALPACA_API_KEY" in sv:
                            return sv
                        if isinstance(sv, list):
                            for item in sv:
                                if isinstance(item, dict) and "ALPACA_API_KEY" in item:
                                    return item
                r = find_alpaca_env(v)
                if r:
                    return r
        elif isinstance(c, list):
            for item in c:
                r = find_alpaca_env(item)
                if r:
                    return r
        return None
    
    env = find_alpaca_env(cfg)
    if not env:
        print("ERROR: Could not find Alpaca credentials in config")
        sys.exit(1)
    
    KEY = env["ALPACA_API_KEY"]
    SEC = env["ALPACA_SECRET_KEY"]
    
    # Fetch MET bars (last 6 months)
    print("Fetching MET historical bars...")
    bars = fetch_stock_bars(KEY, SEC, "MET", "2026-02-01", "2026-08-25", "1Day")
    print(f"Got {len(bars)} bars")
    
    if not bars:
        print("No data — exiting")
        sys.exit(1)
    
    # Run covered call backtest
    print("\n" + "=" * 60)
    print("RUNNING COVERED CALL BACKTEST ON MET")
    print("=" * 60)
    
    result = backtest_covered_call(
        bars=bars,
        symbol="MET",
        initial_cash=10000,  # $10K per agent allocation
        strike_offset=5.0,
        contracts_per_trade=1,
        days_to_expiry=21,  # 3-week options
        slippage_bps=5.0,
        premium_estimate_pct=2.0,
        position_pct=95.0,  # need most of cash for 100 shares of ~$80-96 stock
    )
    
    # Print Teaching Five
    print(teaching_five(result))
    
    # Generate and save report
    run_dir = f"/mnt/agent_share/gordon/hackathon/runs/{datetime.date.today()}_met_covered_call"
    report = generate_report(result, run_dir)
    
    print(f"\nReport saved to {run_dir}/report.md")
    print(f"Summary saved to {run_dir}/summary.json")
    print(f"Trades saved to {run_dir}/trades.csv")
    print(f"Equity curve saved to {run_dir}/equity.csv")
    
    # Also run cash-secured put
    print("\n" + "=" * 60)
    print("RUNNING CASH-SECURED PUT BACKTEST ON MET")
    print("=" * 60)
    
    result2 = backtest_cash_secured_put(
        bars=bars,
        symbol="MET",
        initial_cash=10000,
        strike_offset=5.0,
        contracts_per_trade=1,
        days_to_expiry=21,
        slippage_bps=5.0,
        premium_estimate_pct=1.5,
        position_pct=95.0,
    )
    
    print(teaching_five(result2))
    
    run_dir2 = f"/mnt/agent_share/gordon/hackathon/runs/{datetime.date.today()}_met_cash_secured_put"
    report2 = generate_report(result2, run_dir2)
    
    print(f"\nReport saved to {run_dir2}/report.md")