"""
Astrology Module using Swiss Ephemeris (pyswisseph)
Provides planetary positions, aspects, and basic market timing signals.
"""

from datetime import datetime, timezone, timedelta
from typing import Dict, List, Tuple, Optional
import math

try:
    import swisseph as swe
    HAS_SWISSEPH = True
except ImportError:
    HAS_SWISSEPH = False
    print("Warning: pyswisseph not installed. Astrology features limited.")


# Planet IDs in Swiss Ephemeris
PLANETS = {
    "Sun": swe.SUN if HAS_SWISSEPH else 0,
    "Moon": swe.MOON if HAS_SWISSEPH else 1,
    "Mercury": swe.MERCURY if HAS_SWISSEPH else 2,
    "Venus": swe.VENUS if HAS_SWISSEPH else 3,
    "Mars": swe.MARS if HAS_SWISSEPH else 4,
    "Jupiter": swe.JUPITER if HAS_SWISSEPH else 5,
    "Saturn": swe.SATURN if HAS_SWISSEPH else 6,
    "Rahu": swe.TRUE_NODE if HAS_SWISSEPH else 10,  # Mean/True Node
}

# Major aspects and their orbs (degrees)
ASPECTS = {
    "Conjunction": (0, 8),
    "Opposition": (180, 8),
    "Trine": (120, 6),
    "Square": (90, 6),
    "Sextile": (60, 4),
}


def set_ephemeris_path(path: str = None):
    """Set path to ephemeris files if needed."""
    if HAS_SWISSEPH and path:
        swe.set_ephe_path(path)


def julian_day(dt: datetime) -> float:
    """Convert datetime to Julian Day."""
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=timezone.utc)
    return swe.julday(dt.year, dt.month, dt.day, 
                      dt.hour + dt.minute/60 + dt.second/3600)


def get_planet_positions(dt: datetime = None, ayanamsa: str = "lahiri") -> Dict[str, Dict]:
    """
    Get sidereal planetary positions.
    Returns longitude, sign, degree, speed (retrograde if negative).
    """
    if not HAS_SWISSEPH:
        return {"error": "pyswisseph not available"}
    
    if dt is None:
        dt = datetime.now(timezone.utc)
    
    jd = julian_day(dt)
    
    # Set ayanamsa
    if ayanamsa.lower() == "lahiri":
        swe.set_sid_mode(swe.SIDM_LAHIRI)
    elif ayanamsa.lower() == "krishnamurti":
        swe.set_sid_mode(swe.SIDM_KRISHNAMURTI)
    else:
        swe.set_sid_mode(swe.SIDM_LAHIRI)
    
    positions = {}
    signs = ["Aries", "Taurus", "Gemini", "Cancer", "Leo", "Virgo",
             "Libra", "Scorpio", "Sagittarius", "Capricorn", "Aquarius", "Pisces"]
    
    for name, pid in PLANETS.items():
        try:
            # Flags: sidereal + speed
            result, ret = swe.calc_ut(jd, pid, swe.FLG_SIDEREAL | swe.FLG_SPEED)
            lon = result[0] % 360
            speed = result[3]
            
            sign_idx = int(lon // 30)
            degree = lon % 30
            
            positions[name] = {
                "longitude": round(lon, 4),
                "sign": signs[sign_idx],
                "degree": round(degree, 2),
                "speed": round(speed, 4),
                "retrograde": speed < 0
            }
        except Exception as e:
            positions[name] = {"error": str(e)}
    
    return positions


def find_aspects(positions: Dict) -> List[Dict]:
    """Find major aspects between planets."""
    aspects_found = []
    planet_names = list(positions.keys())
    
    for i, p1 in enumerate(planet_names):
        if "longitude" not in positions[p1]:
            continue
        for p2 in planet_names[i+1:]:
            if "longitude" not in positions[p2]:
                continue
            
            lon1 = positions[p1]["longitude"]
            lon2 = positions[p2]["longitude"]
            diff = abs(lon1 - lon2)
            if diff > 180:
                diff = 360 - diff
            
            for asp_name, (angle, orb) in ASPECTS.items():
                if abs(diff - angle) <= orb:
                    aspects_found.append({
                        "planet1": p1,
                        "planet2": p2,
                        "aspect": asp_name,
                        "orb": round(abs(diff - angle), 2),
                        "exact_diff": round(diff, 2)
                    })
    
    return aspects_found


def market_timing_bias(positions: Dict, aspects: List[Dict]) -> Dict:
    """
    Simple rule-based market bias from astrology.
    This is educational / research oriented.
    """
    score = 0.0
    reasons = []
    
    # Moon sign influence (simplified)
    if "Moon" in positions and "sign" in positions["Moon"]:
        moon_sign = positions["Moon"]["sign"]
        fiery = ["Aries", "Leo", "Sagittarius"]
        watery = ["Cancer", "Scorpio", "Pisces"]
        if moon_sign in fiery:
            score += 0.5
            reasons.append(f"Moon in {moon_sign} (fiery - active)")
        elif moon_sign in watery:
            score -= 0.3
            reasons.append(f"Moon in {moon_sign} (emotional/volatile)")
    
    # Retrogrades
    for planet in ["Mercury", "Venus", "Mars"]:
        if planet in positions and positions[planet].get("retrograde"):
            score -= 0.4
            reasons.append(f"{planet} retrograde (caution)")
    
    # Key aspects
    for asp in aspects:
        p1, p2, aspect = asp["planet1"], asp["planet2"], asp["aspect"]
        
        # Bullish aspects
        if aspect in ["Trine", "Sextile"] and set([p1, p2]) & {"Jupiter", "Venus", "Sun"}:
            score += 0.6
            reasons.append(f"{p1}-{p2} {aspect} (supportive)")
        
        # Bearish / volatile
        if aspect in ["Square", "Opposition"] and set([p1, p2]) & {"Mars", "Saturn"}:
            score -= 0.7
            reasons.append(f"{p1}-{p2} {aspect} (challenging)")
        
        if aspect == "Conjunction" and "Mars" in (p1, p2) and "Saturn" in (p1, p2):
            score -= 1.0
            reasons.append("Mars-Saturn conjunction (high caution)")
    
    bias = "Bullish" if score >= 0.8 else "Bearish" if score <= -0.8 else "Neutral / Mixed"
    
    return {
        "score": round(score, 2),
        "bias": bias,
        "reasons": reasons[:6]  # limit
    }


def get_astrology_analysis(dt: datetime = None) -> Dict:
    """Full astrology snapshot for trading research."""
    if not HAS_SWISSEPH:
        return {
            "error": "Install pyswisseph: pip install pyswisseph",
            "positions": {},
            "aspects": [],
            "timing": {"bias": "Unknown", "score": 0, "reasons": ["Ephemeris not available"]}
        }
    
    positions = get_planet_positions(dt)
    aspects = find_aspects(positions)
    timing = market_timing_bias(positions, aspects)
    
    return {
        "datetime_utc": (dt or datetime.now(timezone.utc)).isoformat(),
        "positions": positions,
        "aspects": aspects,
        "timing": timing
    }
