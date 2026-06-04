#!/usr/bin/env python3
"""
seed.py — Populates the database with sample data for development/testing.
Run with: python server/seed.py  (from the project root)
"""

from datetime import date
from app import app
from models import db, Exercise, Workout, WorkoutExercise


def clear_tables():
    """Delete all rows in reverse dependency order to avoid FK violations."""
    WorkoutExercise.query.delete()
    Workout.query.delete()
    Exercise.query.delete()
    db.session.commit()
    print("✓ Tables cleared.")


def seed_exercises():
    exercises = [
        Exercise(name="Barbell Squat",      category="strength",    equipment_needed=True),
        Exercise(name="Push-Up",            category="strength",    equipment_needed=False),
        Exercise(name="Pull-Up",            category="strength",    equipment_needed=True),
        Exercise(name="Running",            category="cardio",      equipment_needed=False),
        Exercise(name="Cycling",            category="cardio",      equipment_needed=True),
        Exercise(name="Plank",              category="balance",     equipment_needed=False),
        Exercise(name="Downward Dog",       category="flexibility", equipment_needed=False),
        Exercise(name="Burpee",             category="hiit",        equipment_needed=False),
    ]
    db.session.add_all(exercises)
    db.session.commit()
    print(f"✓ {len(exercises)} exercises seeded.")
    return exercises


def seed_workouts():
    workouts = [
        Workout(date=date(2025, 6, 1),  duration_minutes=45,  notes="Upper-body focus."),
        Workout(date=date(2025, 6, 3),  duration_minutes=30,  notes="Quick cardio session."),
        Workout(date=date(2025, 6, 5),  duration_minutes=60,  notes="Full-body HIIT."),
        Workout(date=date(2025, 6, 7),  duration_minutes=50,  notes=None),
    ]
    db.session.add_all(workouts)
    db.session.commit()
    print(f"✓ {len(workouts)} workouts seeded.")
    return workouts


def seed_workout_exercises(exercises, workouts):
    squat, pushup, pullup, running, cycling, plank, downdog, burpee = exercises
    w1, w2, w3, w4 = workouts

    workout_exercises = [
        # Workout 1 — Upper body
        WorkoutExercise(workout=w1, exercise=pushup,  sets=4, reps=15, duration_seconds=None),
        WorkoutExercise(workout=w1, exercise=pullup,  sets=3, reps=8,  duration_seconds=None),
        WorkoutExercise(workout=w1, exercise=plank,   sets=3, reps=None, duration_seconds=60),

        # Workout 2 — Cardio
        WorkoutExercise(workout=w2, exercise=running, sets=1, reps=None, duration_seconds=1800),
        WorkoutExercise(workout=w2, exercise=cycling, sets=1, reps=None, duration_seconds=600),

        # Workout 3 — Full-body HIIT
        WorkoutExercise(workout=w3, exercise=burpee,  sets=5, reps=10, duration_seconds=None),
        WorkoutExercise(workout=w3, exercise=squat,   sets=4, reps=12, duration_seconds=None),
        WorkoutExercise(workout=w3, exercise=pushup,  sets=4, reps=20, duration_seconds=None),
        WorkoutExercise(workout=w3, exercise=plank,   sets=3, reps=None, duration_seconds=45),

        # Workout 4 — Flexibility & strength mix
        WorkoutExercise(workout=w4, exercise=downdog, sets=2, reps=None, duration_seconds=90),
        WorkoutExercise(workout=w4, exercise=squat,   sets=3, reps=10, duration_seconds=None),
    ]
    db.session.add_all(workout_exercises)
    db.session.commit()
    print(f"✓ {len(workout_exercises)} workout_exercises seeded.")


if __name__ == "__main__":
    with app.app_context():
        clear_tables()
        exercises = seed_exercises()
        workouts  = seed_workouts()
        seed_workout_exercises(exercises, workouts)
        print("\n🌱 Database seeded successfully!")
