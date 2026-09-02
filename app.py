import streamlit as st
import pandas as pd
import joblib
from google import genai
import os
import json
if "GOOGLE_API_KEY" in os.environ:
    del os.environ["GOOGLE_API_KEY"]

loaded_model = joblib.load("churn_model.pkl")
def predict_churn(customer_data):
    probability = loaded_model.predict_proba(customer_data)[0, 1]

    if probability >= 0.35:
        prediction = "Likely to Churn"
    else:
        prediction = "Likely to Stay"

    return prediction,probability

client = genai.Client()

def generate_retention_plan(customer_info, churn_probability):
    prompt = f"""
Analyze this customer who has been predicted as likely to churn.

Customer information:
{customer_info}

Churn probability: {churn_probability:.0%}

Give:
1. 2-3 main risk factors.
2. 3 practical retention actions.
3. A short professional customer message.

Do not invent specific discounts, prices, plans, refunds, or company policies.
Base your analysis only on the customer information provided.

Return the answer as JSON with exactly these keys:

{{
    "risk_factors": ["factor 1", "factor 2"],
    "recommended_actions": ["action 1", "action 2", "action 3"],
    "customer_message": "short professional message"
}}
"""
    try:
        
        response = client.models.generate_content(
            model="gemini-3.6-flash",
            contents=prompt,
            config={
        "response_mime_type": "application/json"
    }
        )
        return json.loads(response.text)

    except Exception as e:
         return {
            "error": str(e)
        }

    return json.loads(response.text)

st.title("Customer Churn Prediction")
st.write("Enter customer information below.")
tenure = st.number_input("Tenure (months)", min_value=0, value=12)
monthly_charges = st.number_input("Monthly Charges",min_value=0.0,value=50.0)
total_charges = st.number_input("Total Charges",min_value=0.0,value=600.0)
gender = st.selectbox("Gender",["Female", "Male"])
partner = st.selectbox("Partner",["Yes", "No"])
dependents = st.selectbox("Dependents",["Yes", "No"])
internet_service = st.selectbox("Internet Service",["DSL", "Fiber optic", "No"])
contract = st.selectbox("Contract",["Month-to-month", "One year", "Two year"])
phone_service = st.selectbox("Phone Service", ["Yes", "No"])
multiple_lines = st.selectbox("Multiple Lines",["Yes", "No", "No phone service"])
online_security = st.selectbox("Online Security",["Yes", "No", "No internet service"])
online_backup = st.selectbox("Online Backup",["Yes", "No", "No internet service"])
device_protection = st.selectbox("Device Protection",["Yes", "No", "No internet service"])
tech_support = st.selectbox("Tech Support",["Yes", "No", "No internet service"])
streaming_movies = st.selectbox("Streaming Movies",["Yes", "No", "No internet service"])
streaming_tv = st.selectbox("Streaming TV",["Yes", "No", "No internet service"])
paperless_billing = st.selectbox("Paperless Billing",["Yes", "No"])
payment_method = st.selectbox("Payment Method",["Bank transfer (automatic)","Credit card (automatic)","Electronic check","Mailed check"])
customer_data = pd.DataFrame({
    "gender": [gender],
    "Partner": [partner],
    "Dependents": [dependents],
    "PhoneService": [phone_service],
    "MultipleLines": [multiple_lines],
    "InternetService": [internet_service],
    "OnlineSecurity": [online_security],
    "OnlineBackup": [online_backup],
    "DeviceProtection": [device_protection],
    "TechSupport": [tech_support],
    "StreamingMovies": [streaming_movies],
    "StreamingTV": [streaming_tv],
    "Contract": [contract],
    "PaperlessBilling": [paperless_billing],
    "PaymentMethod": [payment_method],
    "TotalCharges": [total_charges],
    "MonthlyCharges": [monthly_charges],
    "tenure": [tenure]
})


if st.button("Predict Churn"):

    prediction, probability = predict_churn(customer_data)
    st.subheader("👤 Customer Summary")
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Tenure", f"{tenure} months")

    with col2:
        st.metric("Monthly Charges", f"${monthly_charges:.2f}")

    with col3:
        st.metric("Contract", contract)
        
    col4, col5, col6 = st.columns(3)
    with col4:
        st.metric("Internet Service", internet_service)
    with col5:
        st.metric("Tech Support", tech_support)
    with col6:
        st.metric("Total Charges", f"${total_charges:.2f}")
        
    st.subheader("📊 Churn Prediction")
    with st.container(border=True):
        col1, col2 = st.columns(2)
        with col1:
            st.metric(
                "Churn Probability",
                f"{probability:.0%}"
            )
        with col2:
            st.metric(
                "Prediction",
                prediction
            )
        st.progress(probability)
        if prediction == "Likely to Churn":
            st.error("⚠️ This customer is at high risk of churn.")
        else:
            st.success("✅ This customer is likely to stay.")
        if prediction == "Likely to Churn":
            customer_info = {
                "Tenure": tenure,
                "MonthlyCharges": monthly_charges,
                "TotalCharges": total_charges,
                "InternetService": internet_service,
                "Contract": contract,
                "OnlineSecurity": online_security,
                "TechSupport": tech_support,
                "StreamingMovies": streaming_movies,
                "StreamingTV": streaming_tv,
                "PaymentMethod": payment_method}

            with st.spinner("🤖 AI is analyzing the customer..."):
                result = generate_retention_plan(customer_info, probability)
            if "error" in result:

                st.error("❌ Unable to generate AI retention analysis contact Toufiq.")
            else:
                with st.expander("🤖 AI Retention Analysis", expanded=True):

                    st.write("#### ⚠️ Risk Factors")

                    for factor in result["risk_factors"]:
                        st.warning(factor)

                    st.write("#### 💡 Recommended Actions")

                    for action in result["recommended_actions"]:
                        st.info(action)

                    st.write("#### 💬 Customer Message")

                    st.success(result["customer_message"])

            
        else:
             st.info("No retention action is required based on the current prediction.")
