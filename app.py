import PriceChecker, os
from flask import Flask, request, render_template, url_for, redirect
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)

# App Settings
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL')
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY')

db = SQLAlchemy(app)

class Items(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(255))
    selling_price = db.Column(db.String(255))
    imageurl = db.Column(db.String(255))
    buy_price = db.Column(db.String(255))
    link = db.Column(db.String(255))

#homepage view
@app.route('/')
def index():
    items = PriceChecker.get_items()

    return render_template('index.html', items=items)

#html button to test price check function
@app.route('/test_price_check', methods=['POST'])
def test_price_check():
    PriceChecker.price_check()

    return redirect(url_for('index'))

#add item page
@app.route('/add')
def add():
    
    return render_template('add.html')

#add new item to db
@app.route('/submit', methods=['POST'])
def add_submit():
    link = request.form['link']
    buy_price = request.form['price']
    PriceChecker.create_item(link, buy_price)

    return redirect(url_for('index'))

#add MBP to DB with higher price for testing
@app.route('/macbook')
def macbook():
    item = Items(title='Macbook Pro', selling_price='1550', imageurl='https://static.bhphoto.com/images/images500x500/apple_mxk32ll_a_13_3_macbook_pro_with_1588701104_1560523.jpg', buy_price='1300', link='https://www.bhphotovideo.com/c/product/1560523-REG/apple_mxk32ll_a_13_3_macbook_pro_with.html')
    db.session.add(item)
    db.session.commit()

    return redirect(url_for('index'))

@app.cli.command()
def update_prices():
    PriceChecker.price_check()
    print('Price Check job complete.')