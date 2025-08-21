import subprocess
import re
import requests
import json
import os
from bs4 import BeautifulSoup

def maigret_lookup(username):
    print(f"🔍 Running Maigret for @{username}...")
    try:
        result = subprocess.run(['maigret', username, '--json', f'{username}_maigret.json'], timeout=300)
    except Exception as e:
        print(f"Maigret error: {e}")

def sherlock_lookup(username):
    print(f"🕵️‍♂️ Running Sherlock...")
    try:
        subprocess.run(['python3', 'sherlock/sherlock.py', username, '--print-found'], timeout=300)
    except Exception as e:
        print(f"Sherlock error: {e}")

def search_in_bios(file):
    try:
        with open(file, 'r') as f:
            data = json.load(f)
        phones, emails = set(), set()
        for site in data.get("accounts", {}).values():
            bio = site.get("description", "")
            found_phones = re.findall(r'(\+?\d[\d\s\-()]{7,})', bio)
            found_emails = re.findall(r'[\w\.-]+@[\w\.-]+\.\w+', bio)
            phones.update(found_phones)
            emails.update(found_emails)
        return phones, emails
    except Exception as e:
        print(f"Error parsing bios: {e}")
        return set(), set()

def hibp_lookup(email):
    print(f"💥 Checking breaches for {email} via HaveIBeenPwned...")
    headers = {"User-Agent": "osint-script"}
    try:
        resp = requests.get(f"https://haveibeenpwned.com/unifiedsearch/{email}", headers=headers)
        if resp.status_code == 200:
            return True
    except:
        pass
    return False

def emailrep_lookup(email):
    try:
        resp = requests.get(f"https://emailrep.io/{email}")
        if resp.status_code == 200:
            return resp.json()
    except:
        pass
    return {}

def phoneinfoga_lookup(phone):
    print(f"📞 Running PhoneInfoga for {phone}")
    subprocess.run(['phoneinfoga', 'scan', '-n', phone])

def main():
    username = input("🔑 Enter the Telegram username (without @): ").strip()
    maigret_lookup(username)
    sherlock_lookup(username)

    phones, emails = search_in_bios(f"{username}_maigret.json")

    print("\n📱 Found phone numbers:")
    for p in phones:
        print(f"   {p}")
        phoneinfoga_lookup(p)

    print("\n📧 Found emails:")
    for e in emails:
        print(f"   {e}")
        print("   🔍 Breach status:", "Detected" if hibp_lookup(e) else "None")
        rep = emailrep_lookup(e)
        if rep:
            print("   📊 Reputation:", rep.get("reputation", "unknown"))

    print("\n✅ Search completed. Data saved to JSON.")
    print(f"File: {username}_maigret.json")

if __name__ == "__main__":
    main()
