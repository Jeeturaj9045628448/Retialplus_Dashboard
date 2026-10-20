)

st.dataframe(
    city_age_pivot,
    width="stretch"
)

# Step 60: Sales by Customer Gender & Age Group

st.subheader("Sales by Customer Gender & Age Group")

gender_age_sales = sales.merge(
    customers[["cust_id", "gender", "age"]],
    left_on="customer_id",
    right_on="cust_id",
    how="left"
)

gender_age_sales["age_group"] = pd.cut(
    gender_age_sales["age"],
    bins=[0, 18, 25, 35, 45, 55, 65, 100],
    labels=[
        "0-18",
        "19-25",
        "26-35",
        "36-45",
        "46-55",
        "56-65",
        "66+"
    ]
)

gender_age_summary = (
    gender_age_sales
    .groupby(
        ["age_group", "gender"],
        observed=False
    )["total_value"]
    .sum()
    .reset_index()
)

gender_age_pivot = gender_age_summary.pivot(
    index="age_group",
    columns="gender",
    values="total_value"
).fillna(0)

st.bar_chart(
    gender_age_pivot,
    x_label="Age Group",
    y_label="Total Sales"
)

st.dataframe(
    gender_age_pivot,
    width="stretch"
)

# Step 62: Sales by Customer Loyalty Segment & Age Group

st.subheader("Sales by Customer Loyalty Segment & Age Group")

loyalty_age_sales = sales.merge(
    customers[["cust_id", "loyalty_segment", "age"]],
    left_on="customer_id",
    right_on="cust_id",
    how="left"
)

loyalty_age_sales["age_group"] = pd.cut(
    loyalty_age_sales["age"],
    bins=[0, 18, 25, 35, 45, 55, 65, 100],
    labels=[
        "0-18",
        "19-25",
        "26-35",
        "36-45",
        "46-55",
        "56-65",
        "66+"
    ]
)

loyalty_age_summary = (
    loyalty_age_sales
    .groupby(
        ["age_group", "loyalty_segment"],
        observed=False
    )["total_value"]
    .sum()
    .reset_index()
)

loyalty_age_pivot = loyalty_age_summary.pivot(
    index="age_group",
    columns="loyalty_segment",
    values="total_value"
).fillna(0)

st.bar_chart(
    loyalty_age_pivot,
    x_label="Age Group",
    y_label="Total Sales"
)

st.dataframe(
    loyalty_age_pivot,
    width="stretch"
)

# Step 64: Sales by Customer Preferred Channel & Loyalty Segment

st.subheader("Sales by Customer Preferred Channel & Loyalty Segment")

channel_loyalty_sales = sales.merge(
    customers[["cust_id", "preferred_channel", "loyalty_segment"]],
    left_on="customer_id",
    right_on="cust_id",
    how="left"
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
