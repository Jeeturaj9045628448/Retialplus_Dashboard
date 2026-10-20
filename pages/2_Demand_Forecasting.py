
from pathlib import Path
import zipfile

import pandas as pd
import streamlit as st


# ---------------- PAGE CONFIGURATION ----------------
st.set_page_config(
    page_title="RetailPulse | Demand Forecasting",
    page_icon="📈",
    layout="wide",
)

# Correct path when this file is inside the pages folder
APP_DIR = Path(__file__).resolve().parent
BASE_DIR = (
    APP_DIR.parent
    if APP_DIR.name.lower() == "pages"
    else APP_DIR
)

st.markdown(
    """
    <style>
    [data-testid="stSidebarNav"] {display: block;}
    .block-container {
        padding-top: 1.5rem;
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


# ---------------- FIND DATASET ----------------
def find_dataset():
    folders = [BASE_DIR, APP_DIR, BASE_DIR.parent]
    filenames = [
        "cleaned_sales_transactions.csv",
        "cleaned_sales_transactions.zip",
    ]

    for folder in folders:
        for filename in filenames:
            candidate = folder / filename
            if candidate.is_file():
                return candidate

    return None


@st.cache_data
def load_sales_data(path_string):
    path = Path(path_string)

    if path.suffix.lower() == ".zip":
        with zipfile.ZipFile(path, "r") as archive:
            csv_files = [
                name for name in archive.namelist()
                if name.lower().endswith(".csv")
                and not name.startswith("__MACOSX/")
            ]

            if not csv_files:
                raise ValueError(
                    "ZIP file ke andar koi CSV file nahi mili."
                )

            with archive.open(csv_files[0]) as file:
                return pd.read_csv(file)

    return pd.read_csv(path)


# ---------------- PAGE HEADER ----------------
st.title("📈 Demand Forecasting")
st.write("View future demand predictions for RetailPulse.")

st.subheader("Forecast Overview")

col1, col2 = st.columns(2)
col1.metric("Forecast Period", "30 Days")
col2.metric("Forecast Status", "Baseline Forecast")

st.info(
    "This page generates a simple baseline forecast using "
    "historical sales demand. LSTM, Prophet and Hybrid models "
    "are not connected in this version."
)


# ---------------- LOAD DATA ----------------
sales_path = find_dataset()

if sales_path is None:
    st.error(
        "Sales dataset nahi mili. "
        "cleaned_sales_transactions.csv ya "
        "cleaned_sales_transactions.zip ko GitHub repository "
        "ke root folder mein app.py ke saath rakho."
    )
    st.stop()

try:
    sales = load_sales_data(str(sales_path))
except Exception as exc:
    st.error(f"Sales dataset load nahi hui: {exc}")
    st.stop()

required_columns = {"date", "quantity"}
missing_columns = required_columns - set(sales.columns)

if missing_columns:
    st.error(
        "Dataset mein required columns missing hain: "
        + ", ".join(sorted(missing_columns))
    )
    st.stop()

sales["date"] = pd.to_datetime(
    sales["date"], errors="coerce"
)
sales["quantity"] = pd.to_numeric(
    sales["quantity"], errors="coerce"
)

sales = sales.dropna(
    subset=["date", "quantity"]
).copy()

if sales.empty:
    st.error("Dataset mein valid date ya quantity data nahi hai.")
    st.stop()

# Remove time component to create daily totals
sales["date"] = sales["date"].dt.normalize()


# ---------------- SIDEBAR FILTERS ----------------
with st.sidebar:
    st.header("🔎 Forecast Filters")

    min_date = sales["date"].min().date()
    max_date = sales["date"].max().date()

    date_range = st.date_input(
        "Historical Date Range",
        value=(min_date, max_date),
        min_value=min_date,
        max_value=max_date,
    )

    if "channel" in sales.columns:
        channels = sorted(
            sales["channel"].dropna().astype(str).unique()
        )
        selected_channels = st.multiselect(
            "Sales Channel",
            channels,
            default=channels,
        )
    else:
        selected_channels = None

    if "store_id" in sales.columns:
        stores = sorted(
            sales["store_id"].dropna().astype(str).unique()
        )
        selected_stores = st.multiselect(
            "Store",
            stores,
            default=stores,
        )
    else:
        selected_stores = None


# ---------------- APPLY FILTERS ----------------
filtered = sales.copy()

if isinstance(date_range, (tuple, list)) and len(date_range) == 2:
    start_date, end_date = date_range
    filtered = filtered[
        filtered["date"].dt.date.between(
            start_date, end_date
        )
    ]

if selected_channels is not None:
    filtered = filtered[
        filtered["channel"].astype(str).isin(
            selected_channels
        )
    ]

if selected_stores is not None:
    filtered = filtered[
        filtered["store_id"].astype(str).isin(
            selected_stores
        )
    ]

if filtered.empty:
    st.warning(
        "Selected filters ke liye data nahi mila. "
        "Date range, channel ya store change karke dekho."
    )
    st.stop()


# ---------------- HISTORICAL DATA ----------------
st.subheader("📊 Forecasting Data Overview")

col1, col2, col3 = st.columns(3)

col1.metric("Sales Records", f"{len(filtered):,}")
col2.metric(
    "Total Units Sold",
    f"{filtered['quantity'].sum():,.0f}",
)
col3.metric(
    "Historical Days",
    f"{filtered['date'].dt.date.nunique():,}",
)

st.success(f"Dataset loaded: {sales_path.name}")

st.subheader("Sales Dataset Preview")
st.dataframe(
    filtered.head(30),
    use_container_width=True,
)


# ---------------- DAILY DEMAND ----------------
st.subheader("📅 Daily Demand Overview")

daily_demand = (
    filtered.groupby("date", as_index=False)["quantity"]
    .sum()
    .rename(columns={"quantity": "demand"})
    .sort_values("date")
)

col1, col2 = st.columns(2)
col1.metric(
    "Total Historical Demand",
    f"{daily_demand['demand'].sum():,.0f} units",
)
col2.metric(
    "Average Daily Demand",
    f"{daily_demand['demand'].mean():,.1f} units",
)

st.line_chart(
    daily_demand.set_index("date")["demand"],
    x_label="Date",
    y_label="Units Sold",
)

st.dataframe(
    daily_demand.tail(30),
    use_container_width=True,
)


# ---------------- 30-DAY BASELINE FORECAST ----------------
st.subheader("🔮 30-Day Forecast Overview")

forecast_days = st.selectbox(
    "Forecast Period",
    [7, 14, 30, 60, 90],
    index=2,
)

# Use the latest 30 available daily observations
recent_demand = daily_demand["demand"].tail(30)
average_demand = float(recent_demand.mean())

last_date = daily_demand["date"].max()

future_dates = pd.date_range(
    start=last_date + pd.Timedelta(days=1),
    periods=forecast_days,
    freq="D",
)

forecast = pd.DataFrame({
    "date": future_dates,
    "forecast_demand": [max(0, round(average_demand, 2))]
    * forecast_days,
})

col1, col2, col3 = st.columns(3)

col1.metric(
    "Average Daily Forecast",
    f"{average_demand:,.1f} units",
)
col2.metric(
    "Forecast Period",
    f"{forecast_days} days",
)
col3.metric(
    "Total Forecast Demand",
    f"{forecast['forecast_demand'].sum():,.0f} units",
)

st.line_chart(
    forecast.set_index("date")["forecast_demand"],
    x_label="Date",
    y_label="Forecasted Units",
)

st.dataframe(forecast, use_container_width=True)


# ---------------- DEMAND SCENARIO ANALYSIS ----------------
st.subheader("🎯 Demand Scenario Analysis")

demand_change = st.slider(
    "Expected Demand Adjustment (%)",
    min_value=-30,
    max_value=30,
    value=0,
    step=5,
)

what_if_forecast = forecast.copy()

what_if_forecast["adjusted_demand"] = (
    what_if_forecast["forecast_demand"]
    * (1 + demand_change / 100)
).round(2)

col1, col2 = st.columns(2)

col1.metric(
    "Demand Adjustment",
    f"{demand_change:+d}%",
)

col2.metric(
    "Adjusted Total Demand",
    f"{what_if_forecast['adjusted_demand'].sum():,.0f} units",
)

st.line_chart(
    what_if_forecast.set_index("date")[
        ["forecast_demand", "adjusted_demand"]
    ],
    x_label="Date",
    y_label="Demand",
)

st.dataframe(
    what_if_forecast,
    use_container_width=True,
)


# ---------------- FORECAST SUMMARY ----------------
st.subheader("📌 Forecast Summary")

forecast_avg = forecast["forecast_demand"].mean()
forecast_min = forecast["forecast_demand"].min()
forecast_max = forecast["forecast_demand"].max()
forecast_total = forecast["forecast_demand"].sum()

col1, col2, col3 = st.columns(3)

col1.metric("Average Daily Demand", f"{forecast_avg:,.1f}")
col2.metric("Minimum Forecast", f"{forecast_min:,.1f}")
col3.metric("Maximum Forecast", f"{forecast_max:,.1f}")

st.write(
    f"Expected demand for the next {forecast_days} days: "
    f"**{forecast_total:,.0f} units**."
)

st.write(
    f"Average expected daily demand: "
    f"**{forecast_avg:,.1f} units**."
)

st.caption(
    "Forecast method: baseline average of the latest "
    "30 available daily observations. This is a simple "
    "estimate, not an LSTM, Prophet or Hybrid model prediction."
)
