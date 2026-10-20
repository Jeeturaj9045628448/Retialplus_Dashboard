total_checks = len(validation_checks)



if passed_checks == total_checks:
    st.success(
        "✅ completed  "
        "Real-time metrics, sales alerts, inventory alerts, "
        "and reorder priority monitoring are working correctly."
    )
else:
    st.warning(
        "⚠️ Some  validation checks require review."
    )

st.subheader("📥 Report Export Center")

st.markdown("Generate and download business reports in CSV and PDF formats")

sales_export = sales_data.copy()

sales_csv = sales_export.to_csv(index=False).encode("utf-8")

st.download_button(
label="📄 Download • 📊 Export Sales Data (CSV)",
data=sales_csv,
file_name="retailpulse_sales_report.csv",
mime="text/csv")

inventory_export = inventory_data.copy()

inventory_export["recommended_order_qty"] = (
    inventory_export["reorder_point"]
    - inventory_export["stock_on_hand"]
).clip(lower=0)

inventory_csv = inventory_export.to_csv(index=False).encode("utf-8")

st.download_button(
    label="📦 Download • 📊 Export Inventory & Reorder Data (CSV)",
    data=inventory_csv,
    file_name="retailpulse_inventory_reorder_report.csv",
    mime="text/csv"
)

alert_summary = pd.DataFrame({
    "Metric": [
        "Latest Sales",
        "Units Sold",
        "Orders",
        "Low Stock Alerts",
        "Average Daily Sales",
        "Sales Difference",
        "Sales Alert Status",
        "Inventory Alert Status",
        "Reorder Alert Status",
        "High Priority Reorder Items",
        "Medium Priority Reorder Items",
        "Low Priority Reorder Items",
        "Total Items Requiring Replenishment",
        "7-Day Average Sales",
        "Latest vs 7-Day Average",
        "Critical Alert Days",
        "Strong Alert Days",
        "Normal Days"
    ],
    "Value": [
        total_sales_latest,
        total_units_latest,
        total_orders_latest,
        low_stock_items,
        average_daily_sales,
        f"{sales_difference_pct:+.2f}%",
        sales_alert_status,
        inventory_alert_status,
        reorder_alert_status,
        high_priority_items,
        medium_priority_items,
        low_priority_items,
        total_reorder_items,
        recent_average_sales,
        f"{latest_vs_recent_avg:+.2f}%",
        critical_alerts,
        strong_alerts,
        normal_alerts
    ]
})

alert_csv = alert_summary.to_csv(index=False).encode("utf-8")

st.download_button(
    label="🚨 Download • 📊 Export Alert Summary (CSV)",
    data=alert_csv,
    file_name="retailpulse_alert_summary.csv",
    mime="text/csv"
)

# Step 5: PDF Report Export

from reportlab.lib.pagesizes import A4
from reportlab.platypus import (
    SimpleDocTemplate,
    Paragraph,
    Spacer,
    Table,
    TableStyle
)
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.enums import TA_CENTER
from io import BytesIO


def create_pdf_report():

    buffer = BytesIO()

    doc = SimpleDocTemplate(
        buffer,
        pagesize=A4,
        rightMargin=40,
        leftMargin=40,
        topMargin=40,
        bottomMargin=40
    )

    styles = getSampleStyleSheet()

    title_style = styles["Title"]
    title_style.alignment = TA_CENTER

    heading_style = styles["Heading2"]

    normal_style = styles["Normal"]

    story = []

    # Report Title
    story.append(
        Paragraph(
            "RetailPulse AI Analytics Platform",
            title_style
        )
    )

    story.append(
        Paragraph(
            "Real-time Metrics & Alert Report",
            heading_style
        )
    )

    story.append(Spacer(1, 12))

    # Key Metrics
    story.append(
        Paragraph("Key Metrics", heading_style)
    )

    metrics_data = [
