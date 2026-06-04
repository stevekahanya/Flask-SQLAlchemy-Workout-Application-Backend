from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import validates

db = SQLAlchemy()


class Exercise(db.Model):
    """Represents a reusable exercise that can be added to multiple workouts."""

    __tablename__ = "exercises"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, nullable=False, unique=True)  # Table constraint: name must be unique and present
    category = db.Column(db.String, nullable=False)           # Table constraint: category required
    equipment_needed = db.Column(db.Boolean, nullable=False, default=False)

    # Relationships
    workout_exercises = db.relationship(
        "WorkoutExercise", back_populates="exercise", cascade="all, delete-orphan"
    )
    workouts = db.relationship(
        "Workout", secondary="workout_exercises", back_populates="exercises", viewonly=True
    )

    @validates("name")
    def validate_name(self, key, value):
        """Name must be a non-empty string."""
        if not value or not value.strip():
            raise ValueError("Exercise name cannot be blank.")
        return value.strip()

    @validates("category")
    def validate_category(self, key, value):
        """Category must be one of the allowed values."""
        allowed = {"strength", "cardio", "flexibility", "balance", "hiit"}
        if value.lower() not in allowed:
            raise ValueError(f"Category must be one of: {', '.join(sorted(allowed))}.")
        return value.lower()

    def __repr__(self):
        return f"<Exercise id={self.id} name={self.name!r} category={self.category!r}>"


class Workout(db.Model):
    """Represents a single training session with a date, duration, and optional notes."""

    __tablename__ = "workouts"

    id = db.Column(db.Integer, primary_key=True)
    date = db.Column(db.Date, nullable=False)                  # Table constraint: date required
    duration_minutes = db.Column(db.Integer, nullable=False)   # Table constraint: duration required
    notes = db.Column(db.Text)

    # Relationships
    workout_exercises = db.relationship(
        "WorkoutExercise", back_populates="workout", cascade="all, delete-orphan"
    )
    exercises = db.relationship(
        "Exercise", secondary="workout_exercises", back_populates="workouts", viewonly=True
    )

    @validates("duration_minutes")
    def validate_duration(self, key, value):
        """Duration must be a positive integer (at least 1 minute)."""
        if not isinstance(value, int) or value < 1:
            raise ValueError("duration_minutes must be a positive integer (>= 1).")
        return value

    @validates("date")
    def validate_date(self, key, value):
        """Date must be provided."""
        if value is None:
            raise ValueError("Workout date is required.")
        return value

    def __repr__(self):
        return f"<Workout id={self.id} date={self.date} duration={self.duration_minutes}min>"


class WorkoutExercise(db.Model):
    """
    Join table linking a Workout to an Exercise.
    Stores per-session details: reps, sets, and/or duration in seconds.
    """

    __tablename__ = "workout_exercises"

    id = db.Column(db.Integer, primary_key=True)
    workout_id = db.Column(db.Integer, db.ForeignKey("workouts.id"), nullable=False)
    exercise_id = db.Column(db.Integer, db.ForeignKey("exercises.id"), nullable=False)
    reps = db.Column(db.Integer)
    sets = db.Column(db.Integer)
    duration_seconds = db.Column(db.Integer)

    # Relationships
    workout = db.relationship("Workout", back_populates="workout_exercises")
    exercise = db.relationship("Exercise", back_populates="workout_exercises")

    @validates("reps")
    def validate_reps(self, key, value):
        """Reps, if provided, must be a positive integer."""
        if value is not None and (not isinstance(value, int) or value < 1):
            raise ValueError("reps must be a positive integer.")
        return value

    @validates("sets")
    def validate_sets(self, key, value):
        """Sets, if provided, must be a positive integer."""
        if value is not None and (not isinstance(value, int) or value < 1):
            raise ValueError("sets must be a positive integer.")
        return value

    @validates("duration_seconds")
    def validate_duration_seconds(self, key, value):
        """Duration in seconds, if provided, must be a positive integer."""
        if value is not None and (not isinstance(value, int) or value < 1):
            raise ValueError("duration_seconds must be a positive integer.")
        return value

    def __repr__(self):
        return (
            f"<WorkoutExercise workout={self.workout_id} "
            f"exercise={self.exercise_id} sets={self.sets} reps={self.reps}>"
        )
