from flask import Flask, render_template, request, redirect, url_for, session
from flask_pymongo import PyMongo
from bson.objectid import ObjectId
import bcrypt

app = Flask(__name__)
app.secret_key = "your_secret_key"

# Hj1onMRG9gQnVmFo

# MongoDB configuration
app.config['MONGO_URI'] = "mongodb+srv://gerkim62:Hj1onMRG9gQnVmFo@cluster0.sj7b0xr.mongodb.net/"
mongo = PyMongo(app)

# clear the database
# print('Clearing the database')
# mongo.db.users.delete_many({})
# print('Cleared users')
# mongo.db.products.delete_many({})
# print('Cleared products')


# Routes
@app.route('/')
def home():
    if 'username' in session:
        return render_template('index.html', username=session['username'])
    else:
        users = mongo.db.users.find_one()
        if users:
            return render_template('login.html')
        else:
            return render_template('create_account.html')

@app.route('/create_account', methods=['GET', 'POST'])
def create_account():
    if request.method == 'POST':
        # Check if passwords match
        if request.form['password'] != request.form['confirm_password']:
            return redirect(url_for('error', message='Passwords do not match', button_label='Try Again'))

        users = mongo.db.users
        existing_user = users.find_one({'username': request.form['username']})

        if existing_user:
             error_message = 'Username already exists. Please choose a different username.'
             button_label = 'Try Again'
             return redirect(url_for('error', message=error_message, button_label=button_label))

        else:
            hashed_password = bcrypt.hashpw(request.form['password'].encode('utf-8'), bcrypt.gensalt())
            users.insert_one({'username': request.form['username'], 'password': hashed_password})
            session['username'] = request.form['username']
            return redirect(url_for('home'))

    return render_template('create_account.html')

@app.route('/error')
def error():
    error_message = request.args.get('message', 'An error occurred.')
    button_label = request.args.get('button_label', 'Go Back to Home')
    return render_template('error.html', error_message=error_message, button_label=button_label)


@app.route('/login', methods=['POST'])
def login():
    users = mongo.db.users
    login_user = users.find_one({'username': request.form['username']})

    if login_user:
        if bcrypt.hashpw(request.form['password'].encode('utf-8'), login_user['password']) == login_user['password']:
            session['username'] = request.form['username']
            return redirect(url_for('home'))
    return render_template("invalid_login.html")

@app.route('/logout')
def logout():
    session.pop('username', None)
    return redirect(url_for('home'))

@app.route('/add_product', methods=['POST', 'GET'])
def add_product():
    if 'username' not in session:
        return redirect(url_for('home'))

    if request.method == 'POST':
        products = mongo.db.products
        product_name = request.form['product_name']
        quantity = int(request.form['quantity'])
        products.insert_one({'name': product_name, 'quantity': quantity})
        return redirect(url_for('view_products'))

    elif request.method == 'GET':
        return render_template('add_product.html')

@app.route('/view_products')
def view_products():
    if 'username' not in session:
        return redirect(url_for('home'))

    products = mongo.db.products.find()
    return render_template('view_products.html', products=list(products))

@app.route('/delete_product/<product_id>')
def delete_product(product_id):
    if 'username' not in session:
        return redirect(url_for('home'))

    mongo.db.products.delete_one({'_id': ObjectId(product_id)})
    return redirect(url_for('view_products'))

@app.route('/set_password', methods=['GET', 'POST'])
def set_password():
    if 'username' not in session:
        return redirect(url_for('home'))

    if request.method == 'POST':
        users = mongo.db.users
        existing_user = users.find_one({'username': session['username']})
        if existing_user:
            hashed_password = bcrypt.hashpw(request.form['password'].encode('utf-8'), bcrypt.gensalt())
            users.update_one({'_id': existing_user['_id']}, {'$set': {'password': hashed_password}})
            return redirect(url_for('home'))
    return render_template('set_password.html')

@app.route('/change_password', methods=['GET', 'POST'])
def change_password():
    if 'username' not in session:
        return redirect(url_for('home'))

    if request.method == 'POST':
        users = mongo.db.users
        existing_user = users.find_one({'username': session['username']})
        if existing_user:
            if bcrypt.hashpw(request.form['old_password'].encode('utf-8'), existing_user['password']) == existing_user['password']:
                if request.form['new_password'] == request.form['confirm_new_password']:
                    hashed_password = bcrypt.hashpw(request.form['new_password'].encode('utf-8'), bcrypt.gensalt())
                    users.update_one({'_id': existing_user['_id']}, {'$set': {'password': hashed_password}})
                    return redirect(url_for('home'))
                else:
                    return redirect(url_for('error', message='New passwords do not match', button_label='Go Back to Home'))
            else:
                return redirect(url_for('error', message='Old password is incorrect', button_label='Go Back to Home'))
    return render_template('change_password.html')

@app.route('/update_product/<product_id>')
def update_product(product_id):
    if 'username' not in session:
        return redirect(url_for('home'))

    # Fetch the product from the database using its ID
    product = mongo.db.products.find_one({'_id': ObjectId(product_id)})
    if product:
        return render_template('update_product.html', product=product)
    else:
        return 'Product not found'

@app.route('/save_product_changes/<product_id>', methods=['POST'])
def save_product_changes(product_id):
    if 'username' not in session:
        return redirect(url_for('home'))

    # Get the updated product information from the form
    updated_name = request.form['updated_name']
    updated_quantity = int(request.form['updated_quantity'])

    # Update the product in the database
    mongo.db.products.update_one({'_id': ObjectId(product_id)}, {'$set': {'name': updated_name, 'quantity': updated_quantity}})

    return redirect(url_for('view_products'))

if __name__ == '__main__':
    app.run(debug=True)
