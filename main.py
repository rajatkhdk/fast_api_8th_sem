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

# Load model components
scaler = joblib.load("calorie_burned/scaler.pkl")
poly = joblib.load("calorie_burned/poly.pkl")
model = joblib.load("calorie_burned/lasso_model.pkl")

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

def predict_for_duration(data_dict):
    """Helper function to predict calories for a given input dict"""
    df = pd.DataFrame([data_dict])
    scaled = scaler.transform(df)
    poly_feat = poly.transform(scaled)
    pred = model.predict(poly_feat)[0]
    return pred

@app.post("/predict_calories")
def predict_calories(data: CalorieInput):
    gender_encoded = encode_gender(data.Gender)

    # Max chunk size (minutes)
    MAX_DURATION = 60

    # Total duration in minutes
    total_duration = data.Duration

    # Number of full chunks + remainder
    full_chunks = int(total_duration // MAX_DURATION)
    remainder = total_duration % MAX_DURATION

    calories_total = 0.0

    # Predict calories for each full chunk
    for _ in range(full_chunks):
        input_chunk = {
            'Gender': gender_encoded,
            'Age': data.Age,
            'Height': data.Height,
            'Weight': data.Weight,
            'Duration': MAX_DURATION,
            'Heart_Rate': data.Heart_Rate,
            'Body_Temp': data.Body_Temp
        }
        calories_total += predict_for_duration(input_chunk)

    # Predict calories for remainder duration if any
    if remainder > 0:
        input_remainder = {
            'Gender': gender_encoded,
            'Age': data.Age,
            'Height': data.Height,
            'Weight': data.Weight,
            'Duration': remainder,
            'Heart_Rate': data.Heart_Rate,
            'Body_Temp': data.Body_Temp
        }
        calories_total += predict_for_duration(input_remainder)

    return {
        "predicted_calories": round(calories_total, 2)
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