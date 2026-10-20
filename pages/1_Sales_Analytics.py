

# Step 24: Sales Analytics with Real Metrics

import streamlit as st
import pandas as pd
from pathlib import Path

st.title("Sales Analytics")

#BASE_PATH = Path(
  #  r"C:\Users\milan\Downloads\archive (3)\retail_clean_dataset"
#)

BASE_PATH = Path(__file__).resolve().parent.parent



sales_path = BASE_PATH / "cleaned_sales_transactions.zip"
customer_path = BASE_PATH / "cleaned_customer_master.csv"

@st.cache_data
def load_sales(path):
    # The ZIP in the repository contains cleaned_sales_transactions.csv.
    return pd.read_csv(path, compression="zip")

if not sales_path.is_file():
    st.error(f"Sales dataset not found: {sales_path}")
    st.info("Make sure cleaned_sales_transactions.zip is in the repository root (the same level as app.py).")
    st.stop()

try:
    sales = load_sales(sales_path)
except Exception as exc:
    st.error("Could not read cleaned_sales_transactions.zip. Upload a valid ZIP containing the sales CSV.")
    st.exception(exc)
    st.stop()

required_sales_columns = [
    "date", "receipt_id", "store_id", "sku_id", "customer_id",
    "quantity", "total_value", "channel", "discount_pct"
]
missing_sales_columns = [column for column in required_sales_columns if column not in sales.columns]
if missing_sales_columns:
    st.error(f"Sales dataset is missing required columns: {', '.join(missing_sales_columns)}")
    st.stop()

sales["date"] = pd.to_datetime(sales["date"], errors="coerce")
sales["total_value"] = pd.to_numeric(sales["total_value"], errors="coerce").fillna(0)
sales["quantity"] = pd.to_numeric(sales["quantity"], errors="coerce").fillna(0)

if sales.empty:
    st.error("The sales dataset is empty.")
    st.stop()

total_sales = sales["total_value"].sum()
total_transactions = sales["receipt_id"].nunique()
average_order_value = (
    sales.groupby("receipt_id")["total_value"].sum().mean()
)

col1, col2, col3 = st.columns(3)

col1.metric("Total Sales", f"₹{total_sales:,.2f}")
col2.metric("Total Orders", f"{total_transactions:,}")
col3.metric("Average Order Value", f"₹{average_order_value:,.2f}")

st.subheader("Sales Dataset Preview")
st.dataframe(sales.head(100), width="stretch")


# Step 26: Daily Sales Trend

st.subheader("Daily Sales Trend")

sales["date"] = pd.to_datetime(sales["date"])

daily_sales = (
    sales.groupby("date")["total_value"]
    .sum()
    .reset_index()
    .sort_values("date")
)

st.line_chart(
    daily_sales.set_index("date")["total_value"],
    x_label="Date",
    y_label="Sales Value"
)


# Step 28: Sales by Channel

st.subheader("Sales by Channel")

channel_sales = (
