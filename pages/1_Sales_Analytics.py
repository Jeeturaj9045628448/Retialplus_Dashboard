st.subheader("Sales by Customer Preferred Channel & Age Group")

channel_age_sales = sales.merge(
    customers[["cust_id", "preferred_channel", "age"]],
    left_on="customer_id",
    right_on="cust_id",
    how="left"
)

channel_age_sales["age_group"] = pd.cut(
    channel_age_sales["age"],
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

channel_age_sales_summary = (
    channel_age_sales
    .groupby(
        ["preferred_channel", "age_group"],
        observed=False
    )["total_value"]
    .sum()
    .reset_index()
)

channel_age_pivot = channel_age_sales_summary.pivot(
    index="age_group",
    columns="preferred_channel",
    values="total_value"
).fillna(0)

st.bar_chart(
    channel_age_pivot,
    x_label="Age Group",
    y_label="Total Sales"
)

st.dataframe(
    channel_age_summary if False else channel_age_pivot,
    width="stretch"
)

# Step 58: Sales by Customer City & Age Group

st.subheader("Sales by Customer City & Age Group")

city_age_sales = sales.merge(
    customers[["cust_id", "city", "age"]],
    left_on="customer_id",
    right_on="cust_id",
    how="left"
)

city_age_sales["age_group"] = pd.cut(
    city_age_sales["age"],
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

city_age_summary = (
    city_age_sales
    .groupby(
        ["city", "age_group"],
        observed=False
    )["total_value"]
    .sum()
    .reset_index()
)

city_age_pivot = city_age_summary.pivot(
    index="age_group",
    columns="city",
    values="total_value"
).fillna(0)

st.bar_chart(
    city_age_pivot,
    x_label="Age Group",
    y_label="Total Sales"
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
