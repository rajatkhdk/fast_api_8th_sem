from fastapi import FastAPI
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from typing import List
from workout_generator import generate_plan
from workout_planner import main
from nutrient import get_macros_from_user_input
import json
import joblib
import numpy as np
import pandas as pd

app = FastAPI()

# Load model
scaler = joblib.load("calorie_burned/scaler.pkl")
poly = joblib.load("calorie_burned/poly.pkl")
model = joblib.load("calorie_burned/lasso_model.pkl")

# Define input schema
class CalorieInput(BaseModel):
    Gender: str
    Age: int
    Height: float
    Weight: float
    Duration: float
    Heart_Rate: float
    Body_Temp: float

def encode_gender(gender: str) -> int:
    return 0 if gender.lower() == "male" else 1

@app.post("/predict_calories")
def predict_calories(data: CalorieInput):
    # Convert gender
    gender_encoded = encode_gender(data.Gender)
    print(gender_encoded)

    # Define the actual user input as a DataFrame
    user_input = pd.DataFrame([{
    'Gender': gender_encoded,        # Will be encoded
    'Age': data.Age,
    'Height': data.Height,
    'Weight': data.Weight,
    'Duration': data.Duration,
    'Heart_Rate': data.Heart_Rate,
    'Body_Temp': data.Body_Temp,
}])

    # # Feature order should match training data!
    # features = np.array([[gender_encoded, data.age, data.bmi, data.duration, data.heart_rate, data.body_temp]])

    # Scale features using the same scaler
    user_scaled = scaler.transform(user_input)
    user_scaled_poly = poly.fit_transform(user_scaled)

    # Predict calories burned
    predicted_calories = model.predict(user_scaled_poly)[0]


    return {
        "predicted_calories": predicted_calories
    }

# ========== Input Schema ==========
class WorkoutRequest(BaseModel):
    fitness_level: str
    goal: str
    availability: int
    equipment_str: str
    age: int
    gender: str
    height: float
    weight: float
    

# @app.post("/workout_generation")
# def workout_generation(data: WorkoutRequest):
#     result = generate_plan(
#         age=data.age,
#         height=data.height,
#         weight=data.weight,
#         goal=data.goal,
#         equipment=data.equipment
#     )
#     return result

@app.post("/workout_planner")
def workout_generation(data: WorkoutRequest):
    print("Received Request:", data)
    result = main(data)
    workout_plan = json.loads(result)
    return JSONResponse(content=workout_plan)

# ========== Input Schema ==========
class NutritionRequest(BaseModel):
    fitness_level: str
    goal: str
    activity_level: str
    age: int
    gender: str
    height: float
    weight: float

# ========== Endpoint ==========
@app.post("/nutrition_plan")
def generate_nutrition_plan(data: NutritionRequest):
    print("Received Request:", data)

    # Convert Pydantic object to plain dict
    input_data = data.dict()

    # Call the nutrient calculator function
    result = get_macros_from_user_input(input_data)

    return JSONResponse(content=result)