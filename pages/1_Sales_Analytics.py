    for column in [
        "gender",
        "city",
        "age_group",
        "customer_segment",
        "loyalty_segment",
        "preferred_channel",
    ]
    if column in filtered.columns
]

if "age" in filtered.columns:
    filtered["age"] = pd.to_numeric(
        filtered["age"], errors="coerce"
    )

    if "age_group" not in filtered.columns:
        filtered["age_group"] = pd.cut(
            filtered["age"],
            bins=[0, 18, 25, 35, 45, 55, 65, 120],
            labels=[
                "0-18",
                "19-25",
                "26-35",
                "36-45",
                "46-55",
                "56-65",
                "66+",
            ],
        )

        demographic_columns.append("age_group")


if demographic_columns:
    st.header("👥 Customer Demographics")

    for column in dict.fromkeys(demographic_columns):
        chart_data = (
            filtered.dropna(subset=[column])
            .groupby(column, as_index=False)["total_value"]
            .sum()
            .sort_values("total_value", ascending=False)
        )

        if not chart_data.empty:
            title = column.replace("_", " ").title()
            st.subheader(f"Sales by {title}")

            fig = px.bar(
                chart_data,
                x=column,
                y="total_value",
                title=f"Sales by {title}",
            )

            st.plotly_chart(fig, use_container_width=True)

    # Combined demographic breakdowns
    combinations = [
        ("preferred_channel", "age_group"),
        ("city", "age_group"),
        ("gender", "age_group"),
        ("loyalty_segment", "age_group"),
        ("preferred_channel", "loyalty_segment"),
        ("gender", "loyalty_segment"),
        ("city", "loyalty_segment"),
        ("preferred_channel", "gender"),
        ("city", "preferred_channel"),
        ("city", "gender"),
        ("loyalty_segment", "gender"),
    ]

    for first, second in combinations:
        if first in filtered.columns and second in filtered.columns:
            combo_data = filtered.dropna(
                subset=[first, second]
            )

            summary = (
                combo_data.groupby(
                    [first, second],
                    as_index=False,
                    observed=True,
                )["total_value"]
                .sum()
            )

            if not summary.empty:
                first_name = first.replace("_", " ").title()
                second_name = second.replace("_", " ").title()

                st.subheader(
                    f"Sales by {first_name} & {second_name}"
                )

                fig = px.bar(
                    summary,
                    x=first,
                    y="total_value",
                    color=second,
                    barmode="group",
                    title=f"{first_name} & {second_name}",
                )

                st.plotly_chart(fig, use_container_width=True)

else:
    st.info(
        "Customer demographic charts ke liye "
        "cleaned_customer_master.csv mein customer_id aur "
        "demographic columns hone chahiye. "
        "Baaki sales charts available hain."
    )


st.caption(
    f"Sales data: {sales_path.name} · "
    f"Filtered rows: {len(filtered):,}"
)
