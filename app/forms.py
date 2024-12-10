import re
from flask_wtf import FlaskForm
from wtforms import IntegerField, StringField, PasswordField, RadioField, SubmitField
from wtforms.validators import (
    DataRequired,
    Email,
    EqualTo,
    ValidationError,
    Length,
    NumberRange,
    Regexp
)
from app.models import get_database

# Utility function to check if an email is taken
def is_email_taken(email):
    """Check if the email is already registered in the database."""
    database = get_database()
    user = database.execute("SELECT * FROM users WHERE email = ?", (email,)).fetchone()
    return user is not None

# Custom Validators
def validate_team_members(form, field):
    """Ensure the team has a valid number of members."""
    if field.data < 2:
        raise ValidationError("A team must have at least 2 members.")
    if field.data > 15:
        raise ValidationError("The team cannot have more than 15 members.")

def validate_phone_number(form, field):
    """Validate phone number format (E.164 format)."""
    phone_pattern = re.compile(r'^\+[1-9]\d{1,14}$')  # Must start with "+"
    if not phone_pattern.match(field.data):
        raise ValidationError("Phone number must start with a '+' and follow E.164 format (e.g., +123456789).")

def validate_email_domain(form, field):
    """Ensure the email address ends with specific domains."""
    allowed_domains = ['.org', '.uk', '.com']
    if not any(field.data.endswith(domain) for domain in allowed_domains):
        raise ValidationError("Email address must end with .org, .uk, or .com.")

class SignupForm(FlaskForm):
    """Form for user signup."""
    email = StringField('Email', validators=[
        DataRequired(),
        Email(message="Please enter a valid email address.")
    ])
    first_name = StringField('First Name', validators=[
        DataRequired(),
        Length(min=2, max=50, message="First name must be between 2 and 50 characters."),
        Regexp(r'^[A-Za-z\s]+$', message="First name must contain only letters and spaces.")
    ])
    password = PasswordField('Password', validators=[
        DataRequired(),
        EqualTo('confirm_password', message="Passwords must match."),
        Regexp(
            r'^(?=.*[A-Za-z])(?=.*\d)(?=.*[@$!%*?&])[A-Za-z\d@$!%*?&]{8,}$',
            message="Password must include at least 8 characters, a letter, a number, and a special character."
        )
    ])
    confirm_password = PasswordField('Confirm Password', validators=[
        DataRequired()
    ])
    user_type = RadioField('User Type', choices=[
        ('admin', 'Admin'),
        ('regular', 'Regular User')
    ], validators=[DataRequired()])
    submit = SubmitField('Sign Up')

    # Custom email validator
    def validate_email(self, email):
        """Ensure the email is unique and conforms to allowed domains."""
        if is_email_taken(email.data):
            raise ValidationError("This email is already registered. Please log in.")
        # Validate domain
        allowed_domains = ['.org', '.uk', '.com']
        if not any(email.data.endswith(domain) for domain in allowed_domains):
            raise ValidationError("Email address must end with .org, .uk, or .com.")

class AddTeamForm(FlaskForm):
    """Form for adding a team."""
    team_name = StringField('Team Name', validators=[
        DataRequired(),
        Length(min=3, max=100, message="Team name must be between 3 and 100 characters.")
    ])
    team_location = StringField('Team Location', validators=[
        DataRequired(),
        Length(min=3, max=100, message="Team location must be between 3 and 100 characters.")
    ])
    number_of_team_members = IntegerField('Number of Team Members', validators=[
        DataRequired(),
        NumberRange(min=1, message="Team must have at least 1 member."),
        validate_team_members
    ])
    team_email_address = StringField('Team Email Address', validators=[
        DataRequired(),
        Email(message="Please enter a valid email address."),
        validate_email_domain
    ])
    team_phone_number = StringField('Team Phone Number', validators=[
        DataRequired(),
        Length(max=20, message="Phone number must not exceed 20 characters."),
        validate_phone_number
    ])
    submit = SubmitField('Add Team')