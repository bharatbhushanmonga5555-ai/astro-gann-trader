"""
Console version of Astro-Gann-Numerology Tool
(No Streamlit needed - pure Python)
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from datetime import datetime
from modules.signals import generate_signal
from modules.data_fetcher import get_latest_price, get_multi_prices
from modules.astrology import get_astrology_analysis, HAS_SWISSEPH
from modules.gann import get_gann_analysis
from modules.numerology import get_numerology_analysis


def print_header():
    print("=" * 60)
    print("  ASTRO + GANN + NUMEROLOGY TRADING RESEARCH TOOL")
    print("  Educational Prototype - Not Financial Advice")
    print("=" * 60)
    print()


def analyze_symbol(symbol: str, price: float = None):
    if price is None:
        print(f"Fetching price for {symbol}...")
        price = get_latest_price(symbol)
    
    if price is None:
        print(f"Could not fetch price for {symbol}. Enter manually.")
        try:
            price = float(input(f"Enter current price for {symbol}: "))
        except:
            print("Invalid price.")
            return
    
    print(f"\n{'─'*50}")
    print(f"  {symbol}  |  Price: {price:,.2f}")
    print(f"{'─'*50}")
    
    signal = generate_signal(price, symbol)
    
    print(f"\n  ACTION      : {signal['action']}")
    print(f"  BIAS        : {signal['bias']}")
    print(f"  CONFIDENCE  : {signal['confidence']}%")
    print(f"  TOTAL SCORE : {signal['total_score']}")
    
    print("\n  Reasons:")
    for r in signal["reasons"]:
        print(f"    • {r}")
    
    gann = signal["details"]["gann"]
    print(f"\n  Gann Nearest Support    : {gann.get('nearest_support')}")
    print(f"  Gann Nearest Resistance : {gann.get('nearest_resistance')}")
    print(f"  At Support?             : {gann.get('at_support')}")
    print(f"  At Resistance?          : {gann.get('at_resistance')}")
    
    print(f"\n  Supports   : {gann.get('all_supports')}")
    print(f"  Resistances: {gann.get('all_resistances')}")
    
    num = signal["details"]["numerology"]
    print(f"\n  Numerology Day Number  : {num.get('day_number')}")
    print(f"  Numerology Price Number: {num.get('price_number')}")
    print(f"  Numerology Bias        : {num.get('bias')}")


def main():
    print_header()
    
    if not HAS_SWISSEPH:
        print("⚠️  pyswisseph not installed → Astrology limited")
        print("   Install: pip install pyswisseph\n")
    
    print("Available instruments: NIFTY, BANKNIFTY, GOLD, CRUDEOIL, NATURALGAS")
    print()
    
    while True:
        print("\nOptions:")
        print("  1. Analyze one instrument")
        print("  2. Analyze all (Nifty + BankNifty + Gold + Crude + NG)")
        print("  3. Show current Astrology snapshot")
        print("  4. Exit")
        
        choice = input("\nEnter choice (1-4): ").strip()
        
        if choice == "1":
            sym = input("Enter symbol (NIFTY/BANKNIFTY/GOLD/CRUDEOIL/NATURALGAS): ").strip().upper()
            analyze_symbol(sym)
        
        elif choice == "2":
            symbols = ["NIFTY", "BANKNIFTY", "GOLD", "CRUDEOIL", "NATURALGAS"]
            prices = get_multi_prices(symbols)
            for sym, price in prices.items():
                if price:
                    analyze_symbol(sym, price)
                else:
                    print(f"\n{sym}: Price not available via free source")
        
        elif choice == "3":
            print("\nFetching planetary positions...")
            astro = get_astrology_analysis()
            if "error" in astro:
                print(astro["error"])
            else:
                print("\nPlanetary Positions (Sidereal):")
                for p, data in astro.get("positions", {}).items():
                    if "sign" in data:
                        retro = " (R)" if data.get("retrograde") else ""
                        print(f"  {p:10} : {data['sign']:12} {data['degree']:6.2f}°{retro}")
                
                print("\nMajor Aspects:")
                for asp in astro.get("aspects", [])[:8]:
                    print(f"  {asp['planet1']}-{asp['planet2']} : {asp['aspect']} (orb {asp['orb']}°)")
                
                timing = astro.get("timing", {})
                print(f"\nMarket Timing Bias: {timing.get('bias')} (score {timing.get('score')})")
                for r in timing.get("reasons", []):
                    print(f"  • {r}")
        
        elif choice == "4":
            print("\nGoodbye. Trade responsibly!")
            break
        else:
            print("Invalid choice.")


if __name__ == "__main__":
    main()
