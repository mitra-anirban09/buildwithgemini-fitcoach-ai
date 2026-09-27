"""Seed script for Firestore exercises collection in FitCoach AI."""

from google.cloud import firestore

# IMPORTANT: Hardcoded GCP Project ID (do not use auth.default or env vars on Agent Platform)
PROJECT_ID = "qwiklabs-gcp-02-210a21fedfc2"


def seed_firestore() -> None:
    """Seeds sample exercises into the Firestore 'exercises' collection."""
    db = firestore.Client(project=PROJECT_ID)
    collection_ref = db.collection("exercises")

    seed_data = [
        {
            "exercise_id": "barbell_bench_press",
            "name": "Barbell Bench Press",
            "category": "Chest",
            "target_muscle": "Pectoralis Major",
            "equipment": "Barbell",
            "difficulty": "Intermediate",
            "description": "Lie on flat bench, lower bar to mid-chest, and press explosively.",
            "tags": ["chest", "push", "compound"],
        },
        {
            "exercise_id": "barbell_squat",
            "name": "Barbell Back Squat",
            "category": "Legs",
            "target_muscle": "Quadriceps & Glutes",
            "equipment": "Barbell",
            "difficulty": "Intermediate",
            "description": "Barbell across upper traps, squat down below parallel, press up.",
            "tags": ["legs", "squat", "compound"],
        },
        {
            "exercise_id": "dumbbell_row",
            "name": "Single-Arm Dumbbell Row",
            "category": "Back",
            "target_muscle": "Latissimus Dorsi",
            "equipment": "Dumbbell",
            "difficulty": "Beginner",
            "description": "One knee on bench, pull dumbbell to hip, squeezing the lat.",
            "tags": ["back", "pull", "hypertrophy"],
        },
        {
            "exercise_id": "pushups",
            "name": "Standard Push-Ups",
            "category": "Chest",
            "target_muscle": "Pectoralis Major & Triceps",
            "equipment": "Bodyweight",
            "difficulty": "Beginner",
            "description": "Plank posture, lower chest near floor and push up cleanly.",
            "tags": ["chest", "bodyweight", "calisthenics"],
        },
    ]

    for item in seed_data:
        doc_ref = collection_ref.document(item["exercise_id"])
        doc_ref.set(item)
        print(f"Seeded exercise: {item['exercise_id']} -> {item['name']}")


if __name__ == "__main__":
    seed_firestore()
