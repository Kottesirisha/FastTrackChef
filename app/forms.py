from flask_wtf import FlaskForm
from flask_wtf.file import FileAllowed, FileField
from wtforms import (
    BooleanField,
    DecimalField,
    PasswordField,
    SelectField,
    StringField,
    SubmitField,
    TextAreaField,
)
from wtforms.validators import DataRequired, Email, EqualTo, Length, NumberRange, Optional, Regexp


class LoginForm(FlaskForm):
    email = StringField("Email", validators=[DataRequired(), Email()])
    password = PasswordField("Password", validators=[DataRequired()])
    remember = BooleanField("Remember Me")
    submit = SubmitField("Login")


class RegisterForm(FlaskForm):
    name = StringField("Full Name", validators=[DataRequired(), Length(min=2, max=100)])
    email = StringField("Email", validators=[DataRequired(), Email()])
    phone = StringField(
        "Phone",
        validators=[
            Optional(),
            Length(max=20),
            Regexp(r"^[\d\s\+\-\(\)]{7,20}$", message="Enter a valid phone number."),
        ],
    )
    address = TextAreaField("Address", validators=[Optional(), Length(max=500)])
    password = PasswordField(
        "Password",
        validators=[
            DataRequired(),
            Length(min=8, message="Password must be at least 8 characters."),
        ],
    )
    confirm_password = PasswordField(
        "Confirm Password",
        validators=[DataRequired(), EqualTo("password", message="Passwords must match.")],
    )
    submit = SubmitField("Register")


class ForgotPasswordForm(FlaskForm):
    email = StringField("Email", validators=[DataRequired(), Email()])
    submit = SubmitField("Send Reset Link")


class ProfileForm(FlaskForm):
    name = StringField("Full Name", validators=[DataRequired(), Length(min=2, max=100)])
    email = StringField("Email", validators=[DataRequired(), Email()])
    phone = StringField(
        "Phone",
        validators=[
            Optional(),
            Length(max=20),
            Regexp(r"^[\d\s\+\-\(\)]{7,20}$", message="Enter a valid phone number."),
        ],
    )
    address = TextAreaField("Address", validators=[Optional(), Length(max=500)])
    submit = SubmitField("Update Profile")


class ChangePasswordForm(FlaskForm):
    current_password = PasswordField("Current Password", validators=[DataRequired()])
    new_password = PasswordField(
        "New Password",
        validators=[DataRequired(), Length(min=8, message="Password must be at least 8 characters.")],
    )
    confirm_password = PasswordField(
        "Confirm New Password",
        validators=[DataRequired(), EqualTo("new_password", message="Passwords must match.")],
    )
    submit = SubmitField("Change Password")


class CategoryForm(FlaskForm):
    name = StringField("Category Name", validators=[DataRequired(), Length(min=2, max=80)])
    description = TextAreaField("Description", validators=[Optional(), Length(max=500)])
    submit = SubmitField("Save Category")


class FoodItemForm(FlaskForm):
    name = StringField("Food Name", validators=[DataRequired(), Length(min=2, max=100)])
    description = TextAreaField("Description", validators=[Optional(), Length(max=1000)])
    price = DecimalField(
        "Price ($)",
        places=2,
        validators=[DataRequired(), NumberRange(min=0.01, message="Price must be greater than zero.")],
    )
    category_id = SelectField("Category", coerce=int, validators=[DataRequired()])
    image = FileField(
        "Food Image",
        validators=[FileAllowed(["jpg", "jpeg", "png", "gif", "webp"], "Images only (JPG, PNG, GIF, WEBP).")],
    )
    available = BooleanField("Available", default=True)
    submit = SubmitField("Save Food Item")


class OrderStatusForm(FlaskForm):
    status = SelectField(
        "Order Status",
        choices=[("pending", "Pending"), ("preparing", "Preparing"), ("delivered", "Delivered"), ("cancelled", "Cancelled")],
        validators=[DataRequired()],
    )
    submit = SubmitField("Update Status")
