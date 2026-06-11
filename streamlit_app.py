import pandas as pd
import streamlit as st

from ml_engine import DEFAULT_CSV, ChurnEngine

st.set_page_config(
    page_title="Bank Customer Churn Analysis",
    page_icon="",
    layout="wide",
)


@st.cache_resource(show_spinner="Loading churn dataset and training model...")
def load_engine() -> ChurnEngine:
    engine = ChurnEngine()
    if DEFAULT_CSV.exists():
        engine.load_csv(DEFAULT_CSV, source_label=DEFAULT_CSV.name)
    return engine


def distribution_chart(title: str, rows: list[dict], index_col: str = "label") -> None:
    st.subheader(title)
    df = pd.DataFrame(rows)
    if df.empty:
        st.info("No data available.")
        return
    st.dataframe(df, use_container_width=True)
    if "rate" in df.columns:
        st.bar_chart(df.set_index(index_col)["rate"])
    elif "count" in df.columns:
        st.bar_chart(df.set_index(index_col)["count"])


st.title("Bank Customer Churn Analysis")
st.caption(f"Using backend dataset: {DEFAULT_CSV.as_posix()}")

engine = load_engine()

if engine.df is None:
    st.error(
        "The backend CSV was not found. Add the file at "
        "`data/Churn_Modelling.csv` and redeploy the app."
    )
    st.stop()

tabs = st.tabs(
    [
        "Overview",
        "Data",
        "Distributions",
        "Segmentation",
        "Prediction",
        "Customer Lookup",
        "High-Risk Customers",
    ]
)

with tabs[0]:
    kpis = engine.kpis()
    metric_cols = st.columns(5)
    metric_cols[0].metric("Total Customers", f"{kpis['total_customers']:,}")
    metric_cols[1].metric("Churned", f"{kpis['churned_customers']:,}")
    metric_cols[2].metric("Churn Rate", f"{kpis['churn_rate']:.2f}%")
    metric_cols[3].metric("Retention Rate", f"{kpis['retention_rate']:.2f}%")
    metric_cols[4].metric("Avg Credit Score", f"{kpis['avg_credit_score']:.1f}")

    st.subheader("Model Metrics")
    model_cols = st.columns(5)
    for col, key in zip(model_cols, ["accuracy", "precision", "recall", "f1", "roc_auc"], strict=False):
        col.metric(key.replace("_", " ").title(), f"{engine.metrics.get(key, 0):.3f}")

    st.subheader("Feature Importance")
    importance_df = pd.DataFrame(engine.feature_importance)
    st.dataframe(importance_df, use_container_width=True)
    st.bar_chart(importance_df.set_index("feature")["importance"])

    st.subheader("Monthly Churn Signal")
    monthly_df = pd.DataFrame(engine.monthly_trend())
    st.dataframe(monthly_df, use_container_width=True)
    if not monthly_df.empty:
        metric_col = "rate" if "rate" in monthly_df.columns else "churn_rate" if "churn_rate" in monthly_df.columns else None
        if metric_col:
            st.line_chart(monthly_df.set_index("month")[metric_col])
        else:
            st.info("Monthly trend data is available but does not include a rate column.")

with tabs[1]:
    st.subheader("Dataset Preview")
    preview_rows = st.slider("Preview rows", 10, 200, 50, key="preview_rows")
    st.dataframe(engine.df.head(preview_rows), use_container_width=True)

    st.subheader("Cleaning Summary")
    summary = engine.cleaning_summary()
    summary_cols = st.columns(3)
    summary_cols[0].metric("Rows", f"{summary['rows']:,}")
    summary_cols[1].metric("Columns", f"{summary['columns']:,}")
    summary_cols[2].metric("Duplicates Removed", summary["duplicates_removed"])

    detail_left, detail_right = st.columns(2)
    detail_left.write("Missing values")
    detail_left.dataframe(
        pd.DataFrame(summary["missing_values"].items(), columns=["column", "missing"]),
        use_container_width=True,
    )
    detail_right.write("Data types")
    detail_right.dataframe(
        pd.DataFrame(summary["dtypes"].items(), columns=["column", "dtype"]),
        use_container_width=True,
    )

with tabs[2]:
    dist_cols = st.columns(2)
    with dist_cols[0]:
        distribution_chart("Age Groups", engine.age_groups())
        distribution_chart("Credit Score Buckets", engine.credit_buckets())
        distribution_chart("Products Distribution", engine.products_dist())
    with dist_cols[1]:
        distribution_chart("Balance Buckets", engine.balance_buckets())
        distribution_chart("Tenure Distribution", engine.tenure_dist())
        geography = engine.distribution("Geography")
        distribution_chart("Geography Distribution", geography)

    st.subheader("Custom Distribution")
    selected_col = st.selectbox("Column", list(engine.df.columns))
    custom_rows = engine.distribution(selected_col)
    distribution_chart(f"{selected_col} Distribution", custom_rows)

    st.subheader("Correlation Matrix")
    corr = engine.correlation()
    corr_df = pd.DataFrame(corr["matrix"], index=corr["labels"], columns=corr["labels"])
    st.dataframe(corr_df, use_container_width=True)

with tabs[3]:
    st.subheader("Customer Segments")
    segment_df = pd.DataFrame(engine.segmentation())
    st.dataframe(segment_df, use_container_width=True)
    st.bar_chart(segment_df.set_index("segment")["churn_rate"])

with tabs[4]:
    st.subheader("Predict Churn Risk")
    left, right = st.columns(2)
    payload = {
        "CreditScore": left.number_input("Credit Score", 300, 900, 600),
        "Age": left.number_input("Age", 18, 100, 35),
        "Tenure": left.number_input("Tenure", 0, 20, 5),
        "Balance": left.number_input("Balance", 0.0, 500000.0, 0.0),
        "NumOfProducts": right.number_input("Number Of Products", 1, 4, 1),
        "HasCrCard": 1 if right.checkbox("Has Credit Card", value=True) else 0,
        "IsActiveMember": 1 if right.checkbox("Is Active Member", value=True) else 0,
        "EstimatedSalary": right.number_input("Estimated Salary", 0.0, 500000.0, 50000.0),
        "Geography": right.selectbox("Geography", sorted(engine.df["Geography"].dropna().unique())),
        "Gender": right.selectbox("Gender", sorted(engine.df["Gender"].dropna().unique())),
    }

    if st.button("Predict Churn Risk", type="primary"):
        prediction = engine.predict_single(payload)
        result_cols = st.columns(3)
        result_cols[0].metric("Prediction", prediction["prediction"])
        result_cols[1].metric("Risk Level", prediction["risk_level"])
        result_cols[2].metric("Churn Probability", f"{prediction['churn_probability']:.2f}%")

        if prediction.get("risk_factors"):
            st.write("Risk factors")
            st.write(prediction["risk_factors"])

with tabs[5]:
    st.subheader("Find Customer")
    min_id = int(engine.df["CustomerId"].min())
    max_id = int(engine.df["CustomerId"].max())
    customer_id = st.number_input("Customer ID", min_id, max_id, min_id)

    if st.button("Load Customer"):
        customer = engine.find_customer(int(customer_id))
        if customer is None:
            st.warning("Customer not found.")
        else:
            lookup_cols = st.columns(4)
            lookup_cols[0].metric("Customer ID", customer["customer_id"])
            lookup_cols[1].metric("Surname", customer["surname"])
            lookup_cols[2].metric("Actual Exited", customer["exited_actual"])
            lookup_cols[3].metric("Churn Probability", f"{customer['churn_probability']:.2f}%")

            st.write("Profile")
            st.dataframe(pd.DataFrame([customer["profile"]]), use_container_width=True)
            if customer.get("risk_factors"):
                st.write("Risk factors")
                st.write(customer["risk_factors"])

with tabs[6]:
    st.subheader("High-Risk Customers")
    limit = st.slider("Rows", 10, 200, 50, key="risk_rows")
    st.dataframe(pd.DataFrame(engine.high_risk_customers(limit)), use_container_width=True)
