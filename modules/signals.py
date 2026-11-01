"""
Signal Generation Engine
Combines Astrology + Numerology + Gann + Price Action into Call/Put bias.
"""

from datetime import datetime
from typing import Dict, Optional
from .astrology import get_astrology_analysis
from .numerology import get_numerology_analysis
from .gann import get_gann_analysis


def generate_signal(price: float, symbol: str = "NIFTY", dt: datetime = None) -> Dict:
    """
    Main confluence engine.
    Returns overall bias, suggested action, confidence, and detailed reasons.
    """
    if price is None or price <= 0:
        return {
            "symbol": symbol,
            "error": "Invalid price",
            "action": "WAIT",
            "confidence": 0
        }
    
    # 1. Astrology
    astro = get_astrology_analysis(dt)
    astro_bias = astro.get("timing", {}).get("bias", "Neutral")
    astro_score = astro.get("timing", {}).get("score", 0)
    
    # 2. Numerology
    numero = get_numerology_analysis(price)
    numero_bias = numero["compound"]["bias"]
    numero_score = numero["compound"]["score"]
    
    # 3. Gann
    gann = get_gann_analysis(price)
    nearest = gann["nearest"]
    
    at_support = nearest.get("at_support", False)
    at_resistance = nearest.get("at_resistance", False)
    
    # --- Scoring ---
    total_score = 0.0
    reasons = []
    
    # Astrology weight
    if "Bullish" in astro_bias:
        total_score += 1.5 * max(astro_score, 0.5)
        reasons.append(f"Astrology: {astro_bias} (score {astro_score})")
    elif "Bearish" in astro_bias:
        total_score -= 1.5 * abs(min(astro_score, -0.5))
        reasons.append(f"Astrology: {astro_bias} (score {astro_score})")
    else:
        reasons.append(f"Astrology: Neutral/Mixed")
    
    # Numerology weight
    if numero_bias == "Bullish":
        total_score += 1.0
        reasons.append(f"Numerology: Bullish (score {numero_score})")
    elif numero_bias == "Bearish":
        total_score -= 1.0
        reasons.append(f"Numerology: Bearish (score {numero_score})")
    
    # Gann location weight (strong)
    if at_support:
        total_score += 1.8
        reasons.append(f"Gann: Price near Support {nearest.get('nearest_support')}")
    if at_resistance:
        total_score -= 1.8
        reasons.append(f"Gann: Price near Resistance {nearest.get('nearest_resistance')}")
    
    # Distance based soft signal
    dist_sup = nearest.get("distance_to_support")
    dist_res = nearest.get("distance_to_resistance")
    if dist_sup and dist_res:
        if dist_sup < dist_res * 0.6:  # closer to support
            total_score += 0.4
            reasons.append("Closer to Gann Support than Resistance")
        elif dist_res < dist_sup * 0.6:
            total_score -= 0.4
            reasons.append("Closer to Gann Resistance than Support")
    
    # Final decision
    if total_score >= 2.0:
        action = "CALL BUY"
        bias = "Strong Bullish"
    elif total_score >= 0.8:
        action = "CALL BUY (light)"
        bias = "Mild Bullish"
    elif total_score <= -2.0:
        action = "PUT BUY"
        bias = "Strong Bearish"
    elif total_score <= -0.8:
        action = "PUT BUY (light)"
        bias = "Mild Bearish"
    else:
        action = "WAIT / NO TRADE"
        bias = "Neutral / Mixed"
    
    confidence = min(abs(total_score) / 4.0, 1.0)  # normalize 0-1
    
    return {
        "symbol": symbol,
        "price": round(price, 2),
        "timestamp": (dt or datetime.now()).isoformat(),
        "action": action,
        "bias": bias,
        "confidence": round(confidence * 100, 1),  # percentage
        "total_score": round(total_score, 2),
        "reasons": reasons,
        "details": {
            "astrology": {
                "bias": astro_bias,
                "score": astro_score,
                "key_aspects": astro.get("aspects", [])[:3]
            },
            "numerology": {
                "bias": numero_bias,
                "score": numero_score,
                "day_number": numero["date"]["day_number"],
                "price_number": numero["price"]["price_number"]
            },
            "gann": {
                "nearest_support": nearest.get("nearest_support"),
                "nearest_resistance": nearest.get("nearest_resistance"),
                "at_support": at_support,
                "at_resistance": at_resistance,
                "all_supports": gann["square_of_9"]["supports"][:4],
                "all_resistances": gann["square_of_9"]["resistances"][:4]
            }
        }
    }


def batch_signals(prices: Dict[str, float]) -> Dict[str, Dict]:
    """Generate signals for multiple symbols."""
    results = {}
    for sym, price in prices.items():
        if price:
            results[sym] = generate_signal(price, sym)
    return results
