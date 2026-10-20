
from pathlib import Path
import zipfile

import pandas as pd
import plotly.express as px
import streamlit as st

st.set_page_config(
    page_title="Sales Analytics",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)


# Correct repository path for files inside pages/
APP_DIR = Path(__file__).resolve().parent
BASE_DIR = APP_DIR.parent if APP_DIR.name.lower() == "pages" else APP_DIR

st.markdown(
    """
    <style>
    [data-testid="stSidebarNav"] {display: none;}
    .block-container {
        padding-top: 1.4rem;
        padding-bottom: 2rem;
        max-width: 1600px;
    }
    div[data-testid="stMetric"] {
        background: rgba(128,128,128,.07);
        padding: 12px 14px;
        border-radius: 10px;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

st.title("📊 Sales Analytics")
st.caption(
    "Explore sales performance with date, channel, store, product, and customer filters."
)


def find_file(*names):
    for folder in (BASE_DIR, APP_DIR, BASE_DIR.parent):
        for name in names:
            candidate = folder / name
            if candidate.is_file():
                return candidate
    return None


@st.cache_data
def load_sales(file_path):
    path = Path(file_path)

    if path.suffix.lower() == ".zip":
        with zipfile.ZipFile(path) as archive:
            csv_files = [
                name for name in archive.namelist()
                if name.lower().endswith(".csv")
                and not name.startswith("__MACOSX/")
            ]

            if not csv_files:
                raise ValueError("ZIP file ke andar koi CSV file nahi mili.")

            with archive.open(csv_files[0]) as csv_file:
                return pd.read_csv(csv_file)

    return pd.read_csv(path)


# Find sales dataset in the repository
sales_path = find_file(
    "cleaned_sales_transactions.zip",
    "cleaned_sales_transactions.csv"
)

customer_path = find_file(
    "cleaned_customer_master.csv",
    "customer_master.csv",
    "cleaned_customers.csv"
)

if sales_path is None:
    st.error(
        "Sales dataset nahi mili. "
        "cleaned_sales_transactions.zip ya "
        "cleaned_sales_transactions.csv ko app.py ke saath "
        "repository ke root folder mein rakho."
    )
    st.stop()

try:
    sales = load_sales(str(sales_path))
except Exception as exc:
    st.error(f"Sales dataset load nahi hui: {exc}")
    st.stop()


# Check required columns
required_columns = {
    "date",
    "receipt_id",
    "store_id",
    "sku_id",
    "customer_id",
    "quantity",
    "total_value",
    "channel",
    "discount_pct",
}

missing_columns = required_columns - set(sales.columns)

if missing_columns:
    st.error(
        "Dataset mein required columns missing hain: "
        + ", ".join(sorted(missing_columns))
    )
    st.stop()


# Clean sales data
sales["date"] = pd.to_datetime(sales["date"], errors="coerce")
sales = sales.dropna(subset=["date"]).copy()

if sales.empty:
    st.error("Dataset mein valid dates wala sales data nahi mila.")
    st.stop()

for column in ["quantity", "total_value", "discount_pct"]:
    sales[column] = pd.to_numeric(
        sales[column], errors="coerce"
    ).fillna(0)

for column in [
    "receipt_id",
    "store_id",
    "sku_id",
    "customer_id",
    "channel",
]:
    sales[column] = sales[column].fillna("Unknown").astype(str)


# Optional customer master data
if customer_path is not None:
    try:
        customers = pd.read_csv(customer_path)

        if (
            "customer_id" not in customers.columns
            and "cust_id" in customers.columns
        ):
            customers = customers.rename(
                columns={"cust_id": "customer_id"}
            )

        if "customer_id" in customers.columns:
            customers["customer_id"] = (
                customers["customer_id"].astype(str)
            )

            customer_columns = [
                "customer_id",
                "gender",
                "city",
                "age",
                "age_group",
                "customer_segment",
                "loyalty_segment",
                "preferred_channel",
            ]

            available_columns = [
                col for col in customer_columns
                if col in customers.columns
            ]

            if len(available_columns) > 1:
                sales = sales.merge(
                    customers[available_columns].drop_duplicates(
                        "customer_id"
                    ),
                    on="customer_id",
                    how="left",
                )

    except Exception as exc:
        st.warning(
            f"Customer master load nahi hui. "
            f"Demographic charts skip honge: {exc}"
        )


# Sidebar filters
with st.sidebar:
    st.header("🔎 Sales Filters")

    min_date = sales["date"].min().date()
    max_date = sales["date"].max().date()

    date_range = st.date_input(
        "Select Date Range",
        value=(min_date, max_date),
        min_value=min_date,
        max_value=max_date,
    )

    channels = sorted(sales["channel"].unique().tolist())

    selected_channels = st.multiselect(
        "Sales Channel",
        channels,
        default=channels,
    )

    stores = sorted(sales["store_id"].unique().tolist())

    selected_stores = st.multiselect(
        "Store",
        stores,
        default=stores,
    )


# Apply filters
filtered = sales.copy()

if isinstance(date_range, (tuple, list)) and len(date_range) == 2:
    start_date, end_date = date_range

    filtered = filtered[
        filtered["date"].dt.date.between(start_date, end_date)
    ]

filtered = filtered[
    filtered["channel"].isin(selected_channels)
]

filtered = filtered[
    filtered["store_id"].isin(selected_stores)
]


# Sales KPIs
st.subheader("📊 Filtered Sales Overview")

transactions = (
    filtered["receipt_id"].nunique()
    if not filtered.empty else 0
)

units_sold = (
    filtered["quantity"].sum()
    if not filtered.empty else 0
)

total_sales = (
    filtered["total_value"].sum()
    if not filtered.empty else 0
)

average_order_value = (
    total_sales / transactions if transactions else 0
)

col1, col2, col3, col4 = st.columns(4)

col1.metric("Transactions", f"{transactions:,}")
col2.metric("Units Sold", f"{units_sold:,.0f}")
col3.metric("Total Sales", f"₹{total_sales:,.2f}")
col4.metric("Average Order Value", f"₹{average_order_value:,.2f}")

if filtered.empty:
    st.warning(
        "Selected filters ke liye sales nahi mili. "
        "Date range, channel ya store change karke dekho."
    )
    st.stop()


# Sales by channel and store
chart1, chart2 = st.columns(2)

with chart1:
    st.subheader("🥧 Sales by Channel")

    channel_sales = (
        filtered.groupby("channel", as_index=False)["total_value"]
        .sum()
    )

    fig = px.pie(
        channel_sales,
        names="channel",
        values="total_value",
        title="Revenue Share by Channel",
    )

    st.plotly_chart(fig, use_container_width=True)

with chart2:
    st.subheader("🍩 Sales by Store")

    store_sales = (
        filtered.groupby("store_id", as_index=False)["total_value"]
        .sum()
        .nlargest(8, "total_value")
    )

    fig = px.pie(
        store_sales,
        names="store_id",
        values="total_value",
        hole=0.55,
        title="Revenue Share by Top 8 Stores",
    )

    st.plotly_chart(fig, use_container_width=True)


# Filtered data preview
st.subheader("📋 Filtered Sales Data")
st.dataframe(filtered.head(500), use_container_width=True)


# Daily sales trend
st.subheader("Daily Sales Trend")

daily_sales = (
    filtered.assign(day=filtered["date"].dt.date)
    .groupby("day", as_index=False)["total_value"]
    .sum()
)

fig = px.line(
    daily_sales,
    x="day",
    y="total_value",
    markers=True,
    title="Daily Sales",
)

st.plotly_chart(fig, use_container_width=True)


# Monthly sales trend
st.subheader("Monthly Sales Trend")

monthly_sales = (
    filtered.assign(
        month=filtered["date"].dt.to_period("M").astype(str)
    )
    .groupby("month", as_index=False)["total_value"]
    .sum()
)

fig = px.line(
    monthly_sales,
    x="month",
    y="total_value",
    markers=True,
    title="Monthly Sales",
)

st.plotly_chart(fig, use_container_width=True)
st.dataframe(monthly_sales, use_container_width=True)


# Top stores and products
col1, col2 = st.columns(2)

with col1:
    st.subheader("Top 10 Stores by Sales")

    top_stores = (
        filtered.groupby("store_id", as_index=False)["total_value"]
        .sum()
        .nlargest(10, "total_value")
    )

    fig = px.bar(
        top_stores,
        x="store_id",
        y="total_value",
        title="Top 10 Stores",
    )

    st.plotly_chart(fig, use_container_width=True)
    st.dataframe(top_stores, use_container_width=True)

with col2:
    st.subheader("Top 10 Products (SKU) by Sales")

    top_products = (
        filtered.groupby("sku_id", as_index=False)["total_value"]
        .sum()
        .nlargest(10, "total_value")
    )

    fig = px.bar(
        top_products,
        x="sku_id",
        y="total_value",
        title="Top 10 Products",
    )

    st.plotly_chart(fig, use_container_width=True)
    st.dataframe(top_products, use_container_width=True)


# Store-wise sales by channel
st.subheader("Store-wise Sales by Channel")

store_channel = filtered.pivot_table(
    index="store_id",
    columns="channel",
    values="total_value",
    aggfunc="sum",
    fill_value=0,
)

st.bar_chart(store_channel)
st.dataframe(store_channel, use_container_width=True)


# Sales by discount
col1, col2 = st.columns(2)

with col1:
    st.subheader("Sales by Discount Percentage")

    discount_sales = (
        filtered.groupby("discount_pct", as_index=False)["total_value"]
        .sum()
        .sort_values("discount_pct")
    )

    fig = px.bar(
        discount_sales,
        x="discount_pct",
        y="total_value",
        title="Sales by Discount",
    )

    st.plotly_chart(fig, use_container_width=True)

with col2:
    st.subheader("Sales by Quantity")

    quantity_sales = (
        filtered.groupby("quantity", as_index=False)["total_value"]
        .sum()
        .sort_values("quantity")
    )

    fig = px.bar(
        quantity_sales,
        x="quantity",
        y="total_value",
        title="Sales by Quantity",
    )

    st.plotly_chart(fig, use_container_width=True)


# Yearly sales
st.subheader("Sales by Year")

yearly_sales = (
    filtered.assign(year=filtered["date"].dt.year)
    .groupby("year", as_index=False)["total_value"]
    .sum()
)

fig = px.bar(
    yearly_sales,
    x="year",
    y="total_value",
    title="Yearly Sales",
)

st.plotly_chart(fig, use_container_width=True)
st.dataframe(yearly_sales, use_container_width=True)


# Top customers
st.subheader("Top 10 Customers by Sales")

top_customers = (
    filtered.groupby("customer_id", as_index=False)["total_value"]
    .sum()
    .nlargest(10, "total_value")
)

fig = px.bar(
    top_customers,
    x="customer_id",
    y="total_value",
    title="Top 10 Customers",
)

st.plotly_chart(fig, use_container_width=True)
st.dataframe(top_customers, use_container_width=True)


# Customer demographic charts, if the customer data is available
demographic_columns = [
    column
    for column in [
        "gender",
        "city",
        "age_group",
        "customer_segment",
        "loyalty_segment",
        "preferred_channel",
    ]
    if column in filtered.columns
]

if "age" in filtered.columns:
    filtered["age"] = pd.to_numeric(
        filtered["age"], errors="coerce"
    )

    if "age_group" not in filtered.columns:
        filtered["age_group"] = pd.cut(
            filtered["age"],
            bins=[0, 18, 25, 35, 45, 55, 65, 120],
            labels=[
                "0-18",
                "19-25",
                "26-35",
                "36-45",
                "46-55",
                "56-65",
                "66+",
            ],
        )

        demographic_columns.append("age_group")


if demographic_columns:
    st.header("👥 Customer Demographics")

    for column in dict.fromkeys(demographic_columns):
        chart_data = (
            filtered.dropna(subset=[column])
            .groupby(column, as_index=False)["total_value"]
            .sum()
            .sort_values("total_value", ascending=False)
        )

        if not chart_data.empty:
            title = column.replace("_", " ").title()
            st.subheader(f"Sales by {title}")

            fig = px.bar(
                chart_data,
                x=column,
                y="total_value",
                title=f"Sales by {title}",
            )

            st.plotly_chart(fig, use_container_width=True)

    # Combined demographic breakdowns
    combinations = [
        ("preferred_channel", "age_group"),
        ("city", "age_group"),
        ("gender", "age_group"),
        ("loyalty_segment", "age_group"),
        ("preferred_channel", "loyalty_segment"),
        ("gender", "loyalty_segment"),
        ("city", "loyalty_segment"),
        ("preferred_channel", "gender"),
        ("city", "preferred_channel"),
        ("city", "gender"),
        ("loyalty_segment", "gender"),
    ]

    for first, second in combinations:
        if first in filtered.columns and second in filtered.columns:
            combo_data = filtered.dropna(
                subset=[first, second]
            )

            summary = (
                combo_data.groupby(
                    [first, second],
                    as_index=False,
                    observed=True,
                )["total_value"]
                .sum()
            )

            if not summary.empty:
                first_name = first.replace("_", " ").title()
                second_name = second.replace("_", " ").title()

                st.subheader(
                    f"Sales by {first_name} & {second_name}"
                )

                fig = px.bar(
                    summary,
                    x=first,
                    y="total_value",
                    color=second,
                    barmode="group",
                    title=f"{first_name} & {second_name}",
                )

                st.plotly_chart(fig, use_container_width=True)

else:
    st.info(
        "Customer demographic charts ke liye "
        "cleaned_customer_master.csv mein customer_id aur "
        "demographic columns hone chahiye. "
        "Baaki sales charts available hain."
    )


st.caption(
    f"Sales data: {sales_path.name} · "
    f"Filtered rows: {len(filtered):,}"
)
