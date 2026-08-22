# Import necessary libraries
import numpy as np
import joblib  # For loading the serialized model
import pandas as pd  # For data manipulation
from flask import Flask, request, jsonify  # For creating the Flask API

# Initialize the Flask application
product_sales_predictor_api = Flask("Product Sales Predictor")

# Load the trained machine learning model
model = joblib.load("superkart_product_sales_prediction_model_v1_0.joblib")

# Define a route for the home page (GET request)
@product_sales_predictor_api.get('/')
def home():
    """
    This function handles GET requests to the root URL ('/') of the API.
    It returns a simple welcome message.
    """
    return "Welcome to the Product Sales Predictor API!"

# Define an endpoint for single property prediction (POST request)
@product_sales_predictor_api.post('/v1/productsales')
def predict_product_sales():
    """
    This function handles POST requests to the '/v1/productsales' endpoint.
    It expects a JSON payload containing property details and returns
    the predicted product sales as a JSON response.
    """
    # Get the JSON data from the request body
    product_data = request.get_json()

    # Extract relevant features from the JSON data
    request_data = {
        'Product_Id': product_data['Product_Id'],
        'Product_Weight': product_data['Product_Weight'],
        'Product_Sugar_Content': product_data['Product_Sugar_Content'],
        'Product_Allocated_Area': product_data['Product_Allocated_Area'],
        'Product_Type': product_data['Product_Type'],
        'Product_MRP': product_data['Product_MRP'],
        'Store_Id': product_data['Store_Id'],
        'Store_Establishment_Year': product_data['Store_Establishment_Year'],
        'Store_Size': product_data['Store_Size'],
        'Store_Location_City_Type': product_data['Store_Location_City_Type'],
        'Store_Type': product_data['Store_Type'],
        'Product_Type_Category': product_data['Product_Type_Category'],
        'store_age_years': product_data['store_age_years']
    }

    # Convert the extracted data into a Pandas DataFrame
    input_data = pd.DataFrame([request_data])

    # Make prediction for product sales
    predicted_product_sales = model.predict(input_data)[0]

    # Convert predicted_price to Python float
    predicted_product_sales = round(float(predicted_product_sales), 2)
    # The conversion above is needed as we convert the model prediction (log price) to actual price using np.exp, which returns predictions as NumPy float32 values.
    # When we send this value directly within a JSON response, Flask's jsonify function encounters a datatype error

    # Return the actual price
    return jsonify({'Predicted Product Sales (in dollars)': predicted_product_sales})


# Define an endpoint for batch prediction (POST request)
@product_sales_predictor_api.post('/v1/productsalesbatch')
def predict_product_sales_batch():
    """
    This function handles POST requests to the '/v1/productsalesbatch' endpoint.
    It expects a CSV file containing property details for multiple properties
    and returns the predicted product sales as a dictionary in the JSON response.
    """
    # Get the uploaded CSV file from the request
    file = request.files['file']

    # Read the CSV file into a Pandas DataFrame
    input_data = pd.read_csv(file)

    # Make predictions for all properties in the DataFrame (get log_prices)
    predicted_product_sales = model.predict(input_data).tolist()

    # Create a dictionary of predictions with property IDs as keys
    product_ids = input_data['Product_Id'].tolist()  # Assuming 'id' is the property ID column
    output_dict = dict(zip(product_ids, predicted_product_sales))  # Use actual prices

    # Return the predictions dictionary as a JSON response
    return output_dict

# Run the Flask application in debug mode if this script is executed directly
if __name__ == '__main__':
    product_sales_predictor_api.run(debug=True)
