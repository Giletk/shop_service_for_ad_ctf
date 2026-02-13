#!/usr/bin/env python3

from re import A
import string
import random
import requests
import copy
import sys
import os
from dotenv import load_dotenv


load_dotenv()
argv = copy.deepcopy(sys.argv)


OK, CORRUPT, MUMBLE, DOWN, CHECKER_ERROR = 101, 102, 103, 104, 110
SERVICENAME = "shop"
ADMIN_USERNAME = 'admin'
ADMIN_PASSWORD = 'Xk9mP2vL8qW5nR3jH7tY4uB6cF1sD0zN9xE8aG5wQ2mV7yT3pK6hJ4rL1nB8cX5fZ2'
PORT = os.getenv('PORT')


def get_random_string(N=16):
    return ''.join(random.choice(string.ascii_letters) for i in range(N))


def close(code, public="", private=""):
    if public:
        print(public)
    if private:
        print(private, file=sys.stderr)
    print(f'Exit with code {code}', file=sys.stderr)
    exit(code)


def put(*args):
    team_addr, flag_id, flag = args[:3]

    try:
        base_url = f"http://{team_addr}:{PORT}"
        target_item = 'catnip'

        # Login as admin
        admin_session = requests.Session()

        resp = admin_session.post(f"{base_url}/login", data={
            'username': ADMIN_USERNAME,
            'password': ADMIN_PASSWORD
        }, timeout=5)

        if resp.status_code != 200:
            close(MUMBLE, "Admin login failed")

        # Update secret for the item
        resp = admin_session.post(f"{base_url}/admin/update_secret", data={
            'item_id': target_item,
            'secret': flag
        }, timeout=5)

        if resp.status_code != 200:
            close(MUMBLE, "Failed to update secret")

        # Create a regular user to verify
        username = get_random_string()
        password = get_random_string()

        user_session = requests.Session()
        resp = user_session.post(f"{base_url}/register", data={
            'username': username,
            'password': password
        }, timeout=5)

        if resp.status_code != 200:
            close(MUMBLE, "User registration failed")

        close(OK, f"{username}:{password}:{target_item}")

    except requests.exceptions.RequestException as e:
        close(DOWN, f"Connection error: {e}")
    except Exception as e:
        close(MUMBLE, f"PUT failed: {e}")


def get(*args):
    team_addr, flag_id, flag = args[:3]

    try:

        username = ADMIN_USERNAME
        password = ADMIN_PASSWORD
        item_id = 'catnip'

        base_url = f"http://{team_addr}:{PORT}"
        session = requests.Session()

        resp = session.post(f"{base_url}/login", data={
            'username': username,
            'password': password
        }, timeout=5)

        if resp.status_code != 200:
            close(MUMBLE, "Login failed")

        # Buy the catnip item first to access secrets
        resp = session.post(f"{base_url}/add_to_cart", data={
            'item_id': item_id
        }, timeout=5)

        if resp.status_code != 200:
            close(MUMBLE, "Failed to add item to cart")

        resp = session.post(f"{base_url}/checkout", data={
            f'quantity_{item_id}': '1'
        }, timeout=5)

        if resp.status_code != 200:
            close(MUMBLE, "Failed to buy item")

        # Get secrets for the item
        resp = session.get(
            f"{base_url}/get_secrets?item_id={item_id}", timeout=5)

        if resp.status_code != 200:
            close(MUMBLE, "Failed to get secrets")

        data = resp.json()
        if not data.get('success'):
            close(CORRUPT, "Get secrets failed")

        secrets = data.get('secrets', [])
        if flag not in secrets:
            close(CORRUPT, "Flag not found in secrets")

        close(OK, "Flag retrieved successfully")

    except requests.exceptions.RequestException as e:
        close(DOWN, f"Connection error: {e}")
    except Exception as e:
        close(CORRUPT, f"GET failed: {e}")


def check(*args):
    team_addr = args[0]

    try:
        base_url = f"http://{team_addr}:{PORT}"

        username = get_random_string()
        password = get_random_string()

        session = requests.Session()

        # Register new user
        resp = session.post(f"{base_url}/register", data={
            'username': username,
            'password': password
        }, timeout=5)

        if resp.status_code != 200:
            close(MUMBLE, "Registration failed")

        # Check if redirected to shop
        resp = session.get(f"{base_url}/shop", timeout=5)
        if resp.status_code != 200:
            close(MUMBLE, "Shop page not accessible")

        # Buy an item with quantity
        resp = session.post(f"{base_url}/add_to_cart", data={
            'item_id': 'mouse'
        }, timeout=5)

        if resp.status_code != 200:
            close(MUMBLE, "Failed to add to cart")

        resp = session.post(f"{base_url}/checkout", data={
            'quantity_mouse': '2'
        }, timeout=5)

        if resp.status_code != 200:
            close(MUMBLE, "Failed to checkout")

        data = resp.json()
        if not data.get('success'):
            close(MUMBLE, "Checkout response invalid")
        # Verify secrets work
        resp = session.get(f"{base_url}/get_secrets?item_id=mouse", timeout=5)
        if resp.status_code != 200:
            close(MUMBLE, "Failed to get secrets")

        close(OK, "Service working correctly")

    except requests.exceptions.RequestException as e:
        close(DOWN, f"Connection error: {e}")
    except Exception as e:
        close(DOWN, f"CHECK failed: {e}")


def info(*args):
    close(OK, "vulns: 1")


def error_arg(*args):
    close(CHECKER_ERROR, private=f"Wrong command {sys.argv[1]}")


COMMANDS = {
    'check': check,
    'put': put,
    'get': get,
    'info': info
}


def main():
    if len(argv) < 2:
        close(CHECKER_ERROR, "Not enough args")

    cmd = COMMANDS.get(argv[1], error_arg)
    cmd(*argv[2:])


if __name__ == '__main__':
    main()
