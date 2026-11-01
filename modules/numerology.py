"""
Numerology Module for Trading
Calculates day numbers, price numbers, and compatibility scores.
"""

from datetime import datetime, date
from typing import Dict, Tuple


def reduce_to_single_digit(n: int) -> int:
    """Reduce a number to single digit (except master numbers 11, 22, 33)."""
    if n in (11, 22, 33):
        return n
    while n > 9:
        n = sum(int(d) for d in str(n))
        if n in (11, 22, 33):
            return n
    return n


def date_number(d: date = None) -> Dict[str, int]:
    """Calculate numerology number for a given date."""
    if d is None:
        d = date.today()
    
    day = d.day
    month = d.month
    year = d.year
    
    day_num = reduce_to_single_digit(day)
    month_num = reduce_to_single_digit(month)
    year_num = reduce_to_single_digit(sum(int(x) for x in str(year)))
    
    total = day + month + year
    destiny = reduce_to_single_digit(total)
    
    return {
        "day_number": day_num,
        "month_number": month_num,
        "year_number": year_num,
        "destiny_number": destiny,
        "full_date_sum": total
    }


def price_number(price: float) -> Dict[str, int]:
    """Calculate numerology from price (last digits and full)."""
    # Use integer part and last 3-4 digits
    price_int = int(round(price))
    last_digits = price_int % 10000  # last 4 digits
    
    reduced = reduce_to_single_digit(last_digits)
    digit_sum = sum(int(d) for d in str(price_int))
    reduced_full = reduce_to_single_digit(digit_sum)
    
    return {
        "price_last4": last_digits,
        "price_number": reduced,
        "full_price_number": reduced_full
    }


def compound_score(date_nums: Dict, price_nums: Dict) -> Dict:
    """
    Generate a simple bullish/bearish score based on numerology match.
    Higher positive = more bullish tendency.
    """
    day_n = date_nums["day_number"]
    dest_n = date_nums["destiny_number"]
    price_n = price_nums["price_number"]
    
    # Simple harmonic numbers (bullish): 1, 3, 5, 6, 9
    # Challenging: 2, 4, 7, 8
    bullish_nums = {1, 3, 5, 6, 9, 11, 22, 33}
    
    score = 0
    reasons = []
    
    if day_n in bullish_nums:
        score += 1
        reasons.append(f"Day number {day_n} is supportive")
    else:
        score -= 1
        reasons.append(f"Day number {day_n} is challenging")
    
    if dest_n in bullish_nums:
        score += 1
        reasons.append(f"Destiny number {dest_n} is supportive")
    else:
        score -= 0.5
    
    # Price number matching destiny or day
    if price_n == dest_n or price_n == day_n:
        score += 1.5
        reasons.append(f"Price number {price_n} matches date energy")
    
    if price_n in bullish_nums:
        score += 0.5
    
    bias = "Bullish" if score >= 1.5 else "Bearish" if score <= -1 else "Neutral"
    
    return {
        "score": round(score, 2),
        "bias": bias,
        "reasons": reasons
    }


def get_numerology_analysis(price: float, d: date = None) -> Dict:
    """Complete numerology analysis for trading."""
    date_nums = date_number(d)
    price_nums = price_number(price)
    compound = compound_score(date_nums, price_nums)
    
    return {
        "date": date_nums,
        "price": price_nums,
        "compound": compound
    }
