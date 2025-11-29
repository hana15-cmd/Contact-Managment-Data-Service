import re
from flask_wtf import FlaskForm
from wtforms import IntegerField, SelectField, StringField, PasswordField, RadioField, SubmitField
from wtforms.validators import (
    DataRequired,
    Email,
    EqualTo,
    ValidationError,
    Length,
    NumberRange,
    Regexp
)
from app.database_logic.models import get_database

# Utility function to check if an email is taken (for both add and edit)
def is_email_taken(email, exclude_team_id=None):
    """Check if the email is already registered in the database, 
    excluding a specific team_id if provided (for edit case).
    """
    database = get_database()
    query = "SELECT * FROM teams WHERE EMAIL_ADDRESS = ?"
    params = (email,)
    if exclude_team_id:
        query += " AND ID != ?"
        params = (email, exclude_team_id)  # Use 'ID' instead of 'team_id'
    team = database.execute(query, params).fetchone()
    return team is not None

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
        Length(min=3, max=25, message="Team name must be between 3 and 25 characters.")
    ])
    team_location = StringField('Team Location', validators=[
        DataRequired(),
        Length(min=3, max=40, message="Team location must be between 3 and 40 characters."),
        Regexp(r'^[A-Za-z\s]+$', message="Team location must contain only alphabetic characters and spaces.")
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
    submit = SubmitField('Add Team')

    def validate_team_email_address(self, field):
        if is_email_taken(field.data):
            raise ValidationError("This email is already registered to another team.")

class EditTeamForm(FlaskForm):
    """Form for editing an existing team."""
    team_name = StringField('Team Name', validators=[
        DataRequired(),
        Length(min=3, max=25, message="Team name must be between 3 and 25 characters.")
    ])
    team_location = StringField('Team Location', validators=[
        DataRequired(),
        Length(min=3, max=40, message="Team location must be between 3 and 40 characters."),
        Regexp(r'^[A-Za-z\s]+$', message="Team location must contain only alphabetic characters and spaces.")
    ])
    number_of_team_members = IntegerField('Number of Team Members', validators=[
        DataRequired(),
        validate_team_members
    ])
    team_email_address = StringField('Team Email Address', validators=[
        DataRequired(),
        Email(message="Please enter a valid email address."),
        validate_email_domain
    ])

    submit = SubmitField('Save Changes')

    # Custom email validator (to handle edit scenario)
    def validate_team_email_address(self, field):
        """Ensure the email is unique and conforms to allowed domains, excluding the current team if editing."""
        # Assuming `team_id` is passed into the form somehow
        if is_email_taken(field.data, exclude_team_id=getattr(self, 'team_id', None)):
            raise ValidationError("This email is already taken. Please choose a different email.")

    # Method to set the `team_id` if this form is being used to edit an existing team
    def set_team_id(self, team_id):
        """Sets the team_id for the current form to exclude during email validation."""
        self.team_id = team_id

# Custom validator to ensure no numbers are in the employee name
def validate_no_numbers(form, field):
    """Ensure employee name does not contain numeric values."""
    if any(char.isdigit() for char in field.data):
        raise ValidationError("Employee name must not contain numeric values.")

class AddTeamMemberForm(FlaskForm):
    """Form for adding a team member."""
    employee_name = StringField('Employee Name', validators=[
        DataRequired(),
        Length(min=3, max=100, message="Employee name must be between 3 and 100 characters."),
        validate_no_numbers  # Add the custom validator here
    ])
    email_address = StringField('Employee Email Address', validators=[
        DataRequired(),
        Email(message="Please enter a valid email address."),
        validate_email_domain
    ])
    phone_number = StringField('Phone Number', validators=[
        DataRequired(),
        Length(min=7,max=20, message="Phone number must be between 7 and 20 characters."),
        validate_phone_number
    ])
    team_id = SelectField('Team', coerce=int, validators=[DataRequired()])
    submit = SubmitField('Add Employee')

class EditTeamMemberForm(FlaskForm):
    """Form for editing team member details."""
    employee_name = StringField('Employee Name', validators=[
        DataRequired(),
        Length(min=3, max=100, message="Employee name must be between 3 and 100 characters."),
        validate_no_numbers  # Custom validator for no numbers
    ])
    email_address = StringField('Employee Email Address', validators=[
        DataRequired(),
        Email(message="Please enter a valid email address."),
        validate_email_domain  # Custom email domain validator
    ])
    phone_number = StringField('Phone Number', validators=[
        DataRequired(),
        Length(min=7,max=20, message="Phone number must be between 7 and 20 characters."),
        validate_phone_number  # Custom phone number validator
    ])
    team_id = SelectField('Team', coerce=int, validators=[DataRequired()])
    submit = SubmitField('Edit Employee')