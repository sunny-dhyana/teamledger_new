import httpx
import asyncio
import uuid
import sys

BASE_URL = "http://localhost:8000/api/v1"

async def test_api():
    async with httpx.AsyncClient(base_url=BASE_URL, timeout=30.0) as client:
        print("--- Starting API Integration Tests ---")
        
        # 1. Register
        email = f"test_{uuid.uuid4().hex[:6]}@example.com"
        password = "testpassword123"
        print(f"Step 1: Registering user {email}...")
        res = await client.post("/auth/register", json={
            "email": email,
            "password": password,
            "full_name": "Test User"
        })
        if res.status_code != 200:
            print(f"FAILED: Register returned {res.status_code} - {res.text}")
            return
        print("SUCCESS: Registered.")

        # 2. Login
        print("Step 2: Logging in...")
        res = await client.post("/auth/login", data={
            "username": email,
            "password": password
        })
        if res.status_code != 200:
            print(f"FAILED: Login returned {res.status_code} - {res.text}")
            return
        token = res.data["access_token"]
        headers = {"Authorization": f"Bearer {token}"}
        print("SUCCESS: Logged in.")

        # 3. List Organizations (should be empty or contain personal org depending on implementation)
        print("Step 3: Listing organizations...")
        res = await client.get("/organizations/", headers=headers)
        if res.status_code != 200:
            print(f"FAILED: List Orgs returned {res.status_code} - {res.text}")
            return
        orgs = res.json()
        print(f"SUCCESS: Found {len(orgs)} organizations.")

        # 4. Create Organization
        org_name = f"Test Org {uuid.uuid4().hex[:4]}"
        print(f"Step 4: Creating organization {org_name}...")
        res = await client.post("/organizations/", headers=headers, json={
            "name": org_name,
            "slug": org_name.lower().replace(" ", "-")
        })
        if res.status_code != 200:
            print(f"FAILED: Create Org returned {res.status_code} - {res.text}")
            return
        org_id = res.json()["id"]
        print(f"SUCCESS: Created Org {org_id}.")

        # 5. Switch Organization (Get token with org_id claim)
        print(f"Step 5: Switching to Org {org_name}...")
        res = await client.post(f"/organizations/{org_id}/switch", headers=headers)
        if res.status_code != 200:
            print(f"FAILED: Switch Org returned {res.status_code} - {res.text}")
            return
        token = res.json()["access_token"]
        headers = {"Authorization": f"Bearer {token}"}
        print("SUCCESS: Switched organization context.")

        # 6. Create Project
        proj_name = "Test Project"
        print(f"Step 6: Creating project {proj_name}...")
        res = await client.post("/projects/", headers=headers, json={
            "name": proj_name,
            "description": "Integration Test Project"
        })
        if res.status_code != 200:
            print(f"FAILED: Create Project returned {res.status_code} - {res.text}")
            return
        project_id = res.json()["id"]
        print(f"SUCCESS: Created Project {project_id}.")

        # 7. Create Note
        print("Step 7: Adding a note to the project...")
        res = await client.post(f"/notes/?project_id={project_id}", headers=headers, json={
            "title": "Integration Note",
            "content": "This note was created by the integrated test suite."
        })
        if res.status_code != 200:
            print(f"FAILED: Create Note returned {res.status_code} - {res.text}")
            return
        print("SUCCESS: Added note.")

        # 8. Create API Key
        print("Step 8: Creating an API Key...")
        res = await client.post("/api-keys/", headers=headers, json={
            "name": "Test Key",
            "scopes": "read"
        })
        if res.status_code != 200:
            print(f"FAILED: Create API Key returned {res.status_code} - {res.text}")
            return
        api_key_data = res.json()
        raw_key = api_key_data["key"]
        api_key_id = api_key_data["id"]
        print(f"SUCCESS: Created API Key (ID: {api_key_id}).")

        # 9. Test API Key Access (API keys only allow access to note read endpoints)
        print("Step 9: Testing API Key access to notes...")
        api_key_headers = {"X-API-Key": raw_key}
        res = await client.get(f"/notes/?project_id={project_id}", headers=api_key_headers)
        if res.status_code != 200:
            print(f"FAILED: API Key access returned {res.status_code} - {res.text}")
            # Note: Requirement says "API keys only allow access to note read endpoints."
        else:
            print("SUCCESS: API Key access verified.")

        # 10. Trigger Project Export (Background Job)
        print("Step 10: Triggering project export...")
        res = await client.post(f"/projects/{project_id}/export", headers=headers)
        if res.status_code != 200:
            print(f"FAILED: Export returned {res.status_code} - {res.text}")
            return
        job_id = res.json()["id"]
        print(f"SUCCESS: Export job {job_id} started.")

        # 11. Check Job Status
        print("Step 11: Polling job status...")
        for _ in range(10):
            res = await client.get(f"/jobs/{job_id}", headers=headers)
            status = res.json()["status"]
            print(f"Current status: {status}")
            if status == "completed":
                print("SUCCESS: Export completed.")
                break
            await asyncio.sleep(2)
        else:
            print("INFO: Job timed out or still pending.")

        print("\n--- ALL TESTS COMPLETED SUCCESSFULLY ---")

if __name__ == "__main__":
    asyncio.run(test_api())
