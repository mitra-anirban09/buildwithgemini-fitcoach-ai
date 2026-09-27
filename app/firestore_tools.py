"""Firestore tools for FitCoach AI agent."""

from google.cloud import firestore

# IMPORTANT: Hardcode project ID as string (do NOT read from auth.default or GOOGLE_CLOUD_PROJECT)
PROJECT_ID = "qwiklabs-gcp-02-210a21fedfc2"


def _get_db_client() -> firestore.Client:
    """Returns a Firestore client initialized with hardcoded project ID."""
    return firestore.Client(project=PROJECT_ID)


def get_exercise(exercise_id: str) -> str:
    """Retrieve details for a specific exercise from the Firestore database.

    Args:
        exercise_id: The unique ID of the exercise (e.g., 'barbell_bench_press', 'barbell_squat').

    Returns:
        A formatted string describing the exercise details or a not found message.
    """
    db = _get_db_client()
    doc_ref = db.collection("exercises").document(exercise_id)
    doc = doc_ref.get()

    if not doc.exists:
        return f"Exercise '{exercise_id}' not found in the database."

    data = doc.to_dict()
    return (
        f"Exercise: {data.get('name')} (ID: {exercise_id})\n"
        f"Category: {data.get('category')}\n"
        f"Target Muscle: {data.get('target_muscle')}\n"
        f"Equipment: {data.get('equipment')}\n"
        f"Difficulty: {data.get('difficulty')}\n"
        f"Description: {data.get('description')}\n"
        f"Tags: {', '.join(data.get('tags', []))}"
    )


def list_exercises(category: str = "") -> str:
    """List available exercises from the Firestore database, optionally filtered by category.

    Args:
        category: Optional category filter (e.g., 'Chest', 'Legs', 'Back'). Case-insensitive.

    Returns:
        A list of exercises with their IDs, names, target muscles, and equipment.
    """
    db = _get_db_client()
    query = db.collection("exercises")

    docs = list(query.stream())
    results = []

    for doc in docs:
        data = doc.to_dict()
        doc_category = data.get("category", "")
        if category and category.lower() not in doc_category.lower():
            continue

        results.append(
            f"- {data.get('name')} [id: {doc.id}] | Category: {doc_category} | "
            f"Target: {data.get('target_muscle')} | Equipment: {data.get('equipment')}"
        )

    if not results:
        filter_msg = f" for category '{category}'" if category else ""
        return f"No exercises found in Firestore{filter_msg}."

    return "Available Exercises:\n" + "\n".join(results)


def add_exercise(
    exercise_id: str,
    name: str,
    category: str,
    target_muscle: str,
    equipment: str,
    difficulty: str,
    description: str,
) -> str:
    """Add or update an exercise in the Firestore database.

    Args:
        exercise_id: Unique slug/id for the exercise (e.g., 'dumbbell_curl').
        name: Display name (e.g., 'Dumbbell Bicep Curl').
        category: Body part or category (e.g., 'Arms', 'Chest', 'Core').
        target_muscle: Primary muscle worked (e.g., 'Biceps').
        equipment: Required equipment (e.g., 'Dumbbell', 'Machine').
        difficulty: Difficulty level ('Beginner', 'Intermediate', 'Advanced').
        description: Instructions or notes on form.

    Returns:
        Confirmation message.
    """
    db = _get_db_client()
    doc_ref = db.collection("exercises").document(exercise_id)
    doc_data = {
        "exercise_id": exercise_id,
        "name": name,
        "category": category,
        "target_muscle": target_muscle,
        "equipment": equipment,
        "difficulty": difficulty,
        "description": description,
        "tags": [category.lower(), equipment.lower()],
    }
    doc_ref.set(doc_data)
    return f"Successfully added/updated exercise '{name}' (ID: {exercise_id}) in Firestore."


def log_user_workout(
    workout_name: str,
    exercises_performed: str,
    duration_minutes: int,
    notes: str = "",
) -> str:
    """Log a completed workout to the Firestore 'user_workouts' collection.

    Args:
        workout_name: Title of the workout session (e.g., 'Upper Body Power').
        exercises_performed: Summary of exercises, sets, and reps completed.
        duration_minutes: Duration of session in minutes.
        notes: Optional coach or athlete notes.

    Returns:
        Confirmation message with logged document ID.
    """
    db = _get_db_client()
    doc_ref = db.collection("user_workouts").document()
    workout_data = {
        "workout_name": workout_name,
        "exercises_performed": exercises_performed,
        "duration_minutes": duration_minutes,
        "notes": notes,
    }
    doc_ref.set(workout_data)
    return f"Successfully logged workout '{workout_name}' (Doc ID: {doc_ref.id}) in Firestore."
