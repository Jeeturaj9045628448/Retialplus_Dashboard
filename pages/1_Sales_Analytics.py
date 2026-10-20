).properties(height=330)
st.altair_chart(pie, use_container_width=True)

st.subheader("📋 Filtered Sales Data")
m1, m2, m3 = st.columns(3)
m1.metric("Total Sales", f"₹{total_sales:,.2f}")
m2.metric("Total Orders", f"{transactions:,}")
m3.metric("Average Order Value", f"₹{aov:,.2f}")
with st.expander("Sales Dataset Preview"):
    st.dataframe(filtered.head(100), use_container_width=True, hide_index=True)
st.download_button("⬇️ Download Filtered Sales CSV", filtered.to_csv(index=False).encode("utf-8"), "retailpulse_filtered_sales.csv", "text/csv")

st.subheader("📈 Daily Sales Trend")
daily = filtered.assign(Date=filtered["date"].dt.floor("D")).groupby("Date", as_index=False)["total_value"].sum().rename(columns={"total_value":"Sales Value"})
daily_chart = alt.Chart(daily).mark_line(point=False).encode(
    x=alt.X("Date:T", title="Date", axis=alt.Axis(format="%Y %b", labelAngle=-30)),
    y=alt.Y("Sales Value:Q", title="Sales Value", axis=alt.Axis(format=",.0f")),
    tooltip=[alt.Tooltip("Date:T", format="%d %b %Y"), alt.Tooltip("Sales Value:Q", format=",.2f")]
).properties(height=360)
st.altair_chart(daily_chart, use_container_width=True)

st.subheader("Sales by Channel")
st.dataframe(channel_sales.sort_values("Total Sales", ascending=False), use_container_width=True, hide_index=True)

def bar_chart(data, category, value, title, top=None, height=350, horizontal=True):
    if data.empty:
        st.info(f"No data available for {title.lower()}.")
        return
    plot_data = data.copy()
    if top:
        plot_data = plot_data.nlargest(top, value)
    enc_x = alt.X(f"{value}:Q", title=value, axis=alt.Axis(format=",.0f"))
    enc_y = alt.Y(f"{category}:N", title=category, sort="-x")
    chart = alt.Chart(plot_data).mark_bar().encode(
        x=enc_x, y=enc_y,
        tooltip=[category, alt.Tooltip(f"{value}:Q", format=",.2f")]
    ).properties(title=title, height=height)
    st.altair_chart(chart, use_container_width=True)

st.subheader("Top 10 Stores by Sales")
store_sales = filtered.groupby("store_id", as_index=False)["total_value"].sum().rename(columns={"store_id":"Store ID", "total_value":"Total Sales"})
bar_chart(store_sales, "Store ID", "Total Sales", "Top 10 Stores by Sales", top=10)

st.subheader("Monthly Sales Trend")
monthly = filtered.assign(Month=filtered["date"].dt.to_period("M").astype(str)).groupby("Month", as_index=False)["total_value"].sum().rename(columns={"total_value":"Total Sales"})
monthly_chart = alt.Chart(monthly).mark_bar().encode(
    x=alt.X("Month:N", sort=None, axis=alt.Axis(labelAngle=-55), title="Month"),
    y=alt.Y("Total Sales:Q", axis=alt.Axis(format=",.0f")),
    tooltip=["Month", alt.Tooltip("Total Sales:Q", format=",.2f")]
).properties(height=360)
st.altair_chart(monthly_chart, use_container_width=True)

st.subheader("Top 10 Products (SKU) by Sales")
sku_sales = filtered.groupby("sku_id", as_index=False)["total_value"].sum().rename(columns={"sku_id":"SKU ID", "total_value":"Total Sales"})
bar_chart(sku_sales, "SKU ID", "Total Sales", "Top 10 Products by Sales", top=10)

st.subheader("Store-wise Sales by Channel")
store_channel = filtered.groupby(["store_id", "channel"], as_index=False)["total_value"].sum().rename(columns={"store_id":"Store ID", "channel":"Channel", "total_value":"Total Sales"})
stacked = alt.Chart(store_channel).mark_bar().encode(
    x=alt.X("Total Sales:Q", axis=alt.Axis(format=",.0f"), title="Total Sales"),
    y=alt.Y("Store ID:N", sort="-x"),
    color="Channel:N",
    tooltip=["Store ID", "Channel", alt.Tooltip("Total Sales:Q", format=",.2f")]
).properties(height=600)
st.altair_chart(stacked, use_container_width=True)

st.subheader("Sales by Discount Percentage")
discount_sales = filtered.groupby("discount_pct", as_index=False)["total_value"].sum().rename(columns={"discount_pct":"Discount Percentage", "total_value":"Total Sales"})
bar_chart(discount_sales, "Discount Percentage", "Total Sales", "Sales by Discount Percentage", top=30)

st.subheader("Sales by Quantity")
quantity_sales = filtered.groupby("quantity", as_index=False)["total_value"].sum().rename(columns={"quantity":"Quantity", "total_value":"Total Sales"})
bar_chart(quantity_sales, "Quantity", "Total Sales", "Sales by Quantity")

st.subheader("Sales by Year")
year_sales = filtered.assign(Year=filtered["date"].dt.year.astype(str)).groupby("Year", as_index=False)["total_value"].sum().rename(columns={"total_value":"Total Sales"})
bar_chart(year_sales, "Year", "Total Sales", "Sales by Year", height=300)

st.subheader("Top 10 Customers by Sales")
customer_sales = filtered.groupby("customer_id", as_index=False)["total_value"].sum().rename(columns={"customer_id":"Customer ID", "total_value":"Total Sales"})
bar_chart(customer_sales, "Customer ID", "Total Sales", "Top 10 Customers by Sales", top=10)

# Customer demographic breakdowns are included only when the customer master has those columns.
demographic_charts = [
    ("customer_segment", "Sales by Customer Segment"),
    ("preferred_channel", "Sales by Preferred Channel"),
    ("gender", "Sales by Customer Gender"),
    ("city", "Sales by Customer City"),
    ("age_group", "Sales by Customer Age Group"),
]
for col, title in demographic_charts:
    if col in filtered.columns:
        st.subheader(title)
        grouped = filtered.groupby(col, dropna=False, as_index=False)["total_value"].sum()
        grouped[col] = grouped[col].fillna("Unknown").astype(str)
        grouped = grouped.rename(columns={col: title.replace("Sales by ", ""), "total_value":"Total Sales"})
        category_name = title.replace("Sales by ", "")
        bar_chart(grouped, category_name, "Total Sales", title, top=30, height=360)

# Selected cross-breakdowns based on available customer master fields.
cross_breakdowns = [
    ("preferred_channel", "age_group", "Sales by Customer Preferred Channel & Age Group"),
    ("city", "age_group", "Sales by Customer City & Age Group"),
    ("gender", "age_group", "Sales by Customer Gender & Age Group"),
    ("loyalty_segment", "age_group", "Sales by Customer Loyalty Segment & Age Group"),
    ("preferred_channel", "loyalty_segment", "Sales by Customer Preferred Channel & Loyalty Segment"),
    ("gender", "loyalty_segment", "Sales by Customer Gender & Loyalty Segment"),
    ("city", "loyalty_segment", "Sales by Customer City & Loyalty Segment"),
    ("preferred_channel", "gender", "Sales by Customer Preferred Channel & Gender"),
    ("city", "preferred_channel", "Sales by Customer City & Preferred Channel"),
    ("city", "gender", "Sales by Customer City & Gender"),
]
for col_a, col_b, title in cross_breakdowns:
    if col_a in filtered.columns and col_b in filtered.columns:
        st.subheader(title)
        cross = filtered.copy()
        cross[col_a] = cross[col_a].fillna("Unknown").astype(str)
        cross[col_b] = cross[col_b].fillna("Unknown").astype(str)
        cross_data = cross.groupby([col_a, col_b], as_index=False)["total_value"].sum()
        cross_data = cross_data.rename(columns={col_a:"Category", col_b:"Breakdown", "total_value":"Total Sales"})
        chart = alt.Chart(cross_data).mark_bar().encode(
            x=alt.X("Total Sales:Q", axis=alt.Axis(format=",.0f"), title="Total Sales"),
            y=alt.Y("Category:N", sort="-x"),
            color="Breakdown:N",
            tooltip=["Category", "Breakdown", alt.Tooltip("Total Sales:Q", format=",.2f")]
        ).properties(height=450, title=title)
        st.altair_chart(chart, use_container_width=True)
