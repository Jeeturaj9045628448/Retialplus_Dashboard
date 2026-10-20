from __future__ import annotations

import numpy as np
import pandas as pd
import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
from sklearn.ensemble import RandomForestRegressor, RandomForestClassifier
from sklearn.metrics import mean_absolute_error, roc_auc_score
from sklearn.model_selection import train_test_split

st.set_page_config(
    page_title="RetailPulse | Retail Intelligence",
    page_icon="📈",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ---------- Styling ----------
st.markdown("""
<style>
:root { color-scheme: dark; }
.block-container { padding-top: 1.2rem; padding-bottom: 2.5rem; max-width: 1600px; }
[data-testid="stAppViewContainer"] { background: #0b0f17; }
[data-testid="stSidebar"] { background: #171b27; border-right: 1px solid #2a3140; }
[data-testid="stMetric"] {
  background: linear-gradient(145deg,#171e2c,#111722);
  border: 1px solid #293447; padding: 16px 18px; border-radius: 14px;
}
[data-testid="stMetricLabel"] { color: #aab7ca; }
[data-testid="stMetricValue"] { color: #f4f7fb; }
h1, h2, h3 { letter-spacing: -0.025em; }
.section-note { color:#9aa8bd; font-size:0.94rem; }
.hero {
  background: linear-gradient(115deg,#172a46,#172033 60%,#18243a);
  border: 1px solid #2c4568; border-radius: 18px;
  padding: 24px 26px; margin-bottom: 18px;
}
.hero p { color:#c3d0e3; margin-bottom:0; }
.pill {
  display:inline-block; padding:5px 10px; margin-right:6px;
  border-radius:999px; background:#203a35; color:#74e0b3;
  font-size:0.78rem; border:1px solid #2b6254;
}
div[data-testid="stPlotlyChart"] { border:1px solid #222c3c; border-radius:14px; padding:8px; background:#101620; }
hr { border-color:#283244; }
</style>
""", unsafe_allow_html=True)

# ---------- Reproducible demo data ----------
@st.cache_data
def make_data():
    rng = np.random.default_rng(42)
    dates = pd.date_range("2022-01-01", "2025-12-31", freq="D")
    products = [
        ("P001", "Beverages", 18.0), ("P002", "Snacks", 12.0),
        ("P003", "Household", 35.0), ("P004", "Personal Care", 28.0),
        ("P005", "Dairy", 8.0), ("P006", "Fresh Food", 22.0),
        ("P007", "Electronics", 250.0), ("P008", "Clothing", 90.0),
    ]
    rows = []
    for date in dates:
        season = 1 + 0.16 * np.sin(2 * np.pi * date.dayofyear / 365.25)
        weekend = 1.15 if date.dayofweek >= 5 else 1.0
        promo = 1.12 if date.day in (1, 15) else 1.0
        for idx, (pid, cat, price) in enumerate(products):
            qty = max(0, int(rng.poisson((18 + idx * 2) * season * weekend * promo)))
            rows.append((date, pid, cat, price, qty, qty * price,
                         f"ST{(date.dayofyear + idx) % 30 + 1:02d}",
                         ["In-Store", "Online", "Mobile App"][(date.dayofyear + idx) % 3]))
    sales = pd.DataFrame(rows, columns=[
        "date", "product_id", "category", "unit_price", "quantity",
        "sales", "store", "channel"
    ])

    n = 1000
    recency = rng.integers(1, 150, n)
    frequency = rng.integers(1, 45, n)
    monetary = np.round(frequency * rng.uniform(150, 1200, n), 2)
    churn = ((recency > 85) & (frequency < 12)).astype(int)
    customers = pd.DataFrame({
        "customer_id": [f"C{i:05d}" for i in range(1, n + 1)],
        "recency_days": recency,
        "frequency": frequency,
        "monetary": monetary,
        "churn": churn,
    })
    customers["segment"] = np.select(
        [customers.recency_days <= 30,
         customers.frequency >= 28,
         customers.recency_days >= 85],
        ["Recent / Active", "Loyal Customers", "At Risk"],
        default="Needs Nurturing"
    )
    return sales, customers
