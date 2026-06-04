from flask import Flask, make_response, request, jsonify
from flask_migrate import Migrate
from marshmallow import ValidationError
from datetime import date

from models import db, Exercise, Workout, WorkoutExercise
from schemas import (
    exercise_schema,
    exercises_schema,
    exercise_with_workouts_schema,
    workout_schema,
    workouts_schema,
    workout_with_exercises_schema,
    workout_exercise_schema,
)

app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///app.db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

migrate = Migrate(app, db)
db.init_app(app)


# ── Helper ────────────────────────────────────────────────────────────────────

def error_response(message, status=400):
    """Return a consistent JSON error envelope."""
    return make_response(jsonify({"error": message}), status)


# ── Workout Endpoints ─────────────────────────────────────────────────────────

@app.route("/workouts", methods=["GET"])
def get_workouts():
    """List all workouts (without nested exercises for brevity)."""
    workouts = Workout.query.all()
    return make_response(jsonify(workouts_schema.dump(workouts)), 200)


@app.route("/workouts/<int:id>", methods=["GET"])
def get_workout(id):
    """
    Show a single workout with its associated exercises and per-session details
    (reps, sets, duration_seconds) from the WorkoutExercise join table.
    """
    workout = db.session.get(Workout, id)
    if not workout:
        return error_response(f"Workout {id} not found.", 404)
    return make_response(jsonify(workout_with_exercises_schema.dump(workout)), 200)


@app.route("/workouts", methods=["POST"])
def create_workout():
    """Create a new workout. Expects JSON with: date, duration_minutes, notes (optional)."""
    data = request.get_json()
    if not data:
        return error_response("Request body must be JSON.")

    # Schema-level validation (marshmallow)
    try:
        validated = workout_schema.load(data)
    except ValidationError as exc:
        return error_response(exc.messages)

    # Model-level validation (SQLAlchemy @validates)
    try:
        workout = Workout(**validated)
        db.session.add(workout)
        db.session.commit()
    except (ValueError, Exception) as exc:
        db.session.rollback()
        return error_response(str(exc))

    return make_response(jsonify(workout_schema.dump(workout)), 201)


@app.route("/workouts/<int:id>", methods=["DELETE"])
def delete_workout(id):
    """
    Delete a workout by ID.
    Associated WorkoutExercise rows are removed automatically via cascade.
    """
    workout = db.session.get(Workout, id)
    if not workout:
        return error_response(f"Workout {id} not found.", 404)

    db.session.delete(workout)
    db.session.commit()
    return make_response(jsonify({"message": f"Workout {id} deleted."}), 200)


# ── Exercise Endpoints ────────────────────────────────────────────────────────

@app.route("/exercises", methods=["GET"])
def get_exercises():
    """List all exercises."""
    exercises = Exercise.query.all()
    return make_response(jsonify(exercises_schema.dump(exercises)), 200)


@app.route("/exercises/<int:id>", methods=["GET"])
def get_exercise(id):
    """Show a single exercise and the workouts it appears in."""
    exercise = db.session.get(Exercise, id)
    if not exercise:
        return error_response(f"Exercise {id} not found.", 404)
    return make_response(jsonify(exercise_with_workouts_schema.dump(exercise)), 200)


@app.route("/exercises", methods=["POST"])
def create_exercise():
    """Create a new exercise. Expects JSON with: name, category, equipment_needed (optional)."""
    data = request.get_json()
    if not data:
        return error_response("Request body must be JSON.")

    # Schema-level validation
    try:
        validated = exercise_schema.load(data)
    except ValidationError as exc:
        return error_response(exc.messages)

    # Model-level validation and uniqueness check (DB constraint will also catch duplicates)
    try:
        exercise = Exercise(**validated)
        db.session.add(exercise)
        db.session.commit()
    except (ValueError, Exception) as exc:
        db.session.rollback()
        return error_response(str(exc))

    return make_response(jsonify(exercise_schema.dump(exercise)), 201)


@app.route("/exercises/<int:id>", methods=["DELETE"])
def delete_exercise(id):
    """
    Delete an exercise by ID.
    Associated WorkoutExercise rows are removed automatically via cascade.
    """
    exercise = db.session.get(Exercise, id)
    if not exercise:
        return error_response(f"Exercise {id} not found.", 404)

    db.session.delete(exercise)
    db.session.commit()
    return make_response(jsonify({"message": f"Exercise {id} deleted."}), 200)


# ── WorkoutExercise Endpoint ──────────────────────────────────────────────────

@app.route(
    "/workouts/<int:workout_id>/exercises/<int:exercise_id>/workout_exercises",
    methods=["POST"],
)
def add_exercise_to_workout(workout_id, exercise_id):
    """
    Add an exercise to a workout with optional reps, sets, and duration_seconds.
    Both the workout and exercise must already exist.
    """
    workout = db.session.get(Workout, workout_id)
    if not workout:
        return error_response(f"Workout {workout_id} not found.", 404)

    exercise = db.session.get(Exercise, exercise_id)
    if not exercise:
        return error_response(f"Exercise {exercise_id} not found.", 404)

    data = request.get_json() or {}

    # Schema-level validation for the per-session fields
    try:
        validated = workout_exercise_schema.load(data)
    except ValidationError as exc:
        return error_response(exc.messages)

    try:
        we = WorkoutExercise(
            workout_id=workout_id,
            exercise_id=exercise_id,
            reps=validated.get("reps"),
            sets=validated.get("sets"),
            duration_seconds=validated.get("duration_seconds"),
        )
        db.session.add(we)
        db.session.commit()
    except (ValueError, Exception) as exc:
        db.session.rollback()
        return error_response(str(exc))

    return make_response(jsonify(workout_exercise_schema.dump(we)), 201)


if __name__ == "__main__":
    app.run(port=5555, debug=True)
