import streamlit as st
import pandas as pd
import requests

# Base URL of the Flask backend
BACKEND_URL = "http://backend:7860"

# Set the title of the Streamlit app
st.title("Product Sales Predictor")

# Section for online prediction
st.subheader("Online Prediction")

# Collect user input for property features

Product_Id = st.text_input("Product Id")
Product_Weight = st.number_input("Product Weight", min_value=0.0, step=0.01, value=0.0)
Product_Sugar_Content = st.selectbox("Product Sugar Content", ["Low Sugar", "Medium Sugar", "High Sugar"])
Product_Allocated_Area = st.number_input("Product Allocated Area", min_value=0.0, step=0.01, value=0.0)
Product_Type = st.selectbox("Product Type", ["Fruits and Vegetables","Snack Foods","Frozen Foods","Dairy","Household","Baking Goods","Canned","Health and Hygiene","Meat","Soft Drinks","Breads","Hard Drinks","Others","Starchy Foods","Breakfast","Seafood"])
Product_MRP = st.number_input("Product MRP", min_value=0.0, step=0.01, value=0.0)
Store_Id = st.selectbox("Store Id", ["OUT004","OUT001","OUT003","OUT002"])


# compute derived variables before calling the model for prediction


#based on store id add other other store parameters

if Store_Id == "OUT001":
    Store_Establishment_Year = 1987
    Store_Size = "High"
    Store_Location_City_Type = "Tier 2"
    Store_Type = "Supermarket Type1"
elif Store_Id == "OUT002":
    Store_Establishment_Year = 1996
    Store_Size = "Small"
    Store_Location_City_Type = "Tier 3"
    Store_Type = "Food Mart"
elif Store_Id == "OUT003":
    Store_Establishment_Year = 1999
    Store_Size = "Medium"
    Store_Location_City_Type = "Tier 1"
    Store_Type = "Departmental Store"
else :
    Store_Establishment_Year = 2009
    Store_Size = "Medium"
    Store_Location_City_Type = "Tier 2"
    Store_Type = "Supermarket Type2"

#calculate the store_age_years
current_year = 2026
store_age_years = current_year - Store_Establishment_Year

#Derive product_type_categpry

# Mapping dictionary
category_map = {
          'FD': 'Perishables',
          'NC': 'Non-Perishables',
          'DR': 'Perishables'
}

# Extract first 2 characters (uppercased to handle lowercase user input)
prefix = Product_Id[:2].upper()

# Derive category (defaults to 'Unknown' or None if user enters an invalid prefix or empty input)
Product_Type_Category = category_map.get(prefix, 'Other')

# Convert user input into a DataFrame
input_data = pd.DataFrame([{
    "Product_Id":Product_Id,
    "Product_Weight":Product_Weight,
    "Product_Sugar_Content":Product_Sugar_Content,
    "Product_Allocated_Area":Product_Allocated_Area,
    "Product_Type":Product_Type,
    "Product_MRP":Product_MRP,
    "Store_Id":Store_Id,
    "Store_Establishment_Year":Store_Establishment_Year,
    "Store_Size":Store_Size ,
    "Store_Location_City_Type":Store_Location_City_Type,
    "Store_Type":Store_Type ,
    "Product_Type_Category":Product_Type_Category,
    "store_age_years":store_age_years,
}])

# Make prediction when the "Predict" button is clicked
if st.button("Predict", type="primary"):
    response = requests.post(f"{BACKEND_URL}/v1/productsales", json=input_data.to_dict(orient='records')[0])  # Send data to Flask API
    if response.status_code == 200:
        prediction = response.json()
        st.success(f"Predicted Product Sales (in dollars): {prediction}")
    else:
        st.error("Unable to connect to the prediction API.")

# Section for batch prediction
st.subheader("Batch Prediction")

# Allow users to upload a CSV file for batch prediction
uploaded_file = st.file_uploader("Upload CSV file for batch prediction", type=["csv"])

# Make batch prediction when the "Predict Batch" button is clicked
if uploaded_file is not None:
    if st.button("Predict Batch", type="primary"):
        response = requests.post(f"{BACKEND_URL}/v1/productsalesbatch", files={"file": uploaded_file})  # Send file to Flask API
        if response.status_code == 200:
            predictions = response.json()
            st.success("Batch predictions completed!")
            st.write(predictions)  # Display the predictions
        else:
            st.error("Unable to connect to the prediction API.")
