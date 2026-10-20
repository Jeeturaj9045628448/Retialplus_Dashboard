from pathlib import Path
import zipfile
import streamlit as st
import pandas as pd
import altair as alt

st.set_page_config(page_title="RetailPulse Dashboard", page_icon="📊", layout="wide")

# Find files relative to this app first. Streamlit Cloud runs app.py from the repo root.
BASE_PATH = Path(__file__).resolve().parent

def find_data_file(filename: str):
    candidates = [BASE_PATH / filename, BASE_PATH.parent / filename]
    for candidate in candidates:
        if candidate.is_file():
            return candidate
    return None

st.markdown("""
<style>
.block-container {padding-top: 1.5rem; padding-bottom: 2rem;}
[data-testid="stSidebarNav"] {display: none;}
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
load_warnings = []

if sales_path:
    try:
        sales = pd.read_csv(sales_path, compression="zip")
        required = {"date", "receipt_id", "quantity", "total_value"}
        missing = required - set(sales.columns)
        if missing:
            load_warnings.append("Sales file is missing columns: " + ", ".join(sorted(missing)))
            sales = None
        else:
            sales["date"] = pd.to_datetime(sales["date"], errors="coerce")
            sales["quantity"] = pd.to_numeric(sales["quantity"], errors="coerce").fillna(0)
            sales["total_value"] = pd.to_numeric(sales["total_value"], errors="coerce").fillna(0)
            sales = sales.dropna(subset=["date"])
    except Exception as exc:
        load_warnings.append(f"Sales data could not be loaded: {exc}")
else:
    load_warnings.append("`cleaned_sales_transactions.zip` was not found in the repository root.")

if inventory_path:
    try:
        inventory = pd.read_csv(inventory_path)
        needed = {"stock_on_hand", "reorder_point"}
        if not needed.issubset(inventory.columns):
            load_warnings.append("Inventory CSV must contain stock_on_hand and reorder_point columns.")
            inventory = None
    except Exception as exc:
        load_warnings.append(f"Inventory data could not be loaded: {exc}")
else:
    load_warnings.append("Optional inventory file `cleaned_inventory_snapshot.csv` was not found; inventory KPIs will show as unavailable.")

if sales is not None and not sales.empty:
    latest_date = sales["date"].max()
    latest_sales = sales.loc[sales["date"] == latest_date]
    total_sales = float(sales["total_value"].sum())
    latest_day_sales = float(latest_sales["total_value"].sum())
    orders = int(sales["receipt_id"].nunique())
    units = int(sales["quantity"].sum())
    daily_sales = (
        sales.assign(Date=sales["date"].dt.date)
        .groupby("Date", as_index=False)["total_value"]
        .sum()
        .rename(columns={"total_value": "Sales"})
    )
    avg_daily = float(daily_sales["Sales"].mean()) if not daily_sales.empty else 0.0
    low_stock = None
    if inventory is not None and {"stock_on_hand", "reorder_point"}.issubset(inventory.columns):
        low_stock = int((pd.to_numeric(inventory["stock_on_hand"], errors="coerce").fillna(0) <= pd.to_numeric(inventory["reorder_point"], errors="coerce").fillna(0)).sum())

    a, b, c, d = st.columns(4)
    a.metric("Total Sales", f"₹{total_sales:,.0f}")
    b.metric("Orders", f"{orders:,}")
