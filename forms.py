from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, FloatField
from wtforms.validators import InputRequired, Length, Regexp
from wtforms.validators import InputRequired, Length, Regexp, ValidationError
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField

class RegisterForm(FlaskForm):
    username = StringField("Username", validators=[
        InputRequired(),
        Length(min=4, message="Username must be at least 4 characters.")
    ])
    
    password = PasswordField("Password", validators=[
        InputRequired(),
        Length(min=6, message="Password must be at least 6 characters."),
        Regexp(
            r'^(?=.*[A-Za-z])(?=.*\d)[A-Za-z\d]{6,}$',
            message="Password must contain at least one letter and one number."
        )
    ])
    
    submit = SubmitField("Register")

class LoginForm(FlaskForm):
    username = StringField("Username", validators=[InputRequired()])
    password = PasswordField("Password", validators=[InputRequired()])
    submit = SubmitField("Login")

class FoodForm(FlaskForm):
    food_name = StringField("Food Name", validators=[InputRequired()])
    ingredients = StringField("Ingredients", validators=[InputRequired()])
    calories = FloatField("Calories")
    protein = FloatField("Protein (g)")
    carbs = FloatField("Carbs (g)")
    fats = FloatField("Fats (g)")
    submit = SubmitField("Add Food")
