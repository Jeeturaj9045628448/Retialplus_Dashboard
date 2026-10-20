from __future__ import annotations
import io
import numpy as np
import pandas as pd
import streamlit as st
import plotly.express as px
from sklearn.ensemble import RandomForestRegressor, RandomForestClassifier
from sklearn.metrics import mean_absolute_error, accuracy_score, roc_auc_score
from sklearn.model_selection import train_test_split

st.set_page_config(page_title="RetailPulse | Retail Intelligence", page_icon="📈", layout="wide")
st.markdown("<style>.block-container{padding-top:1.5rem}.metric-card{border:1px solid #263449;border-radius:12px;padding:12px}</style>", unsafe_allow_html=True)
st.title("📈 RetailPulse")
st.caption("AI-Powered Customer Analytics & Demand Forecasting Platform · Portfolio prototype")

@st.cache_data
def sample_data():
    rng=np.random.default_rng(42)
    dates=pd.date_range(end=pd.Timestamp.today().normalize(), periods=365, freq='D')
    rows=[]
    products=[('P001','Beverages',18),('P002','Snacks',12),('P003','Household',35),('P004','Personal Care',28),('P005','Dairy',8)]
    for d in dates:
        for pid,cat,price in products:
            qty=max(0,int(rng.poisson(20+8*np.sin(2*np.pi*d.dayofyear/365)+3*(d.dayofweek>=5))))
            rows.append((d,pid,cat,price,qty,qty*price))
    sales=pd.DataFrame(rows,columns=['date','product_id','category','unit_price','quantity','sales'])
    customers=[]
    for i in range(1,301):
        recency=int(rng.integers(1,120)); frequency=int(rng.integers(1,30)); monetary=float(frequency*rng.uniform(15,100))
        churn=int(recency>75 and frequency<8)
        customers.append((f'C{i:04d}',recency,frequency,round(monetary,2),churn))
    return sales,pd.DataFrame(customers,columns=['customer_id','recency_days','frequency','monetary','churn'])

sales, customers=sample_data()
with st.sidebar:
    st.header('Data')
    uploaded=st.file_uploader('Upload sales CSV (optional)',type=['csv'])
    st.caption('Expected columns: date, product_id, category, unit_price, quantity. A reproducible synthetic dataset is used by default.')
if uploaded:
    try:
        incoming=pd.read_csv(uploaded)
        required={'date','product_id','category','unit_price','quantity'}
        if not required.issubset(incoming.columns): st.error('CSV missing columns: '+', '.join(sorted(required-set(incoming.columns))))
        else:
            incoming['date']=pd.to_datetime(incoming['date'],errors='coerce')
            for c in ['unit_price','quantity']: incoming[c]=pd.to_numeric(incoming[c],errors='coerce')
            incoming=incoming.dropna(subset=['date','product_id','category','unit_price','quantity'])
            incoming['sales']=incoming['unit_price']*incoming['quantity']
            if len(incoming): sales=incoming
            else: st.warning('No valid rows found; using sample data.')
    except Exception as e: st.error(f'Could not read CSV: {e}')

sales['date']=pd.to_datetime(sales['date'])
sales['sales']=sales['unit_price']*sales['quantity']
total=float(sales.sales.sum()); units=int(sales.quantity.sum()); products=int(sales.product_id.nunique())
a,b,c,d=st.columns(4)
a.metric('Total sales',f'₹{total:,.0f}'); b.metric('Units sold',f'{units:,}'); c.metric('Products',f'{products:,}'); d.metric('Daily avg. sales',f'₹{sales.groupby("date").sales.sum().mean():,.0f}')

sales_tab, forecast_tab, customer_tab, inventory_tab, mlops_tab=st.tabs(['Overview','Demand Forecasting','Customer Analytics','Inventory','Model Monitoring'])
with sales_tab:
    daily=sales.groupby('date',as_index=False).agg(sales=('sales','sum'),quantity=('quantity','sum'))
    st.subheader('Sales trend')
    st.plotly_chart(px.line(daily,x='date',y='sales',title='Daily revenue'),use_container_width=True)
    left,right=st.columns(2)
    left.plotly_chart(px.bar(sales.groupby('category',as_index=False).sales.sum(),x='category',y='sales',title='Revenue by category'),use_container_width=True)
    right.plotly_chart(px.bar(sales.groupby('product_id',as_index=False).quantity.sum(),x='product_id',y='quantity',title='Units by product'),use_container_width=True)
    st.download_button('Download current sales data',sales.to_csv(index=False).encode(),file_name='retailpulse_sales.csv',mime='text/csv')
with forecast_tab:
    st.subheader('Daily demand forecast')
    daily=sales.groupby('date',as_index=False).quantity.sum().sort_values('date')
    horizon=st.slider('Forecast horizon (days)',7,60,14)
    if len(daily)>=21:
        daily['lag_1']=daily.quantity.shift(1); daily['lag_7']=daily.quantity.shift(7); daily['rolling_7']=daily.quantity.shift(1).rolling(7).mean(); daily['dow']=daily.date.dt.dayofweek; daily['dayofyear']=daily.date.dt.dayofyear
        model_df=daily.dropna().copy(); features=['lag_1','lag_7','rolling_7','dow','dayofyear']
        if len(model_df)>10:
            split=max(1,int(len(model_df)*.8)); train=model_df.iloc[:split]; test=model_df.iloc[split:]
            model=RandomForestRegressor(n_estimators=120,random_state=42,min_samples_leaf=2); model.fit(train[features],train.quantity)
            pred=model.predict(test[features]); mae=mean_absolute_error(test.quantity,pred)
            st.metric('Holdout MAE (units/day)',f'{mae:.2f}')
            history=list(daily.quantity.astype(float)); future=[]
            for step in range(horizon):
                date=daily.date.max()+pd.Timedelta(days=step+1)
                row=pd.DataFrame([{'lag_1':history[-1],'lag_7':history[-7] if len(history)>=7 else history[-1],'rolling_7':float(np.mean(history[-7:])),'dow':date.dayofweek,'dayofyear':date.dayofyear}])
                value=max(0,float(model.predict(row[features])[0])); future.append((date,value)); history.append(value)
            fdf=pd.DataFrame(future,columns=['date','forecast_units'])
            hist=daily.tail(60)[['date','quantity']].rename(columns={'quantity':'units'}); combined=pd.concat([hist.rename(columns={'units':'value'}),fdf.rename(columns={'forecast_units':'value'})],ignore_index=True); combined['type']=['Historical']*len(hist)+['Forecast']*len(fdf)
            st.plotly_chart(px.line(combined,x='date',y='value',color='type',title='Historical demand and forecast'),use_container_width=True)
            st.dataframe(fdf,use_container_width=True)
            st.download_button('Download forecast CSV',fdf.to_csv(index=False).encode(), 'demand_forecast.csv','text/csv')
    else: st.warning('At least 21 daily observations are needed for this forecast.')
with customer_tab:
    st.subheader('Customer RFM-style analysis and churn risk')
    customers['segment']=np.select([customers.recency_days<=30,customers.frequency>=20,customers.recency_days>75],['Recent','Loyal / frequent','At risk'],default='Needs nurture')
    st.plotly_chart(px.scatter(customers,x='frequency',y='monetary',color='segment',size='recency_days',hover_data=['customer_id'],title='Customer segments'),use_container_width=True)
    X=customers[['recency_days','frequency','monetary']]; y=customers.churn
    if y.nunique()>1:
        Xtr,Xte,ytr,yte=train_test_split(X,y,test_size=.25,random_state=42,stratify=y)
        clf=RandomForestClassifier(n_estimators=120,random_state=42,class_weight='balanced'); clf.fit(Xtr,ytr); probs=clf.predict_proba(Xte)[:,1]; preds=(probs>=.5).astype(int)
        m1,m2=st.columns(2); m1.metric('Holdout accuracy',f'{accuracy_score(yte,preds):.1%}')
        try: m2.metric('Holdout ROC-AUC',f'{roc_auc_score(yte,probs):.3f}')
        except ValueError: m2.metric('Holdout ROC-AUC','N/A')
    st.caption('Important: customer data is synthetic for demonstration. Metrics are not evidence of real-world performance.')
    st.dataframe(customers,use_container_width=True)
with inventory_tab:
    st.subheader('Safety-stock and reorder guidance')
    stats=sales.groupby(['product_id','category']).agg(avg_daily_demand=('quantity','mean'),std_daily_demand=('quantity','std'),sales=('sales','sum')).reset_index().fillna(0)
    lead=st.number_input('Supplier lead time (days)',min_value=1,max_value=60,value=7)
    service=st.select_slider('Target service level',options=['90%','95%','97.5%','99%'],value='95%'); z={'90%':1.28,'95%':1.645,'97.5%':1.96,'99%':2.326}[service]
    stats['safety_stock']=np.ceil(z*stats.std_daily_demand*np.sqrt(lead)).astype(int); stats['reorder_point']=np.ceil(stats.avg_daily_demand*lead+stats.safety_stock).astype(int)
    st.dataframe(stats.sort_values('reorder_point',ascending=False),use_container_width=True)
    st.caption('Simplified calculation assumes demand variability is represented by the sample standard deviation and lead time is fixed.')
with mlops_tab:
    st.subheader('Basic data-drift monitor')
    recent=sales[sales.date>=sales.date.max()-pd.Timedelta(days=30)].quantity
    previous=sales[(sales.date<sales.date.max()-pd.Timedelta(days=30)) & (sales.date>=sales.date.max()-pd.Timedelta(days=60))].quantity
    if len(recent) and len(previous):
        old=float(previous.mean()); new=float(recent.mean()); pct=(new-old)/old*100 if old else 0
        x,y,z=st.columns(3); x.metric('Previous 30-day avg units',f'{old:.2f}'); y.metric('Recent 30-day avg units',f'{new:.2f}'); z.metric('Mean change',f'{pct:+.1f}%')
        threshold=st.slider('Drift alert threshold (%)',5,50,20)
        if abs(pct)>=threshold: st.warning('Potential demand drift: mean change exceeds the selected threshold.')
        else: st.success('No mean-shift alert at the selected threshold.')
    else: st.info('More than 30 days of sales data is needed for the comparison.')
    st.caption('This is a simple mean-shift check, not a full production drift-detection service or MLflow deployment.')

st.divider(); st.caption('RetailPulse portfolio prototype · Replace synthetic data with approved business data before operational use.')
