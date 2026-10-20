
# Day 18 - Inventory Optimization Dashboard

import streamlit as st
import pandas as pd
from pathlib import Path

# --------------------------------------------------
# PAGE CONFIGURATION
# --------------------------------------------------
st.set_page_config(
    page_title="Inventory Optimization",
    page_icon="📦",
    layout="wide",
    initial_sidebar_state="expanded"
)

st.title("📦 Inventory Optimization")
st.write("Monitor stock levels and inventory requirements.")

# --------------------------------------------------
# FIND PROJECT ROOT AND INVENTORY FILE
# --------------------------------------------------
APP_DIR = Path(__file__).resolve().parent

# If this script is inside pages/, project root is one level above.
BASE_PATH = APP_DIR.parent if APP_DIR.name.lower() == "pages" else APP_DIR

INVENTORY_FILE_NAMES = [
    "cleaned_inventory_snapshot.csv",
    "inventory_snapshot.csv",
    "cleaned_inventory.csv"
]

inventory_path = None

# Search the project root and pages directory.
for folder in [BASE_PATH, APP_DIR]:
    for file_name in INVENTORY_FILE_NAMES:
        candidate = folder / file_name
        if candidate.is_file():
            inventory_path = candidate
            break
    if inventory_path is not None:
        break

# --------------------------------------------------
# LOAD INVENTORY DATA
# --------------------------------------------------
if inventory_path is None:
    st.error("Inventory dataset file was not found.")
    st.markdown(
        """
        **Please follow these steps:**

        1. Open your GitHub repository.
        2. Upload `cleaned_inventory_snapshot.csv` to the main
           repository folder (the same folder as `app.py`).
        3. Commit the file and wait for Streamlit Cloud to redeploy.

        Your repository structure should look like this:

        ```
        retialplus_dashboard/
        ├── app.py
        ├── cleaned_inventory_snapshot.csv
        └── pages/
            └── 4_Inventory_Optimization.py
        ```

        If your inventory dataset has a different filename, rename it
        to `cleaned_inventory_snapshot.csv` or add its name to the
        `INVENTORY_FILE_NAMES` list in this code.
        """
    )
    st.stop()

try:
    inventory = pd.read_csv(inventory_path)
except Exception as error:
    st.error(f"Unable to read the inventory dataset: {error}")
    st.stop()

if inventory.empty:
    st.warning("The inventory dataset is empty.")
    st.stop()

# --------------------------------------------------
# VALIDATE REQUIRED COLUMNS
# --------------------------------------------------
required_columns = [
    "sku_id",
    "store_id",
    "stock_on_hand",
    "reorder_point",
    "safety_stock"
]

missing_columns = [
    column for column in required_columns
    if column not in inventory.columns
]

if missing_columns:
    st.error(
        "The inventory file is missing required columns: "
        + ", ".join(missing_columns)
    )
    st.write("Columns found in your dataset:", inventory.columns.tolist())
    st.stop()

# Convert inventory calculation columns to numeric values.
for column in ["stock_on_hand", "reorder_point", "safety_stock"]:
    inventory[column] = pd.to_numeric(
        inventory[column], errors="coerce"
    )

inventory = inventory.dropna(
    subset=["stock_on_hand", "reorder_point", "safety_stock"]
).copy()

if inventory.empty:
    st.warning("No valid inventory records are available for analysis.")
    st.stop()

# Ensure stock quantities cannot be negative in the recommendations.
inventory["stock_on_hand"] = inventory["stock_on_hand"].clip(lower=0)
inventory["reorder_point"] = inventory["reorder_point"].clip(lower=0)
inventory["safety_stock"] = inventory["safety_stock"].clip(lower=0)

st.caption(f"Data source: {inventory_path.name}")

# --------------------------------------------------
# STEP 1: INVENTORY OVERVIEW
# --------------------------------------------------
st.subheader("Inventory Overview")

col1, col2, col3 = st.columns(3)

col1.metric(
    "Total Inventory Records",
    f"{len(inventory):,}"
)

col2.metric(
    "Products in Inventory",
    f"{inventory['sku_id'].nunique():,}"
)

col3.metric(
    "Stores Covered",
    f"{inventory['store_id'].nunique():,}"
)

st.success("Inventory data loaded successfully.")

with st.expander("View Inventory Data"):
    st.dataframe(inventory.head(100), use_container_width=True)

# --------------------------------------------------
# STEP 2: STOCK LEVEL ANALYSIS
# --------------------------------------------------
st.subheader("Stock Level Analysis")

low_stock = inventory[
    inventory["stock_on_hand"] <= inventory["reorder_point"]
].copy()

out_of_stock = inventory[
    inventory["stock_on_hand"] <= 0
].copy()

healthy_stock = inventory[
    inventory["stock_on_hand"] > inventory["reorder_point"]
].copy()

col1, col2, col3 = st.columns(3)

col1.metric("Low Stock Items", f"{len(low_stock):,}")
col2.metric("Out of Stock Items", f"{len(out_of_stock):,}")
col3.metric("Healthy Stock Items", f"{len(healthy_stock):,}")

if low_stock.empty:
    st.success("No items are currently at or below their reorder point.")
else:
    st.dataframe(low_stock.head(100), use_container_width=True)

# --------------------------------------------------
# STEP 3: REORDER RECOMMENDATIONS
# --------------------------------------------------
st.subheader("Reorder Recommendations")

reorder_recommendations = low_stock.copy()

reorder_recommendations["recommended_order_qty"] = (
    reorder_recommendations["reorder_point"]
    + reorder_recommendations["safety_stock"]
    - reorder_recommendations["stock_on_hand"]
).clip(lower=0)

reorder_recommendations = reorder_recommendations.sort_values(
    "recommended_order_qty",
    ascending=False
)

col1, col2 = st.columns(2)

col1.metric(
    "Items Requiring Reorder",
    f"{len(reorder_recommendations):,}"
)

col2.metric(
    "Total Recommended Units",
    f"{reorder_recommendations['recommended_order_qty'].sum():,.0f}"
)

reorder_columns = [
    "store_id",
    "sku_id",
    "stock_on_hand",
    "reorder_point",
    "safety_stock",
    "recommended_order_qty"
]

if reorder_recommendations.empty:
    st.info("No reorder recommendations are required at this time.")
else:
    st.dataframe(
        reorder_recommendations[reorder_columns].head(100),
        use_container_width=True
    )

# --------------------------------------------------
# STEP 4: REORDER PRIORITY ANALYSIS
# --------------------------------------------------
st.subheader("Reorder Priority Analysis")

priority_data = reorder_recommendations.copy()

if priority_data.empty:
    priority_summary = pd.DataFrame({
        "Reorder Priority": ["High", "Medium", "Low"],
        "Item Count": [0, 0, 0]
    })
else:
    high_threshold = priority_data["recommended_order_qty"].quantile(0.75)
    low_threshold = priority_data["recommended_order_qty"].quantile(0.25)

    priority_data["reorder_priority"] = "Medium"

    priority_data.loc[
        priority_data["recommended_order_qty"] >= high_threshold,
        "reorder_priority"
    ] = "High"

    priority_data.loc[
        priority_data["recommended_order_qty"] <= low_threshold,
        "reorder_priority"
    ] = "Low"

    # Assign High priority first if thresholds overlap.
    if priority_data["recommended_order_qty"].nunique() == 1:
        priority_data["reorder_priority"] = "High"

    priority_summary = (
        priority_data["reorder_priority"]
        .value_counts()
        .reindex(["High", "Medium", "Low"], fill_value=0)
        .rename_axis("Reorder Priority")
        .reset_index(name="Item Count")
    )

st.dataframe(priority_summary, use_container_width=True)

st.bar_chart(
    priority_summary.set_index("Reorder Priority"),
    x_label="Reorder Priority",
    y_label="Item Count"
)

# --------------------------------------------------
# STEP 5: INVENTORY OPTIMIZATION SUMMARY
# --------------------------------------------------
st.subheader("Inventory Optimization Summary")

total_recommended_qty = reorder_recommendations[
    "recommended_order_qty"
].sum()

col1, col2, col3, col4 = st.columns(4)

col1.metric("Inventory Records", f"{len(inventory):,}")
col2.metric("Low Stock Items", f"{len(low_stock):,}")
col3.metric("Reorder Items", f"{len(reorder_recommendations):,}")
col4.metric("Recommended Order Qty", f"{total_recommended_qty:,.0f}")

# --------------------------------------------------
# STEP 6: PRIORITY INSIGHTS
# --------------------------------------------------
st.subheader("Inventory Reorder Insights")

if priority_data.empty:
    st.info("There are no items requiring reorder.")
else:
    high_priority_items = priority_data[
        priority_data["reorder_priority"] == "High"
    ]

    medium_priority_items = priority_data[
        priority_data["reorder_priority"] == "Medium"
    ]

    low_priority_items = priority_data[
        priority_data["reorder_priority"] == "Low"
    ]

    col1, col2, col3 = st.columns(3)

    col1.metric("High Priority Reorders", f"{len(high_priority_items):,}")
    col2.metric("Medium Priority Reorders", f"{len(medium_priority_items):,}")
    col3.metric("Low Priority Reorders", f"{len(low_priority_items):,}")

    st.write(
        "High-priority items should be considered first for inventory replenishment."
    )

    priority_columns = reorder_columns + ["reorder_priority"]

    st.dataframe(
        high_priority_items[priority_columns].head(100),
        use_container_width=True
    )

# --------------------------------------------------
# STEP 7: REORDER PRIORITY DISTRIBUTION
# --------------------------------------------------
st.subheader("Reorder Priority Distribution")

st.bar_chart(
    priority_summary.set_index("Reorder Priority"),
    x_label="Reorder Priority",
    y_label="Number of Items"
)

st.info(
    "High-priority reorder items should be replenished first "
    "to reduce the risk of stock shortages."
)

# --------------------------------------------------
# STEP 8: STORE-WISE REORDER ANALYSIS
# --------------------------------------------------
st.subheader("Store-wise Reorder Analysis")

if reorder_recommendations.empty:
    st.info("Store-wise reorder analysis is unavailable because no items require reorder.")
else:
    store_reorder_summary = (
        reorder_recommendations
        .groupby("store_id")
        .agg(
            Reorder_Items=("sku_id", "count"),
            Recommended_Order_Qty=("recommended_order_qty", "sum")
        )
        .reset_index()
        .sort_values("Recommended_Order_Qty", ascending=False)
    )

    st.dataframe(store_reorder_summary, use_container_width=True)

    st.bar_chart(
        store_reorder_summary.set_index("store_id")[
            "Recommended_Order_Qty"
        ],
        x_label="Store",
        y_label="Recommended Order Quantity"
    )

# --------------------------------------------------
# STEP 9: SKU-WISE REORDER ANALYSIS
# --------------------------------------------------
st.subheader("SKU-wise Reorder Analysis")

if reorder_recommendations.empty:
    st.info("SKU-wise reorder analysis is unavailable because no items require reorder.")
else:
    sku_reorder_summary = (
        reorder_recommendations
        .groupby("sku_id")
        .agg(
            Reorder_Items=("store_id", "count"),
            Recommended_Order_Qty=("recommended_order_qty", "sum")
        )
        .reset_index()
        .sort_values("Recommended_Order_Qty", ascending=False)
    )

    st.dataframe(
        sku_reorder_summary.head(30),
        use_container_width=True
    )

    st.bar_chart(
        sku_reorder_summary.head(10).set_index("sku_id")[
            "Recommended_Order_Qty"
        ],
        x_label="SKU",
        y_label="Recommended Order Quantity"
    )

# --------------------------------------------------
# STEP 10: FINAL INVENTORY INSIGHTS
# --------------------------------------------------
st.subheader("Inventory Optimization Insights")

st.write(f"**Total inventory records:** {len(inventory):,}")
st.write(f"**Total low-stock items:** {len(low_stock):,}")
st.write(f"**Total reorder items:** {len(reorder_recommendations):,}")
st.write(
    "**Total recommended order quantity:** "
    f"{total_recommended_qty:,.0f} units."
)

if not reorder_recommendations.empty:
    store_reorder_summary = (
        reorder_recommendations
        .groupby("store_id")
        .agg(
            Reorder_Items=("sku_id", "count"),
            Recommended_Order_Qty=("recommended_order_qty", "sum")
        )
        .reset_index()
        .sort_values("Recommended_Order_Qty", ascending=False)
    )

    sku_reorder_summary = (
        reorder_recommendations
        .groupby("sku_id")
        .agg(
            Reorder_Items=("store_id", "count"),
            Recommended_Order_Qty=("recommended_order_qty", "sum")
        )
        .reset_index()
        .sort_values("Recommended_Order_Qty", ascending=False)
    )

    top_store = store_reorder_summary.iloc[0]
    top_sku = sku_reorder_summary.iloc[0]

    st.write(
        "**Highest reorder requirement store:** "
        f"{top_store['store_id']} "
        f"({top_store['Recommended_Order_Qty']:,.0f} units)."
    )

    st.write(
        "**Highest reorder requirement SKU:** "
        f"{top_sku['sku_id']} "
        f"({top_sku['Recommended_Order_Qty']:,.0f} units)."
    )

    st.success("Inventory optimization analysis completed.")
else:
    st.success("Inventory data loaded. No additional stock reorder is currently indicated.")
