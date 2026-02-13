#!/usr/bin/env python3

from flask import Flask, request, render_template, session, redirect, url_for, jsonify
import os
import json
import logging

app = Flask(__name__)
app.secret_key = os.urandom(24)
app.config['DEBUG'] = False

logging.basicConfig(level=logging.WARNING)
logger = logging.getLogger(__name__)

DATA_DIR = '/home/user/data'
USERS_FILE = os.path.join(DATA_DIR, 'users.json')
SECRETS_FILE = os.path.join(DATA_DIR, 'secrets.json')

ADMIN_USERNAME = 'admin'
ADMIN_PASSWORD = 'Xk9mP2vL8qW5nR3jH7tY4uB6cF1sD0zN9xE8aG5wQ2mV7yT3pK6hJ4rL1nB8cX5fZ2'

AVAILABLE_ITEMS = [
    {'id': 'laptop', 'name': 'Laptop Pro', 'image': 'laptop.jpg', 'price': 800},
    {'id': 'phone', 'name': 'Smartphone X',
        'image': 'phone.jpg', 'price': 600},
    {'id': 'tablet', 'name': 'Tablet Air', 'image': 'tablet.jpg', 'price': 400},
    {'id': 'watch', 'name': 'Smart Watch', 'image': 'watch.jpg', 'price': 200},
    {'id': 'headphones', 'name': 'Wireless Headphones',
        'image': 'headphones.jpg', 'price': 150},
    {'id': 'camera', 'name': 'Digital Camera',
        'image': 'camera.jpg', 'price': 500},
    {'id': 'speaker', 'name': 'Bluetooth Speaker',
        'image': 'speaker.jpg', 'price': 100},
    {'id': 'keyboard', 'name': 'Mechanical Keyboard',
        'image': 'keyboard.jpg', 'price': 120},
    {'id': 'mouse', 'name': 'Gaming Mouse', 'image': 'mouse.jpg', 'price': 80},
    {'id': 'catnip', 'name': 'Catnip 🐱',
        'image': 'catnip.jpg', 'price': 999999},
]


def init_data():
    os.makedirs(DATA_DIR, exist_ok=True)
    if not os.path.exists(USERS_FILE):
        with open(USERS_FILE, 'w') as f:
            json.dump({}, f)

    # Create admin user
    users = load_users()
    if ADMIN_USERNAME not in users:
        users[ADMIN_USERNAME] = {
            'password': ADMIN_PASSWORD,
            'balance': 999999 * 1000,
            'purchased_items': [],
            'is_admin': True
        }
        save_users(users)

    # Initialize secrets for items
    if not os.path.exists(SECRETS_FILE):
        secrets = {
            item['id']: f'SECRET_PLACEHOLDER_FOR_{item["id"].upper()}_NO_FLAG_HERE' for item in AVAILABLE_ITEMS}
        save_secrets(secrets)


def load_users():
    with open(USERS_FILE, 'r') as f:
        return json.load(f)


def save_users(users):
    with open(USERS_FILE, 'w') as f:
        json.dump(users, f, indent=2)


def load_secrets():
    with open(SECRETS_FILE, 'r') as f:
        return json.load(f)


def save_secrets(secrets):
    with open(SECRETS_FILE, 'w') as f:
        json.dump(secrets, f, indent=2)


@app.route('/')
def index():
    balance = 0
    username = None
    if 'username' in session:
        users = load_users()
        username = session['username']
        balance = users.get(username, {}).get('balance', 0)
    return render_template('index.html', balance=balance, username=username)


@app.route('/shop')
def shop():
    if 'username' not in session:
        return redirect(url_for('login'))

    users = load_users()
    balance = users.get(session['username'], {}).get('balance', 0)
    purchased_items = users.get(
        session['username'], {}).get('purchased_items', [])

    return render_template('shop.html',
                           items=AVAILABLE_ITEMS,
                           balance=balance,
                           username=session['username'],
                           purchased_items=purchased_items)


@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')

        users = load_users()
        if username in users:
            return render_template('register.html', error="User already exists")

        users[username] = {
            'password': password,
            'balance': 1000,
            'purchased_items': []  # List of item IDs that user has bought at least once
        }
        save_users(users)

        session['username'] = username
        return redirect(url_for('shop'))

    return render_template('register.html')


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')

        users = load_users()
        if username not in users or users[username]['password'] != password:
            return render_template('login.html', error="Invalid credentials")

        session['username'] = username
        return redirect(url_for('shop'))

    return render_template('login.html')


@app.route('/logout')
def logout():
    session.pop('username', None)
    session.pop('cart', None)
    return redirect(url_for('index'))


@app.route('/cart')
def cart():
    if 'username' not in session:
        return redirect(url_for('login'))

    users = load_users()
    balance = users.get(session['username'], {}).get('balance', 0)

    cart_items = session.get('cart', [])
    cart_data = []
    total = 0

    for item_id in cart_items:
        item = next((i for i in AVAILABLE_ITEMS if i['id'] == item_id), None)
        if item:
            cart_data.append(item)
            total += item['price']

    return render_template('cart.html',
                           cart_items=cart_data,
                           balance=balance,
                           username=session['username'],
                           total=total)


@app.route('/add_to_cart', methods=['POST'])
def add_to_cart():
    if 'username' not in session:
        return jsonify({'success': False, 'error': 'Not logged in'}), 401

    item_id = request.form.get('item_id')

    item = next((i for i in AVAILABLE_ITEMS if i['id'] == item_id), None)
    if not item:
        return jsonify({'success': False, 'error': 'Item not found'}), 404

    if 'cart' not in session:
        session['cart'] = []

    session['cart'].append(item_id)
    session.modified = True

    return jsonify({
        'success': True,
        'item_name': item['name'],
        'cart_count': len(session['cart'])
    })


@app.route('/remove_from_cart', methods=['POST'])
def remove_from_cart():
    if 'username' not in session:
        return jsonify({'success': False, 'error': 'Not logged in'}), 401

    username = session['username']
    item_id = request.form.get('item_id')

    if 'cart' not in session:
        session['cart'] = []

    if item_id in session['cart']:
        session['cart'].remove(item_id)
        session.modified = True
        logger.info(f'User {username} removed {item_id} from cart')
        return jsonify({'success': True})
    else:
        return jsonify({'success': False, 'error': 'Item not in cart'}), 400


@app.route('/checkout', methods=['POST'])
def checkout():
    logger.debug('=== CHECKOUT REQUEST ===')
    logger.debug(f'Session: {session}')
    logger.debug(f'Form data: {request.form}')

    if 'username' not in session:
        return jsonify({'success': False, 'error': 'Not logged in'}), 401

    username = session['username']
    users = load_users()
    user = users.get(username)

    if not user:
        logger.error(f'User not found: {username}')
        return jsonify({'success': False, 'error': 'User not found'}), 404

    cart_items = session.get('cart', [])
    if not cart_items:
        return jsonify({'success': False, 'error': 'Cart is empty'}), 400

    # Calculate total cost with quantities from form
    total_cost = 0
    purchased_items_list = []

    for item_id in set(cart_items):  # unique items
        quantity_key = f'quantity_{item_id}'
        quantity = request.form.get(quantity_key)

        try:
            quantity = int(quantity)
        except:
            return jsonify({'success': False, 'error': f'Invalid quantity for {item_id}'}), 400

        item = next((i for i in AVAILABLE_ITEMS if i['id'] == item_id), None)
        if not item:
            continue

        item_cost = item['price'] * quantity
        total_cost += item_cost
        purchased_items_list.append(item_id)

        logger.debug(
            f'Item: {item_id}, Quantity: {quantity}, Cost: {item_cost}')

    logger.debug(
        f'Total cost: {total_cost}, User balance: {user.get("balance", 0)}')

    if user['balance'] < total_cost:
        logger.warning(
            f'Insufficient balance: {user["balance"]} < {total_cost}')
        return jsonify({'success': False, 'error': 'Insufficient balance'}), 400

    user['balance'] -= total_cost

    if 'purchased_items' not in user:
        user['purchased_items'] = []

    # Add items to purchased_items
    for item_id in purchased_items_list:
        if item_id not in user['purchased_items']:
            user['purchased_items'].append(item_id)

    logger.debug(f'New balance: {user["balance"]}')

    users[username] = user
    save_users(users)

    # Clear cart
    session['cart'] = []
    session.modified = True

    logger.debug('Checkout successful!')

    return jsonify({
        'success': True,
        'new_balance': user['balance'],
        'total_cost': total_cost
    })


@app.route('/admin/update_secret', methods=['POST'])
def admin_update_secret():
    logger.debug('=== ADMIN UPDATE SECRET REQUEST ===')
    logger.debug(f'Session: {session}')
    logger.debug(f'Form data: {request.form}')

    if 'username' not in session:
        return jsonify({'success': False, 'error': 'Not logged in'}), 401

    username = session['username']
    users = load_users()
    user = users.get(username)

    if not user or not user.get('is_admin'):
        logger.warning(f'Non-admin user {username} tried to update secret')
        return jsonify({'success': False, 'error': 'Access denied'}), 403

    item_id = request.form.get('item_id')
    new_secret = request.form.get('secret')

    if not item_id or not new_secret:
        return jsonify({'success': False, 'error': 'Missing parameters'}), 400

    item = next((i for i in AVAILABLE_ITEMS if i['id'] == item_id), None)
    if not item:
        return jsonify({'success': False, 'error': 'Item not found'}), 404

    secrets = load_secrets()
    secrets[item_id] = new_secret
    save_secrets(secrets)

    logger.info(f'Admin {username} updated secret for {item_id}')

    return jsonify({
        'success': True,
        'item_id': item_id,
        'message': 'Secret updated successfully'
    })


@app.route('/get_secrets')
def get_secrets():
    logger.debug('=== GET SECRETS REQUEST ===')
    logger.debug(f'Session: {session}')
    logger.debug(f'Args: {request.args}')

    if 'username' not in session:
        logger.warning('User not logged in for secrets')
        return jsonify({'success': False, 'error': 'Not logged in'}), 401

    username = session['username']
    item_id = request.args.get('item_id')

    logger.debug(f'Username: {username}, Item ID: {item_id}')

    users = load_users()
    user = users.get(username)

    if not user:
        return jsonify({'success': False, 'error': 'User not found'}), 404

    if 'purchased_items' not in user:
        user['purchased_items'] = []

    # Check if user has purchased this item at least once
    if item_id not in user['purchased_items']:
        return jsonify({'success': False, 'error': 'You must purchase this item first'}), 403

    # Get secret from global storage
    secrets = load_secrets()
    secret = secrets.get(item_id, 'NO_SECRET_AVAILABLE')

    logger.debug(f'Found secret for item {item_id}: {secret}')

    return jsonify({
        'success': True,
        'secrets': [secret]  # Return as list for compatibility
    })


if __name__ == '__main__':
    init_data()
    app.run(host='0.0.0.0', port=5000, debug=False)
