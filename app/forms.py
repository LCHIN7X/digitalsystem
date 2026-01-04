from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField, DateField, SelectField, PasswordField, SubmitField,SelectMultipleField
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
