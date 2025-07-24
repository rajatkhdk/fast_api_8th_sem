# from fastapi import FastAPI, Request
# from pydantic import BaseModel
# from typing import List

# app = FastAPI()

# # Example Pydantic model for request
# class WorkoutRequest(BaseModel):
#     age: int
#     height: float
#     weight: float
#     goal: str
#     equipment: List[str]

# # Example endpoint
# @app.post("/generate-workout")
# def generate_workout(data: WorkoutRequest):
#     # Your logic here
#     bmi = data.weight / ((data.height / 100) ** 2)
#     plan = {
#         "goal": data.goal,
#         "bmi": round(bmi, 2),
#         "recommended": "HIIT" if data.goal.lower() == "fat loss" else "Strength Training"
#     }
#     return plan

from fastapi import FastAPI
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from typing import List
from workout_generator import generate_plan
from workout_planner import main
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