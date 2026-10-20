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

st.bar_chart(
    city_channel_pivot,
    x_label="City",
    y_label="Total Sales"
)

st.dataframe(
    city_channel_pivot,
    width="stretch"
)

# Step 74: Sales by Customer City & Gender

st.subheader("Sales by Customer City & Gender")

city_gender_sales = sales.merge(
    customers[["cust_id", "city", "gender"]],
    left_on="customer_id",
    right_on="cust_id",
    how="left"
)

city_gender_summary = (
    city_gender_sales
    .groupby(["city", "gender"])["total_value"]
    .sum()
    .reset_index()
)

city_gender_pivot = city_gender_summary.pivot(
    index="city",
    columns="gender",
    values="total_value"
).fillna(0)

st.bar_chart(
    city_gender_pivot,
    x_label="City",
    y_label="Total Sales"
)

st.dataframe(
    city_gender_pivot,
    width="stretch"
)



# Step 78: Sales by Customer Loyalty Segment & Gender

st.subheader("Sales by Customer Loyalty Segment & Gender")

loyalty_gender_sales = sales.merge(
    customers[["cust_id", "loyalty_segment", "gender"]],
    left_on="customer_id",
    right_on="cust_id",
    how="left"
)

loyalty_gender_summary = (
    loyalty_gender_sales
    .groupby(["loyalty_segment", "gender"])["total_value"]
    .sum()
    .reset_index()
)

loyalty_gender_pivot = loyalty_gender_summary.pivot(
    index="loyalty_segment",
    columns="gender",
    values="total_value"
).fillna(0)

st.bar_chart(
    loyalty_gender_pivot,
    x_label="Loyalty Segment",
    y_label="Total Sales"
)

st.dataframe(
    loyalty_gender_pivot,
    width="stretch"
)
