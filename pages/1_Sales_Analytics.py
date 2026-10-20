from pathlib import Path
import streamlit as st
import pandas as pd
import altair as alt

st.set_page_config(page_title="RetailPulse | Sales Analytics", page_icon="📊", layout="wide")

BASE_PATH = Path(__file__).resolve().parent.parent

def find_file(name):
    for p in (BASE_PATH / name, BASE_PATH.parent / name, Path(__file__).resolve().parent / name):
        if p.is_file():
            return p
    return None

@st.cache_data
def load_csv_or_zip(path_string):
    path = Path(path_string)
    if path.suffix.lower() == ".zip":
        return pd.read_csv(path, compression="zip")
    return pd.read_csv(path)

@st.cache_data
def load_customer(path_string):
    return pd.read_csv(path_string)

st.markdown("""
<style>
[data-testid="stSidebarNav"] {display:none;}
.block-container {padding-top:1.5rem; padding-bottom:2rem; max-width:1600px;}
div[data-testid="stMetric"] {background:rgba(128,128,128,.07); padding:12px 14px; border-radius:10px;}
</style>
""", unsafe_allow_html=True)

st.title("📊 Sales Analytics")
st.caption("Explore sales performance with date, channel, store, product, and customer filters.")

sales_path = find_file("cleaned_sales_transactions.zip") or find_file("cleaned_sales_transactions.csv")
customer_path = find_file("cleaned_customer_master.csv")

if sales_path is None:
    st.error("Sales dataset not found. Put cleaned_sales_transactions.zip in the repository root, at the same level as app.py.")
    st.stop()

try:
    sales = load_csv_or_zip(str(sales_path))
except Exception as exc:
    st.error(f"Could not load sales dataset: {exc}")
    st.stop()

required = {"date", "receipt_id", "store_id", "sku_id", "customer_id", "quantity", "total_value", "channel", "discount_pct"}
missing = required - set(sales.columns)
if missing:
    st.error("Sales dataset is missing columns: " + ", ".join(sorted(missing)))
    st.stop()

sales["date"] = pd.to_datetime(sales["date"], errors="coerce")
for col in ["quantity", "total_value", "discount_pct"]:
    sales[col] = pd.to_numeric(sales[col], errors="coerce").fillna(0)
sales = sales.dropna(subset=["date"])
sales["channel"] = sales["channel"].fillna("Unknown").astype(str)
sales["store_id"] = sales["store_id"].fillna("Unknown").astype(str)
sales["sku_id"] = sales["sku_id"].fillna("Unknown").astype(str)
sales["customer_id"] = sales["customer_id"].fillna("Unknown").astype(str)

customers = None
if customer_path is not None:
    try:
        customers = load_customer(str(customer_path))
    except Exception:
        customers = None

# Merge optional customer attributes for the demographic charts.
if customers is not None and "customer_id" in customers.columns:
    customers["customer_id"] = customers["customer_id"].astype(str)
    sales["customer_id"] = sales["customer_id"].astype(str)
    customer_cols = [c for c in ["customer_id", "gender", "city", "age", "age_group", "customer_segment", "loyalty_segment", "preferred_channel"] if c in customers.columns]
    if len(customer_cols) > 1:
        sales = sales.merge(customers[customer_cols].drop_duplicates("customer_id"), on="customer_id", how="left")

# Sidebar filters
with st.sidebar:
    st.markdown("## 🔎 Sales Filters")
    min_date = sales["date"].min().date()
    max_date = sales["date"].max().date()
    date_range = st.date_input("Select Date Range", value=(min_date, max_date), min_value=min_date, max_value=max_date)
    channels = sorted(sales["channel"].dropna().unique().tolist())
    selected_channels = st.multiselect("Sales Channel", channels, default=channels)
    stores = sorted(sales["store_id"].dropna().unique().tolist())
    selected_stores = st.multiselect("Store", stores, default=stores)

filtered = sales.copy()
if isinstance(date_range, (tuple, list)) and len(date_range) == 2:
    start_date, end_date = date_range
    filtered = filtered[filtered["date"].dt.date.between(start_date, end_date)]
if selected_channels:
