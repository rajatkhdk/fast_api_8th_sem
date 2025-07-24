# workout_generator.py

def generate_plan(age, height, weight, goal, equipment):
    bmi = weight / ((height / 100) ** 2)

    if goal.lower() == "fat loss":
        recommended = "HIIT"
    elif goal.lower() == "muscle gain":
        recommended = "Strength Training"
    else:
        recommended = "Cardio + Flexibility"

    return {
        "goal": goal,
        "bmi": round(bmi, 2),
        "recommended": recommended
    }
