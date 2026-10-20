import plotly.express as px
from pathlib import Path
import pandas as pd
import streamlit as st


st.set_page_config(
    page_title="RetailPulse | Sales Analytics",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded",
)
# Keep Streamlit's multipage navigation visible even if older CSS hid it.
st.markdown(
    """<style>
    [data-testid="stSidebarNav"] { display: block !important; visibility: visible !important; }
    [data-testid="stSidebar"] { display: block !important; }
    </style>""",
    unsafe_allow_html=True,
)

st.title("📊 Sales Analytics")

#BASE_PATH = Path(
  #  r"C:\Users\milan\Downloads\archive (3)\retail_clean_dataset"
#)

# Streamlit Cloud layout: repository root / app.py and repository root / pages / this file
APP_DIR = Path(__file__).resolve().parent
BASE_PATH = APP_DIR.parent if APP_DIR.name.lower() == "pages" else APP_DIR

def find_data_file(*names):
    candidates = []
    for name in names:
        candidates.extend([
            BASE_PATH / name,
            APP_DIR / name,
            BASE_PATH.parent / name,
        ])
    for candidate in candidates:
        if candidate.is_file():
            return candidate
    return None

sales_path = find_data_file(
    "cleaned_sales_transactions.zip",
    "cleaned_sales_transactions.csv",
)

@st.cache_data
def load_sales(path_string):
    path = Path(path_string)
    if path.suffix.lower() == ".zip":
        return pd.read_csv(path, compression="zip")
    return pd.read_csv(path)

if sales_path is None:
    st.error(
        "Sales dataset not found. Upload cleaned_sales_transactions.zip "
        "or cleaned_sales_transactions.csv to the repository root "
        "(the same folder as app.py)."
    )
    st.stop()

try:
    sales = load_sales(str(sales_path))
except Exception as exc:
    st.error(f"Could not load the sales dataset: {exc}")
    st.stop()

required_columns = {
    "date", "receipt_id", "store_id", "sku_id", "customer_id",
    "quantity", "total_value", "channel", "discount_pct"
}
missing_columns = required_columns.difference(sales.columns)
if missing_columns:
    st.error("Sales dataset is missing columns: " + ", ".join(sorted(missing_columns)))
    st.stop()

for column in ["quantity", "total_value", "discount_pct"]:
    sales[column] = pd.to_numeric(sales[column], errors="coerce").fillna(0)

for column in ["store_id", "sku_id", "customer_id", "channel"]:
    sales[column] = sales[column].fillna("Unknown").astype(str)



# ---------------- SALES FILTERS ----------------
st.sidebar.header("🔎 Sales Filters")

sales["date"] = pd.to_datetime(sales["date"], errors="coerce")
sales = sales.dropna(subset=["date"])

# Date filter
min_date = sales["date"].min().date()
max_date = sales["date"].max().date()
