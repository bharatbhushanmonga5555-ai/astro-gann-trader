"""
Gann Theory Module
Implements Square of 9, Gann levels, and basic angle calculations.
"""

import math
from typing import List, Dict, Tuple
import numpy as np


def square_of_nine_levels(price: float, levels: int = 8) -> Dict[str, List[float]]:
    """
    Calculate Gann Square of 9 support and resistance levels around a price.
    
    The Square of 9 is a spiral of numbers. We find the nearest numbers
    on the cardinal and ordinal crosses.
    """
    if price <= 0:
        return {"supports": [], "resistances": [], "center": price}
    
    # Find the root (square root of price)
    root = math.sqrt(price)
    
    supports = []
    resistances = []
    
    # Generate levels above and below
    for i in range(1, levels + 1):
        # Up levels (resistance)
        up_root = root + (i * 0.125)  # 1/8 increments common in Gann
        up_price = round(up_root ** 2, 2)
        resistances.append(up_price)
        
        # Down levels (support)
        down_root = root - (i * 0.125)
        if down_root > 0:
            down_price = round(down_root ** 2, 2)
            supports.append(down_price)
    
    # Also add classic 45-degree style jumps (full rotations approx)
    # One full rotation on Square of 9 is roughly +2 on the root for higher numbers
    for i in range(1, 5):
        res = round((root + i) ** 2, 2)
        sup = round((root - i) ** 2, 2) if (root - i) > 0 else None
        if res not in resistances:
            resistances.append(res)
        if sup and sup not in supports:
            supports.append(sup)
    
    supports = sorted([s for s in supports if s < price], reverse=True)[:levels]
    resistances = sorted([r for r in resistances if r > price])[:levels]
    
    return {
        "center": round(price, 2),
        "supports": supports,
        "resistances": resistances,
        "root": round(root, 4)
    }


def gann_angles(price: float, bars: int = 50, price_unit: float = None) -> Dict[str, float]:
    """
    Calculate classic Gann angle prices from a starting point.
    1x1 is the most important (45 degree).
    """
    if price_unit is None:
        # Auto scale: use 1% of price as unit roughly
        price_unit = price * 0.01 / 10  # rough
    
    angles = {
        "1x8": price + (bars * price_unit * 0.125),
        "1x4": price + (bars * price_unit * 0.25),
        "1x3": price + (bars * price_unit * 0.333),
        "1x2": price + (bars * price_unit * 0.5),
        "1x1": price + (bars * price_unit * 1.0),
        "2x1": price + (bars * price_unit * 2.0),
        "3x1": price + (bars * price_unit * 3.0),
        "4x1": price + (bars * price_unit * 4.0),
        "8x1": price + (bars * price_unit * 8.0),
    }
    
    # Also down angles
    down_angles = {f"down_{k}": price - (v - price) for k, v in angles.items()}
    
    return {**{k: round(v, 2) for k, v in angles.items()},
            **{k: round(v, 2) for k, v in down_angles.items()}}


def nearest_gann_level(price: float, levels_dict: Dict) -> Dict:
    """Find the nearest support and resistance from Square of 9."""
    supports = levels_dict.get("supports", [])
    resistances = levels_dict.get("resistances", [])
    
    nearest_sup = max([s for s in supports if s <= price], default=None)
    nearest_res = min([r for r in resistances if r >= price], default=None)
    
    dist_sup = round(price - nearest_sup, 2) if nearest_sup else None
    dist_res = round(nearest_res - price, 2) if nearest_res else None
    
    return {
        "nearest_support": nearest_sup,
        "nearest_resistance": nearest_res,
        "distance_to_support": dist_sup,
        "distance_to_resistance": dist_res,
        "at_support": dist_sup is not None and dist_sup / price < 0.003,  # within 0.3%
        "at_resistance": dist_res is not None and dist_res / price < 0.003
    }


def get_gann_analysis(price: float) -> Dict:
    """Full Gann analysis for a given price."""
    sq9 = square_of_nine_levels(price)
    nearest = nearest_gann_level(price, sq9)
    angles = gann_angles(price)
    
    return {
        "square_of_9": sq9,
        "nearest": nearest,
        "angles_sample": {k: angles[k] for k in ["1x1", "2x1", "1x2", "down_1x1", "down_2x1"]}
    }
