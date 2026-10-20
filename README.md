# RetailPulse — AI-Powered Customer Analytics & Demand Forecasting

A runnable portfolio prototype for retail analytics. It includes an interactive Streamlit dashboard, a lag-feature Random Forest demand forecast, RFM-style customer segmentation, a churn-risk demonstration model, inventory safety-stock guidance, CSV upload/download, and a basic mean-shift monitor.

> **Data and scope note:** The app generates synthetic data on first run. Customer labels are synthetic, and reported metrics are only a software demonstration—not validated business performance. The current package does not claim a deployed Prophet/LSTM model, MLflow server, Kubernetes cluster, cloud deployment, or production ETL pipeline.

## Requirements
- Windows 10/11
- Python 3.10–3.12 recommended
- Internet access for installing Python packages

## Run on Windows (PowerShell)
```powershell
cd RetailPulse
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
pip install -r requirements.txt
streamlit run app.py
```
The dashboard should open in your browser at `http://localhost:8501`.

If PowerShell blocks activation, use `Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass` in that terminal, then activate again.

## CSV upload format
The uploaded sales CSV must contain these columns:
`date, product_id, category, unit_price, quantity`

Example:
```csv
date,product_id,category,unit_price,quantity
2026-09-01,P001,Beverages,18,22
2026-09-01,P002,Snacks,12,31
```
The app calculates `sales = unit_price * quantity`. Use authorized, appropriately anonymized data only.

## Main modules
- **Overview:** revenue trends and product/category charts.
- **Demand Forecasting:** lag-feature Random Forest regression, time-ordered holdout MAE, iterative forecasts.
- **Customer Analytics:** RFM-style segments and a synthetic churn classification example.
- **Inventory:** simplified safety stock and reorder point estimates.
- **Model Monitoring:** basic recent-vs-previous mean-shift alert.
- **docs/original_interactive_dashboard.html:** original HTML dashboard recovered from the available project files.

## Limitations and next steps
1. Replace generated sample data with validated retail datasets.
2. Add time-series cross-validation and compare forecasting baselines before using predictions operationally.
3. Validate churn labels and use leakage-safe evaluation on real customer histories.
4. Add unit/integration tests, logging, a scheduled ETL process, and model versioning.
5. Add MLflow, Docker/Kubernetes, authentication, database integration, and CI/CD only when configured and tested in the target environment.

## Run a quick syntax check
```powershell
python -m py_compile app.py
```

## License
Add a license only after confirming the project ownership and submission requirements.
