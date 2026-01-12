from flask_wtf import FlaskForm

from wtforms import StringField, TextAreaField, DateField, SelectField, PasswordField, SubmitField,SelectMultipleField,DecimalField
from wtforms.validators import DataRequired, Email,Length,EqualTo

class RegistrationForm(FlaskForm):
    username = StringField("Username", validators=[DataRequired(), Length(min=2, max=50)])
    email = StringField("Email", validators=[DataRequired(), Email()])
    your_id = StringField("your_id", validators=[DataRequired(), Length(10)])
    password = PasswordField("Password", validators=[DataRequired(), Length(min=6)])
    confirm_password = PasswordField("Confirm Password", validators=[DataRequired(), EqualTo('password')])
    role = SelectField(
        "Role",
        choices=[
            ('student','Student'),
            ('reviewer','Reviewer'),
            ('committee','Scholarship Committee'),
            ('admin','Admin')
        ],
        validators=[DataRequired()]
    )
    submit = SubmitField("Register")


class LoginForm(FlaskForm):
    email = StringField("Email", validators=[DataRequired(), Email()])
    password = PasswordField("Password", validators=[DataRequired()])
    submit = SubmitField("Login")
    
class ScholarshipForm(FlaskForm):
    title = StringField("Title", validators=[DataRequired()])
    description = TextAreaField("Description", validators=[DataRequired()])
    eligibility_criteria = TextAreaField("Eligibility Criteria", validators=[DataRequired()])
    documents_required = StringField("Documents Required", validators=[DataRequired()])
    application_deadline = DateField("Application Deadline", validators=[DataRequired()])
    submit = SubmitField("Create Scholarship")

class AssignReviewersForm(FlaskForm):
    reviewers = SelectMultipleField("Select Reviewers", coerce=int, validators=[DataRequired()])
    submit = SubmitField("Assign Reviewers")

class ApplicationForm(FlaskForm):
    full_name = StringField("Full Name", validators=[DataRequired()])
    address = TextAreaField("Home Address", validators=[DataRequired()])
    ic_number = StringField("IC / Passport Number", validators=[DataRequired()])
    dob = DateField("Date of Birth", validators=[DataRequired()])
    age = StringField("Age", validators=[DataRequired()])
    intake = StringField("Intake")
    programme = SelectField(
        "Programme",
        choices=[("Foundation","Foundation"),("Diploma","Diploma"),("Degree","Degree")]
    )
    course = StringField("Course")
    nationality = StringField("Nationality")
    race = StringField("Race")
    sex = SelectField("Sex", choices=[("Male","Male"),("Female","Female")])
    contact = StringField("Contact Number")
    home_contact = StringField("Home Contact Number")
    household_income = DecimalField(
        "Household Monthly Income", 
        places=2, 
        validators=[DataRequired()]
    )
    email = StringField("Email", validators=[DataRequired(), Email()])
    statement = TextAreaField(
        "Personal Statement", 
        validators=[DataRequired(), Length(max=1000)]
    )
    submit = SubmitField("Submit Application")
