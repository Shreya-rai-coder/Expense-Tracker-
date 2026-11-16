from flask import Flask, flash, redirect, render_template, request, url_for, get_flashed_messages
from flask_login import(LoginManager, current_user, login_required, login_user, logout_user,)
from models import Expense, User, db
from werkzeug.security import check_password_hash, generate_password_hash

app = Flask(__name__)
app.config['SECRET_KEY'] = 'shreya_expense_tracker_secret key'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'

#---- Connects model.py(db object) with app.py(flask app)------
db.init_app(app)

#---- Configuring Flask-Login-----------
login_manager = LoginManager()
login_manager.login_view = 'login'
login_manager.init_app(app)

#------ Loading current user----------
@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

#------ Creating database tables----------
with app.app_context():
    db.create_all()

#-------- Authentication Routes-----------
@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')

        existing_user = User.query.filter_by(username=username).first()
        if existing_user:
            flash('Username already exists! Choose another.')
            return redirect(url_for('register'))
        
        hashed_password = generate_password_hash(password, method='pbkdf2:sha256')
        new_user = User(username=username, password=hashed_password)

        db.session.add(new_user)
        db.session.commit()
        return redirect(url_for('login'))
    
    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')

        user = User.query.filter_by(username=username).first()
        if user and check_password_hash(user.password, password):
            login_user(user)
            return redirect(url_for('dashboard'))
        else:
            flash('Invalid username or password.')
    return render_template('login.html')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('login'))

#-------------------- Core App Routes -----------------------------
#----- Creating Dashboard Route----------
@app.route('/')
@login_required
def dashboard():
    user_expenses = Expense.query.filter_by(user_id = current_user.id).all()
    total_spent = sum(item.amount for item in user_expenses)
    return render_template('dashboard.html', expenses = user_expenses, total = total_spent)

#----- Add Expense Route----------
@app.route('/add', methods=['POST'])
@login_required
def add_expense():
    title = request.form.get('title')
    amount = float(request.form.get('amount'))
    category = request.form.get('category')
    date = request.form.get('date')

    new_expense = Expense(title=title,
                          amount=amount,
                          category=category,
                          date=date,
                          owner=current_user,)
    db.session.add(new_expense)
    db.session.commit()
    return redirect(url_for('dashboard'))

#------------ Run The Application --------------------
if __name__ == '__main__':
    app.run(debug=True)