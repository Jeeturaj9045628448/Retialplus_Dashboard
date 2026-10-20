
st.caption(
    f"Metrics based on latest available sales date: "
    f"{latest_date.strftime('%d %b %Y')}"
)


st.subheader("Inventory Alerts")

if low_stock_items > 0:

    st.warning(
        f"⚠️ {low_stock_items:,} inventory items are at "
        f"or below their reorder point."
    )

else:

    st.success(
        "✅ No low-stock inventory alerts."
    )

st.subheader("Sales Performance Alert")

sales_difference_pct = (
    ((total_sales_latest - average_daily_sales) / average_daily_sales) * 100
    if pd.notna(average_daily_sales) and average_daily_sales != 0
    else 0.0
)


col1, col2 = st.columns(2)

col1.metric(
    "Average Daily Sales",
    f"₹{average_daily_sales:,.0f}"
)

col2.metric(
    "Sales Difference",
    f"{sales_difference_pct:+.2f}%"
)


if sales_difference_pct <= -20:

    st.error(
        f"🚨 Sales Alert: Latest sales are "
        f"{abs(sales_difference_pct):.2f}% below "
        f"the average daily sales."
    )

elif sales_difference_pct >= 20:

    st.success(
        f"🚀 Strong Sales Alert: Latest sales are "
        f"{sales_difference_pct:.2f}% above "
        f"the average daily sales."
    )

else:

    st.info(
        f"ℹ️ Sales Performance is Normal — "
        f"latest sales are {sales_difference_pct:+.2f}% "
        f"from the average daily sales."
    )

st.subheader("Reorder Priority Alerts")

reorder_mask = (
    inventory_data["stock_on_hand"]
    <= inventory_data["reorder_point"]
)

reorder_items = inventory_data.loc[reorder_mask].copy()

reorder_items["recommended_order_qty"] = (
    reorder_items["reorder_point"]
    - reorder_items["stock_on_hand"]
).clip(lower=0)

if len(reorder_items) > 0:

    q75 = reorder_items["recommended_order_qty"].quantile(0.75)
    q25 = reorder_items["recommended_order_qty"].quantile(0.25)

    high_priority_items = (
        reorder_items["recommended_order_qty"] >= q75
    ).sum()

    medium_priority_items = (
        (reorder_items["recommended_order_qty"] >= q25)
        &
        (reorder_items["recommended_order_qty"] < q75)
    ).sum()

    low_priority_items = (
        reorder_items["recommended_order_qty"] < q25
    ).sum()

else:
    high_priority_items = 0
    medium_priority_items = 0
    low_priority_items = 0

total_reorder_items = (
    high_priority_items
    + medium_priority_items
    + low_priority_items
)

col1, col2, col3 = st.columns(3)

col1.metric("High Priority", f"{high_priority_items:,}")
col2.metric("Medium Priority", f"{medium_priority_items:,}")
col3.metric("Low Priority", f"{low_priority_items:,}")

st.write(
    f"**Total items requiring replenishment:** "
    f"{total_reorder_items:,}"
)

if high_priority_items > 0:
    st.warning(
        f"⚠️ {high_priority_items:,} high-priority "
        "reorder items require immediate attention."
    )
else:
    st.success("✅ No high-priority reorder alerts.")

st.subheader("Alert Status Summary")


if sales_difference_pct <= -20:

    sales_alert_status = "Critical"

elif sales_difference_pct >= 20:

    sales_alert_status = "Strong"

else:

    sales_alert_status = "Normal"


if low_stock_items > 0:

    inventory_alert_status = "Critical"

else:

    inventory_alert_status = "Normal"


if high_priority_items > 0:

    reorder_alert_status = "Critical"
