# -----------------------------------------------------------
# This app tracks the prices of items and sends a text 
# message when the item reaches your desired 'buy price'.
#
# Copyright (c) 2020 Matthew Zenittini
# Released under MIT License
# Email matt@playstowin.com
# -----------------------------------------------------------

# Standard Library Imports
import os

# Third Party Imports
from flask import Flask, request, render_template, url_for, redirect, flash
from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin, LoginManager, login_user, logout_user, login_required, current_user
from werkzeug.security import generate_password_hash, check_password_hash

# Local Imports
import pricechecker



# ---------------
# App Settings  
# ---------------
app = Flask(__name__)

app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL')
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY')

db = SQLAlchemy(app)


# ---------------
# Auth Settings  
# ---------------
login_manager = LoginManager(app)
login_manager.login_view = 'login'
@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# ---------------
# Models  
# ---------------
class Item(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(255))
    selling_price = db.Column(db.String(255))
    imageurl = db.Column(db.String(255))
    buy_price = db.Column(db.String(255))
    link = db.Column(db.String(255))


class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255))
    email = db.Column(db.String(100), unique=True)
    password = db.Column(db.String(100))


# ---------------
# Main Routes   
# ---------------
@app.route('/')
def index():
    items = pricechecker.get_items()

    return render_template('index.html', items=items)


# Html button to test price check function
@app.route('/test_price_check', methods=['POST'])
def test_price_check():
    pricechecker.price_check()

    return redirect(url_for('index'))


# Add item page
@app.route('/add')
def add():
    
    return render_template('add.html')


# Add new item to db
@app.route('/submit', methods=['POST'])
def add_submit():
    link = request.form['link']
    buy_price = request.form['price']
    pricechecker.create_item(link, buy_price)

    return redirect(url_for('index'))


# Add MBP to DB with higher price for testing refresh + text
@app.route('/macbook')
def macbook():
    item = Item(title='Macbook Pro', selling_price='1550', imageurl='https://static.bhphoto.com/images/images500x500/apple_mxk32ll_a_13_3_macbook_pro_with_1588701104_1560523.jpg', buy_price='1300', link='https://www.bhphotovideo.com/c/product/1560523-REG/apple_mxk32ll_a_13_3_macbook_pro_with.html')
    db.session.add(item)
    db.session.commit()

    return redirect(url_for('index'))


# Creates CLI command that updates prices with 'flask update-prices'
@app.cli.command()
def update_prices():
    pricechecker.price_check()
    print('Price Check job complete.')


# ---------------
# Auth Routes  
# ---------------
@app.route('/login')
def login():
    return render_template('login.html')


@app.route('/login', methods=['POST'])
def login_post():
    # Get form website data
    email = request.form['email']
    password = request.form['password']
    remember = True if request.form.get('checkbox') else False

    # Get user data for provided email
    user = User.query.filter_by(email=email).first()

    # Check if user exists 
    # Hash user password and compare to database
    if not user or not check_password_hash(user.password, password):
        flash('Please check your login details and try again.')
        return redirect(url_for('login'))

    # If username and pass match - login
    login_user(user, remember=remember)
    return redirect(url_for('profile'))


@app.route('/signup')
def signup():
    return render_template('signup.html')


@app.route('/signup', methods=['POST'])
def signup_post():
    name = request.form['name']
    email = request.form['email']
    password = request.form['password']

    # Check if user exists
    user = User.query.filter_by(email=email).first()

    if user:
        flash('Email address already exists')
        return redirect(url_for('signup'))

    # Create a new user with form data
    new_user = User(email=email, name=name, password=generate_password_hash(password, method='sha256'))

    # Add user to database
    db.session.add(new_user)
    db.session.commit()

    return redirect(url_for('login'))


@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('index'))


@app.route('/profile')
@login_required
def profile():
    items = pricechecker.get_items()

    return render_template('profile.html', items=items, name=current_user.name)