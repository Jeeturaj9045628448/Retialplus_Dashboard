from pathlib import Path
from io import BytesIO
import streamlit as st
import pandas as pd
import altair as alt

st.set_page_config(
    page_title="RetailPulse AI Analytics Dashboard",
    page_icon="🚀",
    layout="wide",
    initial_sidebar_state="expanded",
)

BASE_PATH = Path(__file__).resolve().parent

def find_data_file(filename):
    for p in (BASE_PATH / filename, BASE_PATH.parent / filename):
        if p.is_file():
            return p
    return None

st.markdown("""
<style>
.block-container {padding-top: 1.5rem; padding-bottom: 2rem; max-width: 1550px;}
[data-testid="stSidebarNav"] {display:none;}
div[data-testid="stMetric"] {background:rgba(128,128,128,.07); padding:12px 14px; border-radius:10px;}
.rp-muted {color:#aab0bb; font-size:.92rem;}
</style>
""", unsafe_allow_html=True)

with st.sidebar:
    st.title("🛍️ RetailPulse")
    st.caption("Retail analytics and decision support")
    st.divider()
    st.page_link("app.py", label="Dashboard Overview", icon="🏠")
    st.page_link("pages/1_Sales_Analytics.py", label="Sales Analytics", icon="📊")
    st.page_link("pages/2_Demand_Forecasting.py", label="Demand Forecasting", icon="📈")
    st.page_link("pages/3_Customer_Segmentation.py", label="Customer Segmentation", icon="👥")
    st.page_link("pages/4_Inventory_Optimization.py", label="Inventory Optimization", icon="📦")

st.title("🚀 RetailPulse AI Analytics Platform")
st.write("Monitor retail performance, explore sales trends, and identify inventory risks.")

sales_path = find_data_file("cleaned_sales_transactions.zip")
if sales_path is None:
    sales_path = find_data_file("cleaned_sales_transactions.csv")
inventory_path = find_data_file("cleaned_inventory_snapshot.csv")

sales = None
inventory = None
if sales_path:
    try:
        if sales_path.suffix.lower() == ".zip":
            sales = pd.read_csv(sales_path, compression="zip")
        else:
            sales = pd.read_csv(sales_path)
        required = {"date", "receipt_id", "quantity", "total_value"}
        missing = required - set(sales.columns)
        if missing:
            st.error("Sales file missing required columns: " + ", ".join(sorted(missing)))
            sales = None
        else:
            sales["date"] = pd.to_datetime(sales["date"], errors="coerce")
            for col in ("quantity", "total_value"):
                sales[col] = pd.to_numeric(sales[col], errors="coerce").fillna(0)
            sales = sales.dropna(subset=["date"])
    except Exception as exc:
        st.error(f"Sales data could not be loaded: {exc}")
else:
    st.error("Sales data file not found. Put cleaned_sales_transactions.zip (or .csv) beside app.py in the repository root.")

if inventory_path:
    try:
        inventory = pd.read_csv(inventory_path)
        needed = {"stock_on_hand", "reorder_point"}
        if not needed.issubset(inventory.columns):
            st.warning("Inventory CSV must contain stock_on_hand and reorder_point columns.")
            inventory = None
    except Exception as exc:
        st.warning(f"Inventory data could not be loaded: {exc}")
else:
    st.warning("Inventory CSV not found. Inventory-related KPIs will show as unavailable until cleaned_inventory_snapshot.csv is added.")

if sales is None or sales.empty:
    st.info("The dashboard sections are ready, but metrics need a valid sales dataset.")
    st.stop()

latest_date = sales["date"].max()
latest_rows = sales.loc[sales["date"] == latest_date]
latest_sales = float(latest_rows["total_value"].sum())
units_sold = int(latest_rows["quantity"].sum())
orders_latest = int(latest_rows["receipt_id"].nunique())
total_sales = float(sales["total_value"].sum())
total_orders = int(sales["receipt_id"].nunique())

daily_sales = (
