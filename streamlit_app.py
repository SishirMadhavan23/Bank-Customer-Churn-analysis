from pathlib import Path
import tempfile

import pandas as pd
import streamlit as st

from ml_engine import DEFAULT_CSV, ChurnEngine


st.set_page_config(
    page_title="Bank Customer Churn Analysis",
    page_icon="",
    layout="wide",
)


@st.cache_resource(show_spinner=False)
def load_engine(path: str | None = None) -> ChurnEngine:
    engine = ChurnEngine()
    source = Path(path) if path else DEFAULT_CSV
    if source.exists():
        engine.load_csv(source, source_label=source.name)
    return engine


st.title("Bank Customer Churn Analysis")

uploaded_file = st.sidebar.file_uploader("Upload churn CSV", type=["csv"])
temp_path = None

if uploaded_file is not None:
    with tempfile.NamedTemporaryFile(delete=False, suffix=".csv") as temp_file:
        temp_file.write(uploaded_file.getbuffer())
        temp_path = temp_file.name

engine = load_engine(temp_path)

if engine.df is None:
    st.info(
        "Upload a churn CSV to begin. The file should include columns such as "
        "CreditScore, Age, Tenure, Balance, NumOfProducts, HasCrCard, "
        "IsActiveMember, EstimatedSalary, Geography, Gender, and Exited."
    )
    st.stop()

tab_overview, tab_predict, tab_customers = st.tabs(
    ["Overview", "Prediction", "High-Risk Customers"]
)

with tab_overview:
    kpis = engine.kpis()
    cols = st.columns(4)
    cols[0].metric("Customers", f"{kpis.get('total_customers', 0):,}")
    cols[1].metric("Churn Rate", f"{kpis.get('churn_rate', 0):.2f}%")
    cols[2].metric("Avg Age", f"{kpis.get('avg_age', 0):.1f}")
    cols[3].metric("Avg Balance", f"{kpis.get('avg_balance', 0):,.0f}")

    st.subheader("Model Metrics")
    metric_cols = st.columns(5)
    for col, key in zip(metric_cols, ["accuracy", "precision", "recall", "f1", "roc_auc"]):
        col.metric(key.replace("_", " ").title(), f"{engine.metrics.get(key, 0):.3f}")

    st.subheader("Feature Importance")
    importance_df = pd.DataFrame(engine.feature_importance)
    st.bar_chart(importance_df.set_index("feature"))

    st.subheader("Dataset Preview")
    st.dataframe(engine.df.head(25), use_container_width=True)

with tab_predict:
    st.subheader("Predict A Customer")
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
        st.metric(
            "Churn Probability",
            f"{prediction['churn_probability']:.2f}%",
            prediction["risk_level"],
        )
        if prediction.get("risk_factors"):
            st.write("Risk factors")
            st.write(prediction["risk_factors"])

with tab_customers:
    st.subheader("High-Risk Customers")
    limit = st.slider("Rows", 10, 100, 25)
    st.dataframe(pd.DataFrame(engine.high_risk_customers(limit)), use_container_width=True)
