"""
Astro-Gann-Numerology Trading Research Tool
===========================================
Free educational prototype combining:
- Vedic Astrology (Swiss Ephemeris)
- Numerology
- Gann Square of 9 + levels
- Simple confluence signals for Call / Put

Supported: Nifty, BankNifty, Gold, Crude Oil, Natural Gas

Disclaimer: This is for research & educational purposes only.
Not financial advice. Past performance is not indicative of future results.
Always do your own due diligence and risk management.
"""

import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from datetime import datetime, timezone
import sys
import os

# Robust path for Streamlit Cloud + local
CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
if CURRENT_DIR not in sys.path:
    sys.path.insert(0, CURRENT_DIR)

try:
    from modules.data_fetcher import get_latest_price, get_multi_prices, fetch_price_data, SYMBOLS
    from modules.signals import generate_signal, batch_signals
    from modules.astrology import get_astrology_analysis, HAS_SWISSEPH
    from modules.gann import get_gann_analysis
    from modules.numerology import get_numerology_analysis
except ModuleNotFoundError as e:
    st.error(f"Module import error: {e}")
    st.error("Please make sure the 'modules' folder is uploaded correctly on GitHub.")
    st.stop()

# Page config - mobile friendly
st.set_page_config(
    page_title="Astro Gann Trader",
    page_icon="📈",
    layout="centered",          # better for mobile
    initial_sidebar_state="collapsed"  # sidebar closed by default on mobile
)

# Custom CSS - Mobile Optimized
st.markdown("""
<style>
    /* Base */
    .main-header {
        font-size: 1.6rem;
        font-weight: 700;
        color: #1f77b4;
        text-align: center;
        margin-bottom: 0.3rem;
        line-height: 1.3;
    }
    .sub-header {
        text-align: center;
        color: #666;
        font-size: 0.85rem;
        margin-bottom: 1.2rem;
    }
    
    /* Signal cards - mobile first */
    .signal-box {
        padding: 1rem;
        border-radius: 12px;
        margin: 0.6rem 0;
        box-shadow: 0 2px 6px rgba(0,0,0,0.08);
    }
    .call {
        background: linear-gradient(135deg, #d4edda, #c3e6cb);
        border-left: 6px solid #28a745;
    }
    .put {
        background: linear-gradient(135deg, #f8d7da, #f5c6cb);
        border-left: 6px solid #dc3545;
    }
    .wait {
        background: linear-gradient(135deg, #fff3cd, #ffeeba);
        border-left: 6px solid #ffc107;
    }
    
    .signal-box h3 {
        margin: 0 0 0.3rem 0;
        font-size: 1.1rem;
    }
    .signal-box h2 {
        margin: 0.2rem 0;
        font-size: 1.5rem;
    }
    .signal-box h4 {
        margin: 0.4rem 0;
        font-size: 1.15rem;
    }
    
    /* Better touch targets */
    .stButton > button {
        width: 100%;
        padding: 0.7rem;
        font-size: 1rem;
        border-radius: 8px;
    }
    
    /* Reduce padding on mobile */
    @media (max-width: 768px) {
        .main-header { font-size: 1.4rem; }
        .block-container { padding-top: 1rem; padding-bottom: 1rem; }
        [data-testid="stSidebar"] { width: 80vw !important; }
    }
    
    /* Hide Streamlit branding a bit cleaner */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
</style>
""", unsafe_allow_html=True)


def color_action(action: str) -> str:
    if "CALL" in action.upper():
        return "call"
    elif "PUT" in action.upper():
        return "put"
    return "wait"


def main():
    st.markdown('<div class="main-header">📈 Astro + Gann + Numerology Trader</div>', unsafe_allow_html=True)
    st.markdown('<div class="sub-header">Research Tool for Nifty • BankNifty • Gold • Crude • Natural Gas</div>', unsafe_allow_html=True)
    
    # Sidebar
    st.sidebar.title("⚙️ Settings")
    
    instruments = st.sidebar.multiselect(
        "Select Instruments",
        options=["NIFTY", "BANKNIFTY", "GOLD", "CRUDEOIL", "NATURALGAS"],
        default=["NIFTY", "BANKNIFTY", "GOLD"]
    )
    
    st.sidebar.markdown("---")
    st.sidebar.info(
        "**Note:** Free data via Yahoo Finance.\n\n"
        "Indian F&O real-time data is limited.\n"
        "For live trading use paid data (TrueData etc)."
    )
    
    if not HAS_SWISSEPH:
        st.sidebar.error("⚠️ pyswisseph not installed.\nAstrology features limited.\nRun: pip install pyswisseph")
    
    # Manual price override
    st.sidebar.markdown("### Manual Price Override")
    use_manual = st.sidebar.checkbox("Use manual prices (if data fails)")
    manual_prices = {}
    if use_manual:
        for inst in instruments:
            manual_prices[inst] = st.sidebar.number_input(f"{inst} Price", min_value=0.0, value=0.0, step=0.1)
    
    # Main content
    tab1, tab2, tab3, tab4 = st.tabs(["🎯 Live Signals", "🌌 Astrology", "🔢 Numerology + Gann", "📊 Charts"])
    
    # ========== TAB 1: Live Signals ==========
    with tab1:
        st.subheader("Confluence Signals (Call / Put)")
        
        if st.button("🔄 Refresh All Signals", type="primary"):
            st.rerun()
        
        prices = {}
        if use_manual:
            prices = {k: v for k, v in manual_prices.items() if v > 0}
        else:
            with st.spinner("Fetching latest prices..."):
                prices = get_multi_prices(instruments)
        
        if not prices or all(v is None for v in prices.values()):
            st.warning("Could not fetch prices. Enable **Manual Price Override** in sidebar (☰ menu) and enter prices.")
        else:
            # Mobile-friendly: show one card after another (vertical)
            for sym, price in prices.items():
                if price is None:
                    continue
                    
                signal = generate_signal(price, sym)
                action = signal["action"]
                css_class = color_action(action)
                
                st.markdown(f"""
                <div class="signal-box {css_class}">
                    <h3>{sym}</h3>
                    <h2>{price:,.2f}</h2>
                    <h4>{action}</h4>
                    <p><b>Bias:</b> {signal['bias']} &nbsp;|&nbsp; <b>Confidence:</b> {signal['confidence']}%</p>
                </div>
                """, unsafe_allow_html=True)
                
                with st.expander(f"📋 {sym} Details"):
                    st.write("**Reasons:**")
                    for r in signal["reasons"]:
                        st.write(f"- {r}")
                    
                    gann = signal["details"]["gann"]
                    st.write(f"**Nearest Support:** {gann.get('nearest_support')}")
                    st.write(f"**Nearest Resistance:** {gann.get('nearest_resistance')}")
                    st.write("**Gann Supports:**", gann.get("all_supports"))
                    st.write("**Gann Resistances:**", gann.get("all_resistances"))
    
    # ========== TAB 2: Astrology ==========
    with tab2:
        st.subheader("Current Planetary Snapshot (Sidereal / Lahiri)")
        
        if HAS_SWISSEPH:
            astro = get_astrology_analysis()
            
            col1, col2 = st.columns(2)
            
            with col1:
                st.markdown("### Planetary Positions")
                pos_data = []
                for planet, data in astro.get("positions", {}).items():
                    if "sign" in data:
                        retro = "℞" if data.get("retrograde") else ""
                        pos_data.append({
                            "Planet": f"{planet} {retro}",
                            "Sign": data["sign"],
                            "Degree": f"{data['degree']}°",
                            "Longitude": data["longitude"]
                        })
                if pos_data:
                    st.dataframe(pd.DataFrame(pos_data), use_container_width=True)
            
            with col2:
                st.markdown("### Major Aspects")
                aspects = astro.get("aspects", [])
                if aspects:
                    asp_df = pd.DataFrame(aspects)
                    st.dataframe(asp_df, use_container_width=True)
                else:
                    st.info("No major aspects within orb right now.")
            
            timing = astro.get("timing", {})
            st.markdown("### Market Timing Bias (Rule-based)")
            st.metric("Bias", timing.get("bias", "N/A"), delta=f"Score: {timing.get('score', 0)}")
            st.write("**Reasons:**")
            for r in timing.get("reasons", []):
                st.write(f"- {r}")
        else:
            st.error("Swiss Ephemeris (pyswisseph) is required for astrology features.")
            st.code("pip install pyswisseph")
    
    # ========== TAB 3: Numerology + Gann ==========
    with tab3:
        st.subheader("Numerology & Gann Detailed Analysis")
        
        selected = st.selectbox("Choose Instrument", instruments or ["NIFTY"])
        
        price = None
        if use_manual and selected in manual_prices and manual_prices[selected] > 0:
            price = manual_prices[selected]
        else:
            price = get_latest_price(selected)
        
        if price:
            col1, col2 = st.columns(2)
            
            with col1:
                st.markdown("### 🔢 Numerology")
                num = get_numerology_analysis(price)
                st.write(f"**Day Number:** {num['date']['day_number']}")
                st.write(f"**Destiny Number:** {num['date']['destiny_number']}")
                st.write(f"**Price Number:** {num['price']['price_number']}")
                st.write(f"**Compound Bias:** {num['compound']['bias']} (Score: {num['compound']['score']})")
                st.write("**Reasons:**")
                for r in num['compound']['reasons']:
                    st.write(f"- {r}")
            
            with col2:
                st.markdown("### 📐 Gann Square of 9")
                gann = get_gann_analysis(price)
                nearest = gann["nearest"]
                
                st.metric("Current Price", f"{price:,.2f}")
                st.write(f"**Nearest Support:** {nearest.get('nearest_support')}")
                st.write(f"**Nearest Resistance:** {nearest.get('nearest_resistance')}")
                
                st.write("**Support Levels:**")
                st.write(gann["square_of_9"]["supports"])
                
                st.write("**Resistance Levels:**")
                st.write(gann["square_of_9"]["resistances"])
        else:
            st.warning("Price not available. Use manual override.")
    
    # ========== TAB 4: Charts ==========
    with tab4:
        st.subheader("Price Chart with Gann Levels")
        
        chart_sym = st.selectbox("Chart Instrument", instruments or ["NIFTY"], key="chart_sym")
        
        df = fetch_price_data(chart_sym, period="5d", interval="15m")
        
        if df is not None and not df.empty:
            price = float(df["close"].iloc[-1])
            gann = get_gann_analysis(price)
            
            fig = go.Figure()
            
            fig.add_trace(go.Candlestick(
                x=df["datetime"] if "datetime" in df.columns else df.index,
                open=df["open"],
                high=df["high"],
                low=df["low"],
                close=df["close"],
                name="Price"
            ))
            
            # Add Gann levels
            for level in gann["square_of_9"]["supports"][:4]:
                fig.add_hline(y=level, line_dash="dot", line_color="green", 
                              annotation_text=f"S {level}", annotation_position="bottom left")
            
            for level in gann["square_of_9"]["resistances"][:4]:
                fig.add_hline(y=level, line_dash="dot", line_color="red",
                              annotation_text=f"R {level}", annotation_position="top left")
            
            fig.update_layout(
                title=f"{chart_sym} with Gann Square of 9 Levels",
                xaxis_title="Time",
                yaxis_title="Price",
                height=600,
                xaxis_rangeslider_visible=False
            )
            
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.warning("Chart data not available for this symbol via free source.")
    
    # Footer
    st.markdown("---")
    st.caption("""
    **Disclaimer:** This tool is strictly for educational and research purposes. 
    Astrology, Numerology and Gann methods are not scientifically proven to predict markets.
    Trading in F&O involves substantial risk of loss. 
    Consult a SEBI registered advisor before taking any trading decisions.
    """)


if __name__ == "__main__":
    main()
