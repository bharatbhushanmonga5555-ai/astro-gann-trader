# Astro + Gann + Numerology Trading Research Tool

Yeh ek **free educational prototype** hai jo combine karta hai:

- **Vedic Astrology** (Swiss Ephemeris - planetary positions, aspects, timing bias)
- **Numerology** (Date + Price numbers)
- **Gann Theory** (Square of 9 Support/Resistance levels)
- **Confluence Signals** → Call Buy / Put Buy / Wait

Supported instruments: **Nifty, BankNifty, Gold, Crude Oil, Natural Gas**

---

## ⚠️ Important Disclaimer

Yeh tool **sirf research aur educational purpose** ke liye hai.  
Yeh financial advice nahi hai. Markets unpredictable hote hain.  
F&O trading mein loss ka risk hota hai. Apna research karo aur SEBI registered advisor se baat karo.

---

## Installation (Windows / Mac / Linux)

### Step 1: Python install karo (3.9 ya usse upar)
https://www.python.org/downloads/

### Step 2: Project folder mein jao
```bash
cd astro_gann_trader
```

### Step 3: Virtual environment banao (recommended)
```bash
python -m venv venv

# Windows
venv\Scripts\activate

# Mac/Linux
source venv/bin/activate
```

### Step 4: Libraries install karo
```bash
pip install -r requirements.txt
```

**Note:** `pyswisseph` install karte time kabhi-kabhi issue aata hai.  
Agar fail ho to:
```bash
pip install pyswisseph --no-cache-dir
```

### Step 5: Software chalao
```bash
streamlit run app.py
```

Browser automatically khul jayega (http://localhost:8501)

---

## Features

| Feature              | Description                                      |
|----------------------|--------------------------------------------------|
| Live Signals         | Call / Put / Wait with confidence %              |
| Astrology Tab        | Sidereal positions + major aspects + bias        |
| Numerology           | Day number, Price number, compound score         |
| Gann Square of 9     | Automatic Support & Resistance levels            |
| Charts               | Candlestick + Gann levels overlay                |
| Manual Price         | Agar free data fail ho to manually price daalo   |

---

## Limitations (Free Version)

1. **Market Data**: Yahoo Finance se aata hai. Indian F&O (especially options) limited hai.
2. Real-time tick data nahi hai.
3. Options chain / Greeks nahi hain.
4. Backtesting engine abhi basic hai.

**Production ke liye** TrueData, Global Datafeeds ya broker API (Zerodha/Angel) connect karna padega.

---

## Folder Structure

```
astro_gann_trader/
├── app.py                 # Main Streamlit application
├── requirements.txt
├── README.md
└── modules/
    ├── astrology.py       # Swiss Ephemeris + aspects
    ├── gann.py            # Square of 9 + levels
    ├── numerology.py      # Date & Price numerology
    ├── data_fetcher.py    # Price data (yfinance)
    └── signals.py         # Confluence engine
```

---

## Kaise Use Karein

1. Sidebar (☰ menu) se instruments select karo.
2. **Live Signals** tab mein dekho kaunsa Call/Put suggest ho raha hai.
3. Details mein reasons padho (Astrology + Gann + Numerology).
4. Gann levels ko Support/Resistance maan kar trade plan banao.
5. Sirf high confidence + multiple reasons match hone par trade socho.

---

## 📱 Mobile Par Kaise Chalayein (3 Easy Tarike)

### Tarika 1: Same WiFi pe (Sabse Simple)
1. Computer pe software chalao → `streamlit run app.py`
2. Terminal mein ek local URL dikhega jaise `http://192.168.x.x:8501`
3. Apne mobile ko **usi WiFi** se connect karo
4. Mobile browser (Chrome) mein woh IP address type karo
5. App mobile pe khul jayega

### Tarika 2: Free Online Link (Sabse Best - Recommended)
1. Free GitHub account banao
2. Is pure `astro_gann_trader` folder ko GitHub pe upload karo
3. https://share.streamlit.io pe jao aur login karo
4. Apna GitHub repo select karo → main file `app.py` choose karo
5. Deploy button dabao
6. Aapko ek permanent link milega (example: `https://yourname-astro-gann.streamlit.app`)
7. Yeh link mobile browser mein kholo — kabhi bhi, kahin se bhi chalega (data bhi lagta hai)

### Tarika 3: Android pe directly (Pydroid 3)
1. Play Store se **Pydroid 3** app install karo
2. Project files phone mein copy karo
3. Pydroid mein terminal se `pip install streamlit yfinance pyswisseph plotly pandas`
4. Phir `streamlit run app.py` chalao
(Thoda heavy hai phone ke liye, Tarika 1 ya 2 better rahega)

---

## Future Improvements (Aap add kar sakte ho)

- TrueData / Broker API integration
- Options chain + suggested strikes
- Personal birth chart timing
- Full backtesting module
- Telegram alerts
- More Gann tools (angles, cycles, hexagon)

---

Created for educational research. Trade responsibly.
