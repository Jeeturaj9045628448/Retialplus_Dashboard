        promo = 1.12 if date.day in (1, 15) else 1.0
        for idx, (pid, cat, price) in enumerate(products):
            qty = max(0, int(rng.poisson((18 + idx * 2) * season * weekend * promo)))
            rows.append((date, pid, cat, price, qty, qty * price,
                         f"ST{(date.dayofyear + idx) % 30 + 1:02d}",
                         ["In-Store", "Online", "Mobile App"][(date.dayofyear + idx) % 3]))
    sales = pd.DataFrame(rows, columns=[
        "date", "product_id", "category", "unit_price", "quantity",
        "sales", "store", "channel"
    ])

    n = 1000
    recency = rng.integers(1, 150, n)
    frequency = rng.integers(1, 45, n)
    monetary = np.round(frequency * rng.uniform(150, 1200, n), 2)
    churn = ((recency > 85) & (frequency < 12)).astype(int)
    customers = pd.DataFrame({
        "customer_id": [f"C{i:05d}" for i in range(1, n + 1)],
        "recency_days": recency,
        "frequency": frequency,
        "monetary": monetary,
        "churn": churn,
    })
    customers["segment"] = np.select(
        [customers.recency_days <= 30,
         customers.frequency >= 28,
         customers.recency_days >= 85],
        ["Recent / Active", "Loyal Customers", "At Risk"],
        default="Needs Nurturing"
    )
    return sales, customers

sales, customers = make_data()

# ---------- Sidebar ----------
with st.sidebar:
    st.markdown("## 📈 RetailPulse")
    st.caption("Retail Intelligence Workspace")
    page = st.radio(
        "NAVIGATION",
        ["🏠 Dashboard Overview", "📊 Sales Analytics", "👥 Customer Segmentation",
         "📈 Demand Forecasting", "📦 Inventory Optimization", "⚠️ Churn Analysis"],
        label_visibility="visible",
    )
    st.divider()
    st.markdown("### 🔎 Global Filters")
    uploaded = st.file_uploader("Upload sales CSV (optional)", type=["csv"])
    st.caption("Required columns: date, product_id, category, unit_price, quantity")
    if uploaded is not None:
        try:
            incoming = pd.read_csv(uploaded)
            required = {"date", "product_id", "category", "unit_price", "quantity"}
            if required.issubset(incoming.columns):
                incoming["date"] = pd.to_datetime(incoming["date"], errors="coerce")
                for col in ["unit_price", "quantity"]:
                    incoming[col] = pd.to_numeric(incoming[col], errors="coerce")
                incoming = incoming.dropna(subset=list(required))
                incoming["sales"] = incoming["unit_price"] * incoming["quantity"]
                incoming["store"] = incoming.get("store", "Uploaded Data")
                incoming["channel"] = incoming.get("channel", "Unknown")
                if not incoming.empty:
                    sales = incoming
                    st.success("Uploaded sales data loaded.")
            else:
                st.error("CSV is missing one or more required columns.")
        except Exception as exc:
            st.error(f"Could not read CSV: {exc}")

sales["date"] = pd.to_datetime(sales["date"], errors="coerce")
sales = sales.dropna(subset=["date", "unit_price", "quantity"]).copy()
sales["sales"] = sales["unit_price"] * sales["quantity"]
min_date = sales["date"].min().date()
max_date = sales["date"].max().date()
with st.sidebar:
    date_range = st.date_input("Date range", value=(min_date, max_date),
                               min_value=min_date, max_value=max_date)
    categories = sorted(sales["category"].dropna().unique().tolist())
    selected_categories = st.multiselect("Categories", categories, default=categories)
    channels = sorted(sales["channel"].dropna().unique().tolist())
    selected_channels = st.multiselect("Sales channels", channels, default=channels)

if isinstance(date_range, (tuple, list)) and len(date_range) == 2:
    start_date, end_date = date_range
else:
    start_date, end_date = min_date, max_date

filtered = sales[
    sales["date"].dt.date.between(start_date, end_date)
    & sales["category"].isin(selected_categories)
    & sales["channel"].isin(selected_channels)
].copy()
if filtered.empty:
    st.warning("No records match the selected filters. Please widen the date range or select more categories/channels.")
    st.stop()

def money(value):
    return f"₹{value:,.0f}"

def kpis(df):
    revenue = float(df["sales"].sum())
    units = int(df["quantity"].sum())
    transactions = len(df)
    avg_daily = df.groupby(df["date"].dt.date)["sales"].sum().mean()
    a, b, c, d = st.columns(4)
    a.metric("Total Revenue", money(revenue))
    b.metric("Units Sold", f"{units:,}")
    c.metric("Sales Records", f"{transactions:,}")
    d.metric("Avg. Daily Revenue", money(avg_daily if pd.notna(avg_daily) else 0))

def chart_theme(fig, height=360):
    fig.update_layout(
        template="plotly_dark", height=height, margin=dict(l=18, r=18, t=55, b=18),
        paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
        legend_title_text="", font=dict(family="Arial", color="#dce5f2"),
    )
    fig.update_xaxes(showgrid=False, zeroline=False)
    fig.update_yaxes(gridcolor="#263244", zeroline=False)
    return fig

# ---------- Pages ----------
if page == "🏠 Dashboard Overview":
    st.markdown("""
    <div class="hero">
      <span class="pill">PORTFOLIO DEMO</span><span class="pill">INTERACTIVE ANALYTICS</span>
      <h1>🚀 RetailPulse AI Analytics Platform</h1>
      <p>One workspace to understand sales, customers, future demand and inventory decisions.</p>
    </div>
    """, unsafe_allow_html=True)
    kpis(filtered)
    st.markdown("### 📌 Business Overview")
    left, right = st.columns(2)
    daily = filtered.groupby(filtered["date"].dt.date, as_index=False).agg(
        revenue=("sales", "sum"), units=("quantity", "sum"))
    left.plotly_chart(chart_theme(px.line(daily, x="date", y="revenue", title="Revenue Trend",
                                          markers=False)), use_container_width=True)
    cat = filtered.groupby("category", as_index=False)["sales"].sum().sort_values("sales", ascending=False)
    right.plotly_chart(chart_theme(px.bar(cat, x="category", y="sales", title="Revenue by Category",
                                          color="sales", color_continuous_scale="Blues")), use_container_width=True)
    a, b = st.columns(2)
    channel = filtered.groupby("channel", as_index=False)["sales"].sum()
    a.plotly_chart(chart_theme(px.pie(channel, names="channel", values="sales",
                                      hole=.55, title="Revenue Share by Channel")), use_container_width=True)
    stores = filtered.groupby("store", as_index=False)["sales"].sum().nlargest(10, "sales")
    b.plotly_chart(chart_theme(px.bar(stores.sort_values("sales"), x="sales", y="store",
                                      orientation="h", title="Top 10 Stores by Revenue")), use_container_width=True)
    st.info("Demo note: generated sample data is used unless you upload your own authorized sales CSV.")

elif page == "📊 Sales Analytics":
    st.title("📊 Sales Analytics")
    st.caption("Explore revenue, volume, channel mix and store performance using the sidebar filters.")
    kpis(filtered)
    daily = filtered.groupby(filtered["date"].dt.date, as_index=False).agg(
        revenue=("sales", "sum"), units=("quantity", "sum"))
    st.plotly_chart(chart_theme(px.line(daily, x="date", y="revenue", title="Daily Revenue Trend",
                                        markers=False)), use_container_width=True)
    left, right = st.columns(2)
    left.plotly_chart(chart_theme(px.bar(filtered.groupby("category", as_index=False)["sales"].sum(),
                                         x="category", y="sales", title="Sales by Category",
                                         color="category")), use_container_width=True)
    right.plotly_chart(chart_theme(px.pie(filtered.groupby("channel", as_index=False)["sales"].sum(),
