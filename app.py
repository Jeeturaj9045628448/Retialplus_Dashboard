from pathlib import Path
import streamlit as st

st.set_page_config(
    page_title="RetailPulse AI Analytics Platform",
    page_icon="🚀",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Keep the main page visually consistent with the screenshots.
st.markdown(
    """
    <style>
    .block-container {
        padding-top: 2rem;
        padding-bottom: 2.5rem;
        max-width: 1500px;
    }
    [data-testid="stSidebarNav"] {
        display: none;
    }
    .rp-subtitle {
        color: #d1d5db;
        font-size: 1.05rem;
        line-height: 1.7;
        margin-bottom: 1.5rem;
    }
    .rp-section {
        border-top: 1px solid rgba(128,128,128,.35);
        padding-top: 1.5rem;
        margin-top: 1.5rem;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

# Custom sidebar: one navigation menu only.
with st.sidebar:
    st.markdown("## 🛍️ RetailPulse")
    st.caption("Retail analytics and decision support")
    st.divider()
    st.page_link("app.py", label="Dashboard Overview", icon="🏠")
    st.page_link("pages/1_Sales_Analytics.py", label="Sales Analytics", icon="📊")
    st.page_link("pages/2_Demand_Forecasting.py", label="Demand Forecasting", icon="📈")
    st.page_link("pages/3_Customer_Segmentation.py", label="Customer Segmentation + Churn Risk", icon="👥")
    st.page_link("pages/4_Inventory_Optimization.py", label="Inventory Optimization", icon="📦")

# Main overview, matching the first reference screenshot.
st.title("🚀 RetailPulse AI Analytics Platform")
st.header("📌 Overview")
st.markdown(
    """
    <div class="rp-subtitle">
    RetailPulse is an AI-powered retail analytics platform designed to help
    businesses understand customers, forecast demand, manage inventory, and
    make data-driven decisions.
    </div>
    """,
    unsafe_allow_html=True,
)

left, right = st.columns(2, gap="large")

with left:
    st.markdown("### 📈 Demand Forecasting")
    st.write("Prophet + LSTM based 30-day demand forecasting.")
    st.markdown("### 👥 Customer Analytics")
    st.write("RFM analysis and customer segmentation using machine learning.")
    st.markdown("### ⚠️ Churn Prediction")
    st.write("Identify customers who are at risk of churn.")

with right:
    st.markdown("### 📦 Inventory Optimization")
    st.write("Forecast-based reorder recommendations and stock monitoring.")
    st.markdown("### 📊 Business Intelligence")
    st.write("Interactive analytics, KPIs, alerts and downloadable reports.")

st.markdown('<div class="rp-section"></div>', unsafe_allow_html=True)
st.header("🏗️ System Architecture")
st.markdown(
    "**Data → Processing → ML Models → Forecasting → Dashboard → Deployment → Insights**"
)

a, b, c, d, e = st.columns(5, gap="medium")
a.info("📥  **Data**")
b.info("⚙️  **Processing**")
c.info("🤖  **ML Models**")
d.info("📈  **Forecasting**")
e.info("💡  **Insights**")

st.markdown('<div class="rp-section"></div>', unsafe_allow_html=True)
st.success("✅ RetailPulse dashboard is ready.")
st.info(
    "👉 Use the sidebar to explore Sales Analytics, Demand Forecasting, "
    "Customer Segmentation + Churn Risk, and Inventory Optimization."
)

st.caption(
    "Note: This page is the dashboard overview. Detailed charts and filters "
    "are available on the individual pages."
)

checks = {
    "Sales data loaded": not sales.empty,
    "Latest sales metric available": latest_sales >= 0,
    "Daily sales trend available": not daily_sales.empty,
    "Inventory monitoring available": low_stock is not None,
}
passed = sum(checks.values())
st.progress(passed / len(checks))
st.write(f"**{passed}/{len(checks)} checks passed**")
for name, ok in checks.items():
    st.write(("✅ " if ok else "⚠️ ") + name)

st.header("📥 Report Export Center")
st.write("Generate and download sales, inventory, alert summary, and business reports.")

sales_csv = sales.to_csv(index=False).encode("utf-8")
st.download_button("📄 Download Sales Data (CSV)", sales_csv, "retailpulse_sales_report.csv", "text/csv")

alert_summary = pd.DataFrame([
    ["Latest Sales", latest_sales],
    ["Units Sold", units_sold],
    ["Orders", orders_latest],
    ["Low Stock Alerts", low_stock if low_stock is not None else "Unavailable"],
    ["Average Daily Sales", average_daily_sales],
    ["Sales Difference", f"{sales_difference_pct:+.2f}%"],
    ["Sales Alert Status", sales_status],
    ["Inventory Alert Status", inventory_status],
    ["Reorder Alert Status", reorder_status],
    ["High Priority Reorder Items", high_priority if low_stock is not None else "Unavailable"],
    ["Medium Priority Reorder Items", medium_priority if low_stock is not None else "Unavailable"],
    ["Low Priority Reorder Items", low_priority if low_stock is not None else "Unavailable"],
    ["7-Day Average Sales", recent_average],
    ["Latest vs 7-Day Average", f"{recent_diff_pct:+.2f}%"],
    ["Critical Alert Days", critical_alerts],
    ["Strong Alert Days", strong_alerts],
    ["Normal Days", normal_alerts],
], columns=["Metric", "Value"])
alert_csv = alert_summary.to_csv(index=False).encode("utf-8")
st.download_button("🚨 Download Alert Summary (CSV)", alert_csv, "retailpulse_alert_summary.csv", "text/csv")

if inventory is not None:
    inventory_export = inventory.copy()
    inventory_export["recommended_order_qty"] = (inventory_export["reorder_point"] - inventory_export["stock_on_hand"]).clip(lower=0)
    st.download_button(
        "📦 Download Inventory & Reorder Data (CSV)",
        inventory_export.to_csv(index=False).encode("utf-8"),
        "retailpulse_inventory_reorder_report.csv",
        "text/csv",
    )
else:
    st.caption("Inventory CSV export becomes available when the inventory file is added.")

st.subheader("📊 Export Summary")
export_rows = [
    {"Report": "Sales Data Report", "Format": "CSV", "Status": "Available"},
    {"Report": "Alert Summary Report", "Format": "CSV", "Status": "Available"},
    {"Report": "Inventory & Reorder Report", "Format": "CSV", "Status": "Available" if inventory is not None else "Needs inventory CSV"},
]
st.dataframe(pd.DataFrame(export_rows), use_container_width=True, hide_index=True)

st.header("📅 Data Freshness Monitor")
today = pd.Timestamp.today().normalize()
data_age_days = max(0, (today - latest_date.normalize()).days)
freshness = "Fresh" if data_age_days <= 2 else ("Slightly Delayed" if data_age_days <= 7 else "Historical / Stale")
z1, z2, z3 = st.columns(3)
z1.metric("Latest Data Date", latest_date.strftime("%d %b %Y"))
z2.metric("Data Age", f"{data_age_days} days")
z3.metric("Freshness Status", freshness)
if freshness == "Fresh":
    st.success("✅ Data appears recent.")
elif freshness == "Slightly Delayed":
    st.warning("⚠️ Please review the data update schedule.")
else:
    st.error("🚨 The dataset may need refreshing.")
st.caption("This indicator compares the system date with the latest date in the dataset; it does not confirm that data is live.")

st.header("📈 Interactive Sales Trend")
trend_days = st.selectbox("Select sales trend period", [7, 14, 30, 90], index=2, format_func=lambda x: f"Last {x} days")
trend = daily_sales.tail(trend_days).copy()
if not trend.empty:
    total_period_sales = float(trend["Sales"].sum())
    avg_period_sales = float(trend["Sales"].mean())
    highest_day = float(trend["Sales"].max())
    lowest_day = float(trend["Sales"].min())
    peak_date = trend.loc[trend["Sales"].idxmax(), "Date"]
    x1, x2, x3, x4 = st.columns(4)
    x1.metric("💰 Total Sales", f"₹{total_period_sales:,.2f}")
    x2.metric("📊 Average Daily Sales", f"₹{avg_period_sales:,.2f}")
    x3.metric("🚀 Highest Daily Sales", f"₹{highest_day:,.2f}")
    x4.metric("📉 Lowest Daily Sales", f"₹{lowest_day:,.2f}")
    st.caption(f"Peak sales date: {peak_date:%d %b %Y} | Showing {len(trend)} available daily records.")
    chart_choice = st.radio("Choose chart type", ["📈 Line Chart", "📊 Bar Chart", "🌊 Area Chart"], horizontal=True)
    base = alt.Chart(trend).encode(
        x=alt.X("Date:T", title="Date", axis=alt.Axis(format="%d %b", labelAngle=-45)),
        y=alt.Y("Sales:Q", title="Sales (₹)", axis=alt.Axis(format=",.0f")),
        tooltip=[alt.Tooltip("Date:T", title="Date", format="%d %b %Y"), alt.Tooltip("Sales:Q", title="Sales", format=",.2f")],
    )
    if chart_choice == "📊 Bar Chart":
        chart = base.mark_bar()
    elif chart_choice == "🌊 Area Chart":
        chart = base.mark_area(opacity=0.45, line=True)
    else:
        chart = base.mark_line(point=True)
    st.altair_chart(chart.properties(height=380, title=f"Daily Sales Trend — Last {trend_days} Days").interactive(), use_container_width=True)
    with st.expander("📋 View Daily Sales Data"):
        display_trend = trend.copy()
        display_trend["Date"] = display_trend["Date"].dt.strftime("%d %b %Y")
        st.dataframe(display_trend, use_container_width=True, hide_index=True)
    st.download_button(
        "⬇️ Download Sales Trend CSV",
        trend.to_csv(index=False).encode("utf-8"),
        f"retailpulse_sales_trend_{trend_days}_days.csv",
        "text/csv",
    )
else:
    st.info("No sales trend data available for the selected period.")

st.caption(f"Data source: {sales_path.name} | Latest sales date in data: {latest_date:%d %b %Y}")
