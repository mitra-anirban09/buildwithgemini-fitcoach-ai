"""Fitness and macronutrient calculation tools for FitCoach AI."""


def calculate_macros_and_zones(
    weight_kg: float,
    height_cm: float,
    age: int,
    gender: str = "male",
    activity_level: str = "moderate",
    goal: str = "maintain",
) -> str:
    """Calculate daily caloric needs, macronutrient targets, and training heart rate zones.

    Args:
        weight_kg: Body weight in kilograms (e.g., 75.0).
        height_cm: Height in centimeters (e.g., 178.0).
        age: Age in years (e.g., 28).
        gender: Gender ('male' or 'female').
        activity_level: Activity multiplier ('sedentary', 'light', 'moderate', 'active', 'very_active').
        goal: Caloric target goal ('maintain', 'cut', 'bulk').

    Returns:
        Formatted summary string with calories, macros (g), and heart rate zones (BPM).
    """
    # 1. BMR (Mifflin-St Jeor)
    is_female = gender.strip().lower() == "female"
    bmr = (10 * weight_kg) + (6.25 * height_cm) - (5 * age) + (-161 if is_female else 5)

    # 2. Activity Multiplier
    activity_multipliers = {
        "sedentary": 1.2,
        "light": 1.375,
        "moderate": 1.55,
        "active": 1.725,
        "very_active": 1.9,
    }
    mult = activity_multipliers.get(activity_level.lower(), 1.55)
    tdee = bmr * mult

    # 3. Adjust for Goal
    goal_lower = goal.lower()
    if "cut" in goal_lower or "loss" in goal_lower:
        target_calories = tdee - 500
    elif "bulk" in goal_lower or "gain" in goal_lower:
        target_calories = tdee + 350
    else:
        target_calories = tdee

    # 4. Macros Calculation
    protein_g = round(weight_kg * 2.0)  # 2g per kg
    fat_calories = target_calories * 0.25  # 25% fat
    fat_g = round(fat_calories / 9.0)
    carb_calories = target_calories - (protein_g * 4.0) - fat_calories
    carb_g = round(max(0.0, carb_calories / 4.0))

    # 5. Heart Rate Training Zones (Est Max HR = 220 - age)
    max_hr = 220 - age
    z1 = f"{round(max_hr * 0.50)}-{round(max_hr * 0.60)} BPM"
    z2 = f"{round(max_hr * 0.60)}-{round(max_hr * 0.70)} BPM"
    z3 = f"{round(max_hr * 0.70)}-{round(max_hr * 0.80)} BPM"
    z4 = f"{round(max_hr * 0.80)}-{round(max_hr * 0.90)} BPM"
    z5 = f"{round(max_hr * 0.90)}-{round(max_hr * 1.00)} BPM"

    return (
        f"--- Daily Nutrition Targets ({goal.upper()}) ---\n"
        f"Target Calories: {round(target_calories)} kcal/day (BMR: {round(bmr)}, TDEE: {round(tdee)})\n"
        f"Protein: {protein_g}g ({protein_g * 4} kcal)\n"
        f"Carbohydrates: {carb_g}g ({carb_g * 4} kcal)\n"
        f"Fats: {fat_g}g ({round(fat_calories)} kcal)\n\n"
        f"--- Heart Rate Training Zones (Max HR: {max_hr} BPM) ---\n"
        f"Zone 1 (Warmup/Recovery): {z1}\n"
        f"Zone 2 (Endurance/Fat Burn): {z2}\n"
        f"Zone 3 (Aerobic Fitness): {z3}\n"
        f"Zone 4 (Anaerobic Threshold): {z4}\n"
        f"Zone 5 (Max Effort): {z5}"
    )
