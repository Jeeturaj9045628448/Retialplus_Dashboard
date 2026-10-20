        )

    else:

        st.success(
            "Inventory levels are healthy."
        )


with col2:

    st.markdown("#### Reorder Alert")

    st.write(
        f"High-priority reorder items: "
        f"**{high_priority_items:,}**"
    )

    if high_priority_items > 0:

        st.warning(
            "High-priority items require immediate attention."
        )

    else:

        st.success(
            "No high-priority reorder items."
        )

st.subheader("Recent Sales Trend")


recent_sales = (
    daily_sales
    .sort_index()
    .tail(7)
)


recent_average_sales = recent_sales.mean()


latest_vs_recent_avg = (
    (
        total_sales_latest
        - recent_average_sales
    )
    / recent_average_sales
) * 100


col1, col2 = st.columns(2)


col1.metric(
    "7-Day Average Sales",
    f"₹{recent_average_sales:,.0f}"
)


col2.metric(
    "Latest Sales vs 7-Day Average",
    f"{latest_vs_recent_avg:+.2f}%"
)


if latest_vs_recent_avg >= 20:

    st.success(
        f"🚀 Recent Sales Alert: Latest sales are "
        f"{latest_vs_recent_avg:.2f}% above the 7-day average."
    )

elif latest_vs_recent_avg <= -20:

    st.error(
        f"🚨 Recent Sales Alert: Latest sales are "
        f"{abs(latest_vs_recent_avg):.2f}% below the 7-day average."
    )

else:

    st.info(
        "ℹ️ Recent sales are within the normal range "
        "of the 7-day average."
    )

st.subheader("Daily Alert Monitoring")


recent_alert_data = (
    daily_sales
    .sort_index()
    .tail(7)
)


recent_alert_data = recent_alert_data.to_frame(
    name="Sales"
)


recent_alert_data["Difference %"] = (
    (
        recent_alert_data["Sales"]
        - average_daily_sales
    )
    / average_daily_sales
) * 100


def get_alert_status(value):

    if value <= -20:

        return "Critical"

    elif value >= 20:

        return "Strong"

    else:

        return "Normal"


recent_alert_data["Alert Status"] = (
    recent_alert_data["Difference %"]
    .apply(get_alert_status)
)


critical_alerts = (
    recent_alert_data["Alert Status"]
    == "Critical"
).sum()


strong_alerts = (
    recent_alert_data["Alert Status"]
    == "Strong"
).sum()


normal_alerts = (
    recent_alert_data["Alert Status"]
    == "Normal"
).sum()


col1, col2, col3 = st.columns(3)


col1.metric(
    "Critical Alerts",
    f"{critical_alerts}"
)

