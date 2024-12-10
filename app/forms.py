from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, RadioField, SubmitField
from wtforms.validators import DataRequired, Email, EqualTo, ValidationError, Length, Regexp

from app.models import get_database

class SignupForm(FlaskForm):
    email = StringField('Email', validators=[
        DataRequired(),
        Email(message="Enter a valid email.")
    ])
    first_name = StringField('First Name', validators=[
        DataRequired(),
        Length(min=2, max=50, message="First name must be between 2 and 50 characters."),
        Regexp(
            r'^[A-Za-z\s]+$',  # Regex to allow alphabetic characters and spaces
            message="First name must contain only alphabetic characters and spaces."
        )
    ])
    password = PasswordField('Password', validators=[
        DataRequired(),
        EqualTo('confirm_password', message='Passwords must match.'),
        Regexp(
            r'^(?=.*[A-Za-z])(?=.*\d)(?=.*[@$!%*?&])[A-Za-z\d@$!%*?&]{8,}$',
            message=(
                "Password must be at least 8 characters long, include at least one letter, "
                "one number, and one special character."
            )
        )
    ])
    confirm_password = PasswordField('Confirm Password', validators=[DataRequired()])
    user_type = RadioField('User Type', choices=[('admin', 'Admin'), ('regular', 'Regular User')], validators=[DataRequired()])
    submit = SubmitField('Sign Up')

    def validate_email(self, email):
        # Ensure the email is unique
        if is_email_taken(email.data):
            raise ValidationError('Email is already registered. Please log in.')

def is_email_taken(email):
    """Check if the email already exists in the database."""
    database = get_database()
    return database.execute("SELECT * FROM users WHERE email = ?", (email,)).fetchone() is not None
