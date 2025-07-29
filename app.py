from flask import Flask, render_template, redirect, url_for, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, login_user, login_required, logout_user, current_user, UserMixin
from flask_jwt_extended import JWTManager, create_access_token, jwt_required, get_jwt_identity
from forms import RegisterForm, LoginForm, FoodForm
from models import db, User, FoodEntry

app = Flask(__name__)
app.config['SECRET_KEY'] = 'super-secret-key'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['JWT_SECRET_KEY'] = 'jwt-secret-key'

db.init_app(app)
login_manager = LoginManager(app)
login_manager.login_view = 'login'
jwt = JWTManager(app)

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# -----------------------------
# Web Routes
# -----------------------------

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

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('login'))

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

# -----------------------------
# REST API Routes
# -----------------------------

@app.route('/api/register', methods=['POST'])
def api_register():
    data = request.json
    username = data.get('username')
    password = data.get('password')
    if not username or not password:
        return jsonify({"msg": "Missing username or password"}), 400
    if User.query.filter_by(username=username).first():
        return jsonify({"msg": "User already exists"}), 400
    new_user = User(username=username, password=password)
    db.session.add(new_user)
    db.session.commit()
    return jsonify({"msg": "User registered successfully"}), 201

@app.route('/api/login', methods=['POST'])
def api_login():
    data = request.json
    user = User.query.filter_by(username=data.get('username')).first()
    if user and user.password == data.get('password'):
        token = create_access_token(identity=user.id)
        return jsonify(access_token=token)
    return jsonify({"msg": "Invalid credentials"}), 401

@app.route('/api/foods', methods=['GET'])
@jwt_required()
def api_get_foods():
    user_id = get_jwt_identity()
    foods = FoodEntry.query.filter_by(user_id=user_id).all()
    return jsonify([{
        'id': f.id,
        'food_name': f.food_name,
        'ingredients': f.ingredients,
        'calories': f.calories,
        'protein': f.protein,
        'carbs': f.carbs,
        'fats': f.fats
    } for f in foods])

@app.route('/api/foods', methods=['POST'])
@jwt_required()
def api_add_food():
    user_id = get_jwt_identity()
    data = request.json
    food = FoodEntry(
        food_name=data['food_name'],
        ingredients=data['ingredients'],
        calories=data.get('calories', 0),
        protein=data.get('protein', 0),
        carbs=data.get('carbs', 0),
        fats=data.get('fats', 0),
        user_id=user_id
    )
    db.session.add(food)
    db.session.commit()
    return jsonify({"msg": "Food entry added"}), 201

@app.route('/api/foods/<int:food_id>', methods=['DELETE'])
@jwt_required()
def api_delete_food(food_id):
    user_id = get_jwt_identity()
    food = FoodEntry.query.get_or_404(food_id)
    if food.user_id != user_id:
        return jsonify({"msg": "Unauthorized"}), 403
    db.session.delete(food)
    db.session.commit()
    return jsonify({"msg": "Food entry deleted"}), 200

# -----------------------------
# Run Server
# -----------------------------
if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)


