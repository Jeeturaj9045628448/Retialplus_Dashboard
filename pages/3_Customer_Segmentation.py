
from pathlib import Path
import zipfile

import pandas as pd
import streamlit as st


# ---------------- PAGE CONFIGURATION ----------------
st.set_page_config(
    page_title="RetailPulse | Customer Segmentation",
    page_icon="👥",
    layout="wide",
)

# Correct repository path for a file inside pages/
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


# ---------------- FIND DATA FILES ----------------
def find_file(*filenames):
    folders = [BASE_DIR, APP_DIR, BASE_DIR.parent]

    for folder in folders:
        for filename in filenames:
            path = folder / filename
            if path.is_file():
                return path

    return None


@st.cache_data
def load_data(path_string):
    path = Path(path_string)

    if path.suffix.lower() == ".zip":
        with zipfile.ZipFile(path, "r") as archive:
            csv_files = [
                name
                for name in archive.namelist()
                if name.lower().endswith(".csv")
                and not name.startswith("__MACOSX/")
            ]

            if not csv_files:
                raise ValueError(
                    f"No CSV file found inside {path.name}"
                )

            with archive.open(csv_files[0]) as file:
                return pd.read_csv(file)

    return pd.read_csv(path)


# ---------------- PAGE HEADER ----------------
st.title("👥 Customer Segmentation")
st.write(
    "Explore customer behavior and purchasing patterns."
)


# ---------------- CUSTOMER DATA ----------------
customer_path = find_file(
    "cleaned_customer_master.csv",
    "customer_master.csv",
    "cleaned_customers.csv",
)

if customer_path is None:
    st.error(
        "Customer dataset nahi mili. Please "
        "cleaned_customer_master.csv ko GitHub repository "
        "ke root folder mein app.py ke saath upload karo."
    )
    st.stop()

try:
    customers = load_data(str(customer_path))
except Exception as exc:
    st.error(f"Customer dataset load nahi hui: {exc}")
    st.stop()


# Support either cust_id or customer_id
if "cust_id" not in customers.columns:
    if "customer_id" in customers.columns:
        customers = customers.rename(
            columns={"customer_id": "cust_id"}
        )
    else:
        st.error(
            "Customer dataset mein cust_id ya customer_id "
            "column nahi mila."
        )
        st.stop()

# Support a missing loyalty segment column
if "loyalty_segment" not in customers.columns:
    customers["loyalty_segment"] = "Unknown"

customers["cust_id"] = customers["cust_id"].astype(str)
customers["loyalty_segment"] = (
    customers["loyalty_segment"]
    .fillna("Unknown")
    .astype(str)
)


# ---------------- CUSTOMER OVERVIEW ----------------
st.subheader("📊 Customer Overview")

col1, col2, col3 = st.columns(3)

col1.metric(
    "Total Customers",
    f"{customers['cust_id'].nunique():,}",
)

col2.metric(
    "Customer Segments",
    f"{customers['loyalty_segment'].nunique():,}",
)

col3.metric(
    "Customer Records",
    f"{len(customers):,}",
)

st.success(
    f"Customer data loaded successfully: {customer_path.name}"
)

st.subheader("Customer Dataset Preview")
st.dataframe(
    customers.head(30),
    use_container_width=True,
)


# ---------------- CUSTOMER SEGMENTATION ----------------
st.subheader("Customer Segmentation")

segment_summary = (
    customers.groupby("loyalty_segment")
    .size()
    .reset_index(name="Customer Count")
    .sort_values("Customer Count", ascending=False)
)

segment_summary["Customer Percentage"] = (
    segment_summary["Customer Count"]
    / max(len(customers), 1)
    * 100
).round(2)

col1, col2 = st.columns(2)

with col1:
    st.dataframe(
        segment_summary,
        use_container_width=True,
    )

with col2:
    st.bar_chart(
        segment_summary.set_index("loyalty_segment")[
            "Customer Count"
        ],
        x_label="Customer Segment",
        y_label="Customer Count",
    )


# ---------------- LOAD SALES DATA ----------------
sales_path = find_file(
    "cleaned_sales_transactions.csv",
    "cleaned_sales_transactions.zip",
)

last_purchase = pd.DataFrame(
    columns=[
        "customer_id",
        "last_purchase_date",
        "days_since_purchase",
        "churn_risk",
    ]
)

if sales_path is None:
    st.warning(
        "Sales dataset nahi mili. Customer segmentation "
        "available hai, lekin churn analysis ke liye "
        "cleaned_sales_transactions.csv ya .zip ko "
        "repository ke root folder mein upload karo."
    )
else:
    try:
        sales_data = load_data(str(sales_path))

        required_sales_columns = {"customer_id", "date"}
        missing = required_sales_columns - set(sales_data.columns)

        if missing:
            st.warning(
                "Sales dataset mein required columns missing hain: "
                + ", ".join(sorted(missing))
            )
        else:
            sales_data["date"] = pd.to_datetime(
                sales_data["date"],
                errors="coerce",
            )
            sales_data["customer_id"] = (
                sales_data["customer_id"].astype(str)
            )

            sales_data = sales_data.dropna(subset=["date"])

            if not sales_data.empty:
                last_purchase = (
                    sales_data.groupby("customer_id")["date"]
                    .max()
                    .reset_index()
                )

                last_purchase.columns = [
                    "customer_id",
                    "last_purchase_date",
                ]

                analysis_date = sales_data["date"].max()

                last_purchase["days_since_purchase"] = (
                    analysis_date
                    - last_purchase["last_purchase_date"]
                ).dt.days

                last_purchase["churn_risk"] = pd.cut(
                    last_purchase["days_since_purchase"],
                    bins=[-1, 90, 180, float("inf")],
                    labels=["Low", "Medium", "High"],
                )

                st.success(
                    f"Sales data loaded successfully: {sales_path.name}"
                )

    except Exception as exc:
        st.warning(
            f"Sales data load nahi hui; churn analysis "
            f"available nahi hai. Details: {exc}"
        )


# ---------------- CHURN RISK ANALYSIS ----------------
st.subheader("⚠️ Churn Risk Analysis")

if last_purchase.empty:
    st.info(
        "Churn analysis ke liye valid sales dates aur "
        "customer_id wala sales dataset required hai."
    )
else:
    risk_summary = (
        last_purchase["churn_risk"]
        .value_counts()
        .reindex(["Low", "Medium", "High"], fill_value=0)
        .rename_axis("Churn Risk")
        .reset_index(name="Customer Count")
    )

    total_with_sales = len(last_purchase)

    risk_summary["Risk Percentage"] = (
        risk_summary["Customer Count"]
        / max(total_with_sales, 1)
        * 100
    ).round(2)

    col1, col2, col3 = st.columns(3)

    low_risk = int(
        risk_summary.loc[
            risk_summary["Churn Risk"] == "Low",
            "Customer Count",
        ].iloc[0]
    )
    medium_risk = int(
        risk_summary.loc[
            risk_summary["Churn Risk"] == "Medium",
            "Customer Count",
        ].iloc[0]
    )
    high_risk = int(
        risk_summary.loc[
            risk_summary["Churn Risk"] == "High",
            "Customer Count",
        ].iloc[0]
    )

    col1.metric("Low Risk Customers", f"{low_risk:,}")
    col2.metric("Medium Risk Customers", f"{medium_risk:,}")
    col3.metric("High Risk Customers", f"{high_risk:,}")

    chart_col1, chart_col2 = st.columns(2)

    with chart_col1:
        st.dataframe(
            risk_summary,
            use_container_width=True,
        )

    with chart_col2:
        st.bar_chart(
            risk_summary.set_index("Churn Risk")[
                "Customer Count"
            ],
            x_label="Churn Risk",
            y_label="Customer Count",
        )

    # ---------------- SEGMENT AND CHURN RISK ----------------
    st.subheader("Customer Segment and Churn Risk")

    customer_risk = customers[
        ["cust_id", "loyalty_segment"]
    ].copy()

    customer_risk = customer_risk.merge(
        last_purchase,
        left_on="cust_id",
        right_on="customer_id",
        how="left",
    )

    segment_risk_summary = (
        customer_risk.groupby(
            ["loyalty_segment", "churn_risk"],
            observed=True,
        )
        .size()
        .reset_index(name="Customer Count")
    )

    st.dataframe(
        segment_risk_summary,
        use_container_width=True,
    )

    if not segment_risk_summary.empty:
        segment_risk_chart = segment_risk_summary.pivot(
            index="loyalty_segment",
            columns="churn_risk",
            values="Customer Count",
        ).fillna(0)

        st.bar_chart(
            segment_risk_chart,
            x_label="Customer Segment",
            y_label="Customer Count",
        )

    # ---------------- AT-RISK CUSTOMER DETAILS ----------------
    st.subheader("Churn Risk Customer Details")

    risk_customers = customer_risk[
        customer_risk["churn_risk"].isin(["High", "Medium"])
    ][
        [
            "cust_id",
            "loyalty_segment",
            "last_purchase_date",
            "days_since_purchase",
            "churn_risk",
        ]
    ].copy()

    risk_customers = risk_customers.sort_values(
        "days_since_purchase",
        ascending=False,
    )

    st.dataframe(
        risk_customers.head(100),
        use_container_width=True,
    )

    # ---------------- CHURN SUMMARY ----------------
    st.subheader("Customer Risk Overview")

    st.bar_chart(
        risk_summary.set_index("Churn Risk")[
            "Risk Percentage"
        ],
        x_label="Churn Risk",
        y_label="Customer Percentage",
    )


# ---------------- CUSTOMER ANALYTICS SUMMARY ----------------
st.subheader("📌 Customer Analytics Summary")

col1, col2, col3 = st.columns(3)

col1.metric(
    "Total Customers",
    f"{customers['cust_id'].nunique():,}",
)

col2.metric(
    "Customer Segments",
    f"{customers['loyalty_segment'].nunique():,}",
)

if not last_purchase.empty:
    col3.metric(
        "High Risk Customers",
        f"{high_risk:,}",
    )
else:
    col3.metric("High Risk Customers", "N/A")

st.write(
    f"Total customer base analyzed: "
    f"**{customers['cust_id'].nunique():,} customers**."
)

st.write(
    f"Customer base is divided into "
    f"**{customers['loyalty_segment'].nunique():,} loyalty segments**."
)

if not last_purchase.empty:
    st.write(
        f"High churn risk customers identified: **{high_risk:,}**."
    )
    st.write(
        f"Medium churn risk customers identified: **{medium_risk:,}**."
    )

st.info(
    "Customer segmentation and churn-risk analysis can support "
    "targeted retention and customer engagement decisions. "
    "Churn risk here is estimated from days since the latest "
    "recorded purchase; it is not a trained prediction model."
)
