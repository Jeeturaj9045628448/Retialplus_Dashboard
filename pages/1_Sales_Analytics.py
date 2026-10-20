)

channel_loyalty_summary = (
    channel_loyalty_sales
    .groupby(
        ["preferred_channel", "loyalty_segment"]
    )["total_value"]
    .sum()
    .reset_index()
)

channel_loyalty_pivot = channel_loyalty_summary.pivot(
    index="loyalty_segment",
    columns="preferred_channel",
    values="total_value"
).fillna(0)

st.bar_chart(
    channel_loyalty_pivot,
    x_label="Loyalty Segment",
    y_label="Total Sales"
)

st.dataframe(
    channel_loyalty_pivot,
    width="stretch"
)

# Step 66: Sales by Customer Gender & Loyalty Segment

st.subheader("Sales by Customer Gender & Loyalty Segment")

gender_loyalty_sales = sales.merge(
    customers[["cust_id", "gender", "loyalty_segment"]],
    left_on="customer_id",
    right_on="cust_id",
    how="left"
)

gender_loyalty_summary = (
    gender_loyalty_sales
    .groupby(
        ["loyalty_segment", "gender"]
    )["total_value"]
    .sum()
    .reset_index()
)

gender_loyalty_pivot = gender_loyalty_summary.pivot(
    index="loyalty_segment",
    columns="gender",
    values="total_value"
).fillna(0)

st.bar_chart(
    gender_loyalty_pivot,
    x_label="Loyalty Segment",
    y_label="Total Sales"
)

st.dataframe(
    gender_loyalty_pivot,
    width="stretch"
)

# Step 68: Sales by Customer City & Loyalty Segment

st.subheader("Sales by Customer City & Loyalty Segment")

city_loyalty_sales = sales.merge(
    customers[["cust_id", "city", "loyalty_segment"]],
    left_on="customer_id",
    right_on="cust_id",
    how="left"
)

city_loyalty_summary = (
    city_loyalty_sales
    .groupby(
        ["loyalty_segment", "city"]
    )["total_value"]
    .sum()
    .reset_index()
)

city_loyalty_pivot = city_loyalty_summary.pivot(
    index="loyalty_segment",
    columns="city",
    values="total_value"
).fillna(0)

st.bar_chart(
    city_loyalty_pivot,
    x_label="Loyalty Segment",
    y_label="Total Sales"
)

st.dataframe(
    city_loyalty_pivot,
    width="stretch"
)

# Step 70: Sales by Customer Preferred Channel & Gender

st.subheader("Sales by Customer Preferred Channel & Gender")

channel_gender_sales = sales.merge(
    customers[["cust_id", "preferred_channel", "gender"]],
    left_on="customer_id",
    right_on="cust_id",
    how="left"
)

channel_gender_summary = (
    channel_gender_sales
    .groupby(["preferred_channel", "gender"])["total_value"]
    .sum()
    .reset_index()
)

channel_gender_pivot = channel_gender_summary.pivot(
    index="preferred_channel",
    columns="gender",
    values="total_value"
).fillna(0)

st.bar_chart(
    channel_gender_pivot,
    x_label="Preferred Channel",
    y_label="Total Sales"
)

st.dataframe(
    channel_gender_pivot,
    width="stretch"
)

# Step 72: Sales by Customer City & Preferred Channel

st.subheader("Sales by Customer City & Preferred Channel")

city_channel_sales = sales.merge(
    customers[["cust_id", "city", "preferred_channel"]],
    left_on="customer_id",
    right_on="cust_id",
    how="left"
)

city_channel_summary = (
    city_channel_sales
    .groupby(["city", "preferred_channel"])["total_value"]
    .sum()
    .reset_index()
)

city_channel_pivot = city_channel_summary.pivot(
    index="city",
    columns="preferred_channel",
    values="total_value"
).fillna(0)
