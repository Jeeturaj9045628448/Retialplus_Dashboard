from pathlib import Path
import streamlit as st
import pandas as pd
import altair as alt

st.set_page_config(page_title="RetailPulse AI Analytics Dashboard", page_icon="📊", layout="wide")

BASE_PATH = Path(__file__).resolve().parent

def find_data_file(filename):
    for candidate in (BASE_PATH / filename, BASE_PATH.parent / filename):
        if candidate.is_file():
            return candidate
    return None

# Hide Streamlit's automatic multipage menu so only the custom sidebar appears.
st.markdown("""
<style>
.block-container {padding-top: 1.6rem; padding-bottom: 2rem;}
[data-testid="stSidebarNav"] {display: none;}
div[data-testid="stMetric"] {background: rgba(128,128,128,0.08); padding: 14px; border-radius: 10px;}
</style>
""", unsafe_allow_html=True)

with st.sidebar:
    st.title("🛍️ RetailPulse")
    st.caption("Retail analytics and decision support")
    st.divider()
    st.page_link("app.py", label="Dashboard Home", icon="🏠")
    st.page_link("pages/1_Sales_Analytics.py", label="Sales Analytics", icon="📊")
    st.page_link("pages/2_Demand_Forecasting.py", label="Demand Forecasting", icon="📈")
    st.page_link("pages/3_Customer_Segmentation.py", label="Customer Segmentation", icon="👥")
    st.page_link("pages/4_Inventory_Optimization.py", label="Inventory Optimization", icon="📦")

st.title("🚀 RetailPulse AI Analytics Dashboard")
st.write("Monitor retail performance, explore sales trends, and identify inventory risks.")

sales_path = find_data_file("cleaned_sales_transactions.zip")
inventory_path = find_data_file("cleaned_inventory_snapshot.csv")
sales = None
inventory = None

if sales_path:
    try:
        sales = pd.read_csv(sales_path, compression="zip")
        required = {"date", "receipt_id", "quantity", "total_value"}
        missing = required - set(sales.columns)
        if missing:
            st.error("Sales data is missing required columns: " + ", ".join(sorted(missing)))
            sales = None
        else:
            sales["date"] = pd.to_datetime(sales["date"], errors="coerce")
            sales["quantity"] = pd.to_numeric(sales["quantity"], errors="coerce").fillna(0)
            sales["total_value"] = pd.to_numeric(sales["total_value"], errors="coerce").fillna(0)
            sales = sales.dropna(subset=["date"])
    except Exception as exc:
        st.error(f"Could not read the sales ZIP file: {exc}")
else:
    st.error("Could not find cleaned_sales_transactions.zip. Put it in the same root folder as app.py.")

if inventory_path:
    try:
        inventory = pd.read_csv(inventory_path)
        if not {"stock_on_hand", "reorder_point"}.issubset(inventory.columns):
            st.warning("Inventory file is missing stock_on_hand and/or reorder_point columns.")
            inventory = None
    except Exception as exc:
        st.warning(f"Inventory data could not be loaded: {exc}")
else:
    st.info("Inventory data file is optional for the home page. Add cleaned_inventory_snapshot.csv to enable inventory KPIs.")

if sales is None or sales.empty:
    st.warning("The dashboard layout loaded, but sales metrics need a valid sales data file.")
    st.stop()

latest_date = sales["date"].max()
latest_sales = sales.loc[sales["date"] == latest_date]
total_sales = float(sales["total_value"].sum())
latest_day_sales = float(latest_sales["total_value"].sum())
orders = int(sales["receipt_id"].nunique())
units = int(sales["quantity"].sum())

daily_sales = (
    sales.assign(Date=sales["date"].dt.date)
    .groupby("Date", as_index=False)["total_value"].sum()
    .rename(columns={"total_value": "Sales"})
)
average_daily_sales = float(daily_sales["Sales"].mean()) if not daily_sales.empty else 0.0
low_stock = None
if inventory is not None:
    stock = pd.to_numeric(inventory["stock_on_hand"], errors="coerce").fillna(0)
    reorder = pd.to_numeric(inventory["reorder_point"], errors="coerce").fillna(0)
    low_stock = int((stock <= reorder).sum())

st.subheader("📌 Business Overview")
k1, k2, k3, k4 = st.columns(4)
