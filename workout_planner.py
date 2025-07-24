#!/usr/bin/env python
# coding: utf-8

import pandas as pd
import numpy as np

def load_data(csv_path):
    """
    Load exercise data from a CSV file into a pandas DataFrame.
    Expected columns: 'Exercise', 'Difficulty', 'Primary Equipment', 'Secondary Equipment',
    'Target Muscle', 'Prime Mover', 'Movement Pattern', 'Plane', 'Program Type', etc.
    """
    try:
        df = pd.read_csv(csv_path)
    except Exception as e:
        print(f"Error loading CSV: {e}")
        return pd.DataFrame()
    return df

def filter_by_difficulty(df, fitness_level):
    """
    Filter exercises based on fitness level.
    Beginner: include only Beginner difficulty.
    Intermediate: include Beginner and Intermediate.
    Advanced: include Intermediate and Advanced.
    """
    if 'Difficulty Level' not in df.columns:
        return df
    level = fitness_level.lower()
    # print(level)
    # if level == 'beginner':
    #     mask = df['Difficulty'].str.lower() == 'beginner'
    # elif level == 'intermediate':
    #     mask = df['Difficulty'].str.lower().isin(['beginner', 'intermediate'])
    # else:  # advanced
    #     mask = df['Difficulty'].str.lower().isin(['intermediate', 'advanced'])

    # df['Difficulty Level'] = df['Difficulty Level'].astype(str).str.strip().str.lower()

    if level == 'beginner':
        mask = df['Difficulty Level'].str.lower().isin(['beginner', 'novice'])
        # print("Beginner")
        # print(mask)
    elif level == 'intermediate':
        mask = df['Difficulty Level'].str.lower().isin(['beginner', 'intermediate'])
        # print("Intermediate")
    else:  # advanced
        mask = df['Difficulty Level'].str.lower().isin(['intermediate', 'advanced'])
        # print("advanced")

    return df[mask].reset_index(drop=True)

def filter_by_equipment(df, equipment_list):
    """
    Filter exercises where:
    - Primary Equipment is in user's list (required)
    - Secondary Equipment is either empty/none or also in user's list
    """
    # Clean column names
    # df.columns = df.columns.str.strip()

    if 'Primary Equipment ' not in df.columns or 'Secondary Equipment' not in df.columns:
        print("Missing equipment columns.")
        return df

    # Prepare cleaned equipment list
    avail = set(eq.strip().lower() for eq in equipment_list)
    print("available")

    def equipment_ok(row):
        primary = str(row.get('Primary Equipment ', '')).strip().lower()
        secondary = str(row.get('Secondary Equipment', '')).strip().lower()

        # Primary equipment must match
        if primary not in avail:
            return False

        # Accept if secondary is missing or also in available equipment
        if secondary in ('', 'none', 'nan'):
            return True
        if secondary in avail:
            return True

        return False

    mask = df.apply(equipment_ok, axis=1)
    return df[mask].reset_index(drop=True)

# def filter_by_injury(df, injury_zones):
#     """
#     Exclude exercises that target or use injured areas.
#     injury_zones: list of body part strings.
#     """
#     if 'Target Muscle Group ' not in df.columns and 'Prime Mover Muscle' not in df.columns:
#         return df
#     inj = [x.lower() for x in injury_zones]
#     def not_injured(row):
#         target = str(row.get('Target Muscle Group ','')).lower()
#         prime = str(row.get('Prime Mover Muscle','')).lower()
#         for zone in inj:
#             if zone and (zone in target or zone in prime):
#                 return False
#         return True
#     mask = df.apply(not_injured, axis=1)
#     return df[mask].reset_index(drop=True)

def filter_by_program(df, goal):
    """
    Filter exercises by program type based on goal.
    Map fitness goals to training focus:
    - Strength, Hypertrophy, Conditioning.
    """
    if 'Program Type' not in df.columns:
        return df
    goal = goal.lower()
    goal_map = {
        'muscle gain': 'hypertrophy',
        'strength': 'strength',
        'endurance': 'conditioning',
        'fatloss': 'conditioning',
    }
    prog_type = goal_map.get(goal, None)
    if prog_type:
        mask = df['Program Type'].str.lower().str.contains(prog_type)
        return df[mask].reset_index(drop=True)
    return df

def generate_plan_split_simple(availability):
    """
    Create workout splits based only on the number of available days:
    - 3 days or fewer: Full Body workouts each day
    - 4 days: Upper/Lower split alternating
    - 5 or more days: Push/Pull/Legs cycle repeated
    
    Returns a dict like {'Day 1': ['Full Body'], 'Day 2': ['Full Body'], ...}
    """
    days = int(availability)
    plan = {}

    if days <= 3:
        # Full Body workouts for all days
        for i in range(days):
            plan[f"Day {i + 1}"] = ['Full Body']
    elif days == 4:
        # Upper/Lower split alternating
        split = ['Upper Body', 'Lower Body']
        for i in range(days):
            plan[f"Day {i + 1}"] = [split[i % 2]]
    else:
        # Push/Pull/Legs split cycling
        cycle = ['Push', 'Pull', 'Legs']
        for i in range(days):
            plan[f"Day {i + 1}"] = [cycle[i % 3]]

    return plan


import random

# Detailed goal mapping based on the image
GOAL_DETAILS = {
    "strength": {
        "sets": (3, 5, 6),
        "reps": (2, 4, 6),
        "rest": "2-5 min",
        "intensity": "85%+ 1RM"
    },
    "musclegain": {  # Hypertrophy
        "sets": (3, 5, 6),
        "reps": (6, 9, 12),
        "rest": "30-90 sec",
        "intensity": "67-85% 1RM"
    },
    "fatloss": {  # Treat similar to hypertrophy with higher reps
        "sets": (3, 4, 5),
        "reps": (10, 13, 15),
        "rest": "30-90 sec",
        "intensity": "67-75% 1RM"
    },
    "endurance": {
        "sets": (3, 4, 4),
        "reps": (12, 15, 20),
        "rest": "up to 30 sec",
        "intensity": "≤ 67% 1RM"
    }
}

def assemble_workout_plan(df, split_plan, goal, experience="beginner"):
    """
    Assemble a workout plan with exercises and set/rep/rest/intensity based on goal and experience.

    Args:
        df (pd.DataFrame): Exercise dataset.
        split_plan (dict): {'Day 1': ['Push'], 'Day 2': ['Pull'], ...}
        goal (str): Fitness goal like 'strength', 'fatloss', 'musclegain', 'endurance'.
        experience (str): 'beginner' or 'advanced'.

    Returns:
        dict: Plan with days as keys, and list of exercises with full prescription as values.
    """
    plan = {}
    goal_key = goal.lower().replace(" ", "")
    goal_data = GOAL_DETAILS.get(goal_key, GOAL_DETAILS["musclegain"])
    print(f'goal key : {goal_key}, goal data = {goal_data}')

    # Pick lower end for beginners, upper for advanced
    sets = goal_data["sets"][0] if experience == "beginner" else  goal_data["sets"][1] if experience == "intermediate" else  goal_data["sets"][2]
    reps = goal_data["reps"][0] if experience == "beginner" else goal_data["reps"][1] if experience == "intermediate" else goal_data["reps"][2]
    rest = goal_data["rest"]
    intensity = goal_data["intensity"]
    print(f'sets : {sets} and experience : {experience}')

    # Muscle group mapping
    muscle_map = {
        'Full Body': ['Chest', 'Back', 'Shoulders', 'Triceps', 'Biceps', 'Quadriceps', 'Hamstrings', 'Glutes'],
        'Upper Body': ['Chest', 'Back', 'Shoulders', 'Triceps', 'Biceps'],
        'Lower Body': ['Quadriceps', 'Hamstrings', 'Glutes', 'Calves'],
        'Push': ['Chest', 'Shoulders', 'Triceps'],
        'Pull': ['Back', 'Biceps'],
        'Legs': ['Quadriceps', 'Hamstrings', 'Glutes', 'Calves']
    }

    df.columns = df.columns.str.strip()

    for i, (day_label, day_type_list) in enumerate(split_plan.items(), start=1):
        day_type = day_type_list[0] if isinstance(day_type_list, list) else day_type_list
        target_muscles = muscle_map.get(day_type, [])
        selected_exercises = []

        for muscle in target_muscles:
            subset = df[df['Target Muscle Group'].str.contains(muscle, case=False, na=False)]
            if not subset.empty:
                import hashlib

                # Generate a deterministic seed from key features
                seed_input = f"{experience}_{goal_key}_{day_label}_{muscle}"
                seed = int(hashlib.sha256(seed_input.encode()).hexdigest(), 16) % (10**8)

                choice = subset.sample(1, random_state=seed).iloc[0]

                selected_exercises.append({
                    "exercise_name": choice['Exercise'],
                    "primary_muscle": muscle,
                    "sets": sets,
                    "reps": reps,
                    "rest": rest,
                    "intensity": intensity
                })

        plan[f'Day {i} - {day_type}'] = selected_exercises

    return plan




# GOAL_SETS_REPS = {
#     "strength": {"sets": 4, "reps": 4},
#     "fatloss": {"sets": 3, "reps": 12},
#     "musclegain": {"sets": 4, "reps": 8},
#     "endurance": {"sets": 2, "reps": 15}
# }

# def assemble_workout_plan(df, split_plan, goal):
#     df.columns = df.columns.str.strip()  # Remove leading/trailing spaces
#     plan = {}
#     goal_key = goal.lower().replace(" ", "")
#     sets_reps = GOAL_SETS_REPS.get(goal_key, {"sets": 3, "reps": 10})

#     for day, muscle_groups in split_plan.items():
#         day_exercises = []

#         for muscle in muscle_groups:
#             subset = df[df["Target Muscle Group"].str.contains(muscle, case=False, na=False)]
#             if not subset.empty:
#                 choice = subset.sample(n=1, random_state=42).iloc[0]
#                 day_exercises.append({
#                     "exercise_name": choice["Exercise Name"],
#                     "primary_muscle": choice["Primary Muscle"],
#                     "sets": sets_reps["sets"],
#                     "reps": sets_reps["reps"]
#                 })

#         plan[day] = day_exercises

#     return plan



primary_exercise_classification = {
    "fatloss": ["Calisthenics", "Ballistics", "Plyometric", "Animal Flow", "Bodybuilding"],
    "musclegain": ["Bodybuilding", "Powerlifting", "Olympic Weightlifting", "Grinds"],
    "strength": ["Bodybuilding", "Powerlifting", "Olympic Weightlifting", "Grinds"],
    "endurance": ["Calisthenics", "Ballistics", "Plyometric"],
    # "balance": ["Balance", "Mobility", "Postural"],
    # "athletic": ["Olympic Weightlifting", "Ballistics", "Plyometric"],
    # "explosive": ["Olympic Weightlifting", "Ballistics", "Plyometric"],
    # "mobility": ["Mobility", "Animal Flow"],
    # "flexibility": ["Mobility", "Animal Flow"]
}

def primary_classification(df, goal):
    # Step 1: Clean the goal string
    cleaned_goal = goal.lower().replace(" ", "")

    # Step 2: Check if the cleaned goal exists in the dictionary
    if cleaned_goal not in primary_exercise_classification:
        raise ValueError(f"Goal '{goal}' not recognized. Available goals: {list(primary_exercise_classification.keys())}")

    # Step 3: Get the allowed classifications for the goal
    allowed_classifications = primary_exercise_classification[cleaned_goal]
    print(allowed_classifications)

    # Step 4: Filter the DataFrame
    filtered_df = df[df["Primary Exercise Classification"].isin(allowed_classifications)].reset_index(drop=True)

    return filtered_df

def main(data):
    # # ====== Hardcoded Inputs for Testing ======
    # fitness_level = "Beginner"
    # goal = "fat loss"
    # availability = "3"  # Can convert to int later if needed
    # equipment_str = "Bodyweight,Dumbbell"
    # injury_str = "Shoulder,Spine"
    # age = "25"
    # gender = "Male"
    # height = "175"
    # weight = "70"
    # bmi = "22.9"

    equipment_available = [eq.strip() for eq in data.equipment_str.split(',') if eq.strip()]
    print(equipment_available)
    fitness_level = data.fitness_level.lower()
    # injury_zones = [iz.strip() for iz in data.injury_str.split(',') if iz.strip()]

    # Load dataset (e.g., 'exercise.csv')
    df = load_data('exercise.csv')
    # print(df.head())

     # Apply filters in sequence
    filtered = filter_by_difficulty(df, data.fitness_level)
    # print(filtered['Difficulty Level'].value_counts(dropna=False))
    filtered = filter_by_equipment(filtered, equipment_available)
    # print(filtered['Primary Equipment '].value_counts(dropna=False))
    # print(filtered['Secondary Equipment'].value_counts(dropna=False))
    # filtered = filter_by_injury(filtered, injury_zones)
    # print(filtered.shape)
    # filtered = filter_by_program(filtered, goal)
    # print(filtered.shape)
    filtered = primary_classification(filtered, data.goal)

    # # Generate workout split plan
    split_plan = generate_plan_split_simple(data.availability)
    print("Split plan:",split_plan)

    # # Assemble final workout plan
    workout_plan = assemble_workout_plan(filtered, split_plan, data.goal, fitness_level)

    # Print the plan dictionary
    print("\nFinal Workout Plan (Day-by-day):")
    print(workout_plan)
    print(filtered["Primary Exercise Classification"].value_counts())

    import json

    # Convert workout plan to JSON
    workout_json = json.dumps(workout_plan, indent=4)

    # Print or return to frontend
    print("\nWorkout Plan in JSON format:")
    print(workout_json)

    # Optionally return from main or send as API response
    return workout_json

