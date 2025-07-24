import pandas as pd
import numpy as np

# Macronutrient guidelines
MACRO_GUIDELINES = {
    "sedentary": {
        "fatloss":     {"protein_g_per_kg": (1.2, 1.6), "fat_pct": 30, "carb_pct": 40},
        "musclegain":  {"protein_g_per_kg": (1.4, 1.8), "fat_pct": 25, "carb_pct": 50},
        "strength":     {"protein_g_per_kg": (1.4, 1.8), "fat_pct": 30, "carb_pct": 45},
        "endurance":    {"protein_g_per_kg": (1.2, 1.5), "fat_pct": 25, "carb_pct": 55}
    },
    "light": {
        "fatloss":     {"protein_g_per_kg": (1.4, 1.8), "fat_pct": 30, "carb_pct": 40},
        "musclegain":  {"protein_g_per_kg": (1.6, 2.0), "fat_pct": 25, "carb_pct": 50},
        "strength":     {"protein_g_per_kg": (1.6, 2.0), "fat_pct": 25, "carb_pct": 50},
        "endurance":    {"protein_g_per_kg": (1.4, 1.6), "fat_pct": 25, "carb_pct": 55}
    },
    "moderate": {
        "fatloss":     {"protein_g_per_kg": (1.6, 2.0), "fat_pct": 30, "carb_pct": 40},
        "musclegain":  {"protein_g_per_kg": (1.8, 2.2), "fat_pct": 25, "carb_pct": 50},
        "strength":     {"protein_g_per_kg": (1.8, 2.2), "fat_pct": 25, "carb_pct": 50},
        "endurance":    {"protein_g_per_kg": (1.5, 1.8), "fat_pct": 20, "carb_pct": 60}
    },
    "active": {
        "fatloss":     {"protein_g_per_kg": (1.8, 2.2), "fat_pct": 30, "carb_pct": 40},
        "musclegain":  {"protein_g_per_kg": (2.0, 2.2), "fat_pct": 25, "carb_pct": 50},
        "strength":     {"protein_g_per_kg": (2.0, 2.2), "fat_pct": 25, "carb_pct": 50},
        "endurance":    {"protein_g_per_kg": (1.6, 1.8), "fat_pct": 20, "carb_pct": 60}
    },
    "very_active": {
        "fatloss":     {"protein_g_per_kg": (2.0, 2.4), "fat_pct": 30, "carb_pct": 40},
        "musclegain":  {"protein_g_per_kg": (2.0, 2.4), "fat_pct": 20, "carb_pct": 55},
        "strength":     {"protein_g_per_kg": (2.0, 2.4), "fat_pct": 25, "carb_pct": 50},
        "endurance":    {"protein_g_per_kg": (1.6, 2.0), "fat_pct": 20, "carb_pct": 60}
    }
}

def calculate_calories(weight_kg, height_cm, age, gender, activity_level, goal):
    if gender.lower() == 'male':
        bmr = 10 * weight_kg + 6.25 * height_cm - 5 * age + 5
    else:
        bmr = 10 * weight_kg + 6.25 * height_cm - 5 * age - 161

    activity_multipliers = {
        'sedentary': 1.2,
        'light': 1.375,
        'moderate': 1.55,
        'active': 1.725,
        'very active': 1.9
    }
    activity_multiplier = activity_multipliers.get(activity_level.lower(), 1.2)
    tdee = bmr * activity_multiplier

    goal = goal.lower()
    if goal == 'fat_loss':
        return tdee - 500
    elif goal == 'muscle_gain':
        return tdee + 300
    elif goal == 'endurance':
        return tdee + 150
    elif goal == 'strength':
        return tdee
    else:
        return tdee  # maintenance

def calculate_macros(goal, activity_level, tdee, weight_kg, fitness_level):
    goal = goal.lower()
    activity_level = activity_level.lower()
    fitness_level = fitness_level.lower()

    guidelines = MACRO_GUIDELINES[activity_level][goal]

    protein_range = guidelines["protein_g_per_kg"]
    if fitness_level == "beginner":
        protein_per_kg = protein_range[0]
    elif fitness_level == "intermediate":
        protein_per_kg = sum(protein_range) / 2
    elif fitness_level == "advanced":
        protein_per_kg = protein_range[1]
    else:
        raise ValueError("Invalid fitness_level")

    protein_g = round(protein_per_kg * weight_kg)
    protein_kcal = protein_g * 4

    fat_pct = guidelines["fat_pct"] / 100
    carb_pct = guidelines["carb_pct"] / 100
    total_pct = fat_pct + carb_pct

    remaining_kcal = tdee - protein_kcal
    fat_kcal = round((fat_pct / total_pct) * remaining_kcal)
    carb_kcal = round((carb_pct / total_pct) * remaining_kcal)

    fat_g = round(fat_kcal / 9)
    carb_g = round(carb_kcal / 4)

    # Calculate percentage contribution from total calories (tdee)
    protein_pct_of_total = (protein_kcal / tdee) * 100
    fat_pct_of_total = (fat_kcal / tdee) * 100
    carb_pct_of_total = (carb_kcal / tdee) * 100

    return {
        "calories_kcal": round(tdee),

        "protein_g": protein_g,
        "protein_kcal": protein_kcal,
        "protein_pct_of_total_kcal": round(protein_pct_of_total, 2),

        "fat_g": fat_g,
        "fat_kcal": fat_kcal,
        "fat_pct_of_total_kcal": round(fat_pct_of_total, 2),

        "carbohydrate_g": carb_g,
        "carb_kcal": carb_kcal,
        "carb_pct_of_total_kcal": round(carb_pct_of_total, 2),

        "total_kcal_from_macros": protein_kcal + fat_kcal + carb_kcal,
    }


# 🔑 Main callable function
def get_macros_from_user_input(data: dict):
    """
    Expected keys in `data`:
    - weight
    - height
    - age
    - gender
    - activity_level
    - goal
    - fitness_level
    """

    def normalize(value: str) -> str:
        return value.lower().replace(" ", "").replace("_", "")

    weight = data["weight"]
    height = data["height"]
    age = data["age"]
    gender = data["gender"]
    activity_level = normalize(data["activity_level"])
    goal = normalize(data["goal"])
    fitness_level = normalize(data["fitness_level"])

    tdee = calculate_calories(weight, height, age, gender, activity_level, goal)
    macros = calculate_macros(goal, activity_level, tdee, weight, fitness_level)
    return macros

