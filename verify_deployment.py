import asyncio
import pytest
from httpx import AsyncClient

# Configuration
BASE_URL = "http://localhost:8000"

@pytest.mark.anyio
async def test_deployment_flow():
    # We use base_url to hit the running server
    async with AsyncClient(base_url=BASE_URL) as ac:
        
        # 1. Register (Randomize email to allow repeated runs)
        import uuid
        random_suffix = str(uuid.uuid4())[:8]
        email = f"user_{random_suffix}@example.com"
        password = "password123"
        print(f"\n1. Registering user {email}...")
        
        res = await ac.post("/api/v1/auth/register", json={
            "email": email,
            "password": password,
            "full_name": "Test User"
        })
        assert res.status_code == 200, f"Register failed: {res.text}"
        user_id = res.json()["id"]

        # 2. Login
        print("2. Logging in...")
        res = await ac.post("/api/v1/auth/login", data={
            "username": email,
            "password": password
        })
        assert res.status_code == 200, f"Login failed: {res.text}"
        token = res.json()["access_token"]
        headers = {"Authorization": f"Bearer {token}"}

        # 3. Create Org
        print("3. Creating Organization...")
        res = await ac.post("/api/v1/organizations/", json={
            "name": f"Org {random_suffix}",
            "slug": f"org_{random_suffix}"
        }, headers=headers)
        assert res.status_code == 200, f"Create Org failed: {res.text}"
        org_id = res.json()["id"]

        # 4. Switch Org (Get New Token)
        print("4. Switching Organization...")
        res = await ac.post(f"/api/v1/organizations/{org_id}/switch", headers=headers)
        assert res.status_code == 200, f"Switch Org failed: {res.text}"
        org_token = res.json()["access_token"]
        org_headers = {"Authorization": f"Bearer {org_token}"}

        # 5. Create Project
        print("5. Creating Project...")
        res = await ac.post("/api/v1/projects/", json={
            "name": "Project X",
            "description": "Top Secret"
        }, headers=org_headers)
        assert res.status_code == 200, f"Create Project failed: {res.text}"
        project_id = res.json()["id"]

        # 6. Create Note
        print("6. Creating Note...")
        res = await ac.post(f"/api/v1/notes/?project_id={project_id}", json={
            "title": "Meeting Notes",
            "content": "Discussed world domination."
        }, headers=org_headers)
        assert res.status_code == 200, f"Create Note failed: {res.text}"
        note_id = res.json()["id"]

        # 7. Get Note (JWT)
        print("7. Getting Note (JWT)...")
        res = await ac.get(f"/api/v1/notes/{note_id}?project_id={project_id}", headers=org_headers)
        assert res.status_code == 200, f"Get Note JWT failed: {res.text}"
        assert res.json()["title"] == "Meeting Notes"

        # 8. Create API Key
        print("8. Creating API Key...")
        res = await ac.post("/api/v1/api-keys/", json={
            "name": "Read Key",
            "scopes": "read"
        }, headers=org_headers)
        assert res.status_code == 200, f"Create API Key failed: {res.text}"
        api_key_val = res.json()["key"]
        api_key_headers = {"X-API-Key": api_key_val}

        # 9. Get Note (API Key)
        print("9. Getting Note (API Key)...")
        res = await ac.get(f"/api/v1/notes/{note_id}?project_id={project_id}", headers=api_key_headers)
        assert res.status_code == 200, f"Get Note API Key failed: {res.text}"
        assert res.json()["title"] == "Meeting Notes"

        # 10. Export Project (Background Task)
        print("10. Exporting Project...")
        res = await ac.post(f"/api/v1/projects/{project_id}/export", headers=org_headers)
        assert res.status_code == 200, f"Export failed: {res.text}"
        job_id = res.json()["id"]
        
        # Poll for job completion
        print(f"11. Polling Job Status (Job ID: {job_id})...")
        for i in range(10):
            res = await ac.get(f"/api/v1/jobs/{job_id}", headers=org_headers)
            status = res.json()["status"]
            print(f"   Attempt {i+1}: {status}")
            if status == "completed":
                print("Job Completed!")
                break
            elif status == "failed":
                pytest.fail("Job failed!")
            await asyncio.sleep(1)
        assert status == "completed"

        print("\nDeployment Verification Successful!")

if __name__ == "__main__":
    import sys
    sys.exit(pytest.main(["-v", __file__]))
