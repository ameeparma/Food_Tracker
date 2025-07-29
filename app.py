from flask import Flask, render_template, redirect, url_for, request
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, login_user, login_required, logout_user, current_user
from models import db, User, FoodEntry
from forms import RegisterForm, LoginForm, FoodForm

app = Flask(__name__)
app.config['SECRET_KEY'] = 'mysecret'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'

db.init_app(app)
login_manager = LoginManager(app)
login_manager.login_view = 'login'

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

@app.route('/')
def index():
    return redirect(url_for('login'))

@app.route('/register', methods=['GET', 'POST'])
def register():
    form = RegisterForm()
    if form.validate_on_submit():
        existing_user = User.query.filter_by(username=form.username.data).first()
        if existing_user:
            return "Username already taken", 400
        user = User(username=form.username.data, password=form.password.data)
        db.session.add(user)
        db.session.commit()
        return redirect(url_for('login'))
    return render_template('register.html', form=form)

@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user and user.password == form.password.data:
            login_user(user)
            return redirect(url_for('dashboard'))
        else:
            return "Invalid credentials", 401
    return render_template('login.html', form=form)

@app.route('/dashboard')
@login_required
def dashboard():
    foods = FoodEntry.query.filter_by(user_id=current_user.id).all()
    total = {
        'calories': sum(f.calories for f in foods),
        'protein': sum(f.protein for f in foods),
        'carbs': sum(f.carbs for f in foods),
        'fats': sum(f.fats for f in foods),
    }
    return render_template('dashboard.html', foods=foods, total=total)

@app.route('/add', methods=['GET', 'POST'])
@login_required
def add_food():
    form = FoodForm()
    if form.validate_on_submit():
        food = FoodEntry(
            food_name=form.food_name.data,
            ingredients=form.ingredients.data,
            calories=form.calories.data,
            protein=form.protein.data,
            carbs=form.carbs.data,
            fats=form.fats.data,
            user_id=current_user.id
        )
        db.session.add(food)
        db.session.commit()
        return redirect(url_for('dashboard'))
    return render_template('add_food.html', form=form)

@app.route('/delete/<int:food_id>', methods=['POST'])
@login_required
def delete_food(food_id):
    food = FoodEntry.query.get_or_404(food_id)
    if food.user_id != current_user.id:
        return "Unauthorized", 403
    db.session.delete(food)
    db.session.commit()
    return redirect(url_for('dashboard'))

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('login'))

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)


