from marshmallow import Schema, fields, validates, ValidationError


# ── Allowed exercise categories ───────────────────────────────────────────────
ALLOWED_CATEGORIES = {"strength", "cardio", "flexibility", "balance", "hiit"}


# ── Flat schemas (no nesting) — used internally and for simple list responses ─

class ExerciseSchema(Schema):
    """Serializes/deserializes an Exercise without nested relationships."""

    id = fields.Int(dump_only=True)
    name = fields.Str(required=True)
    category = fields.Str(required=True)
    equipment_needed = fields.Bool(load_default=False)

    @validates("name")
    def validate_name(self, value):
        if not value or not value.strip():
            raise ValidationError("Exercise name cannot be blank.")

    @validates("category")
    def validate_category(self, value):
        if value.lower() not in ALLOWED_CATEGORIES:
            raise ValidationError(
                f"Category must be one of: {', '.join(sorted(ALLOWED_CATEGORIES))}."
            )


class WorkoutSchema(Schema):
    """Serializes/deserializes a Workout without nested relationships."""

    id = fields.Int(dump_only=True)
    date = fields.Date(required=True)
    duration_minutes = fields.Int(required=True)
    notes = fields.Str(load_default=None)

    @validates("duration_minutes")
    def validate_duration(self, value):
        if value < 1:
            raise ValidationError("duration_minutes must be at least 1.")


class WorkoutExerciseSchema(Schema):
    """Serializes/deserializes per-session details (reps, sets, duration)."""

    id = fields.Int(dump_only=True)
    workout_id = fields.Int(dump_only=True)
    exercise_id = fields.Int(dump_only=True)
    reps = fields.Int(load_default=None)
    sets = fields.Int(load_default=None)
    duration_seconds = fields.Int(load_default=None)

    @validates("reps")
    def validate_reps(self, value):
        if value is not None and value < 1:
            raise ValidationError("reps must be a positive integer.")

    @validates("sets")
    def validate_sets(self, value):
        if value is not None and value < 1:
            raise ValidationError("sets must be a positive integer.")

    @validates("duration_seconds")
    def validate_duration_seconds(self, value):
        if value is not None and value < 1:
            raise ValidationError("duration_seconds must be a positive integer.")


# ── Nested schemas — used for detail (single-resource) endpoints ──────────────

class WorkoutExerciseNestedSchema(WorkoutExerciseSchema):
    """Extends WorkoutExerciseSchema to include the full Exercise details."""

    exercise = fields.Nested(ExerciseSchema, dump_only=True)


class WorkoutWithExercisesSchema(WorkoutSchema):
    """
    Extends WorkoutSchema to include each WorkoutExercise with its Exercise.
    Used for GET /workouts/<id>.
    """

    workout_exercises = fields.List(
        fields.Nested(WorkoutExerciseNestedSchema), dump_only=True
    )


class ExerciseWithWorkoutsSchema(ExerciseSchema):
    """
    Extends ExerciseSchema to include associated Workouts.
    Used for GET /exercises/<id>.
    """

    workouts = fields.List(fields.Nested(WorkoutSchema), dump_only=True)


# ── Instantiated schema objects shared across app.py ─────────────────────────

exercise_schema = ExerciseSchema()
exercises_schema = ExerciseSchema(many=True)
exercise_with_workouts_schema = ExerciseWithWorkoutsSchema()

workout_schema = WorkoutSchema()
workouts_schema = WorkoutSchema(many=True)
workout_with_exercises_schema = WorkoutWithExercisesSchema()

workout_exercise_schema = WorkoutExerciseSchema()
