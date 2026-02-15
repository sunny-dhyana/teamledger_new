
import httpx
import asyncio
import uuid
import sys

BASE_URL = "http://localhost:8003/api/v1"

async def test_access_controls():
    async with httpx.AsyncClient(base_url=BASE_URL, timeout=30.0) as client:
        print("--- Starting Note Access Control Tests ---")
        
        # 1. Setup: Register and Login
        email = f"test_ac_{uuid.uuid4().hex[:6]}@example.com"
        password = "testpassword123"
        print(f"Step 1: Registering user {email}...")
        await client.post("/auth/register", json={
            "email": email,
            "password": password,
            "full_name": "Test User"
        })
        
        res = await client.post("/auth/login", data={
            "username": email,
            "password": password
        })
        if res.status_code != 200:
            print(f"Login failed: {res.status_code} - {res.text}")
            return
        token = res.json()["data"]["access_token"]
        headers = {"Authorization": f"Bearer {token}"}
        
        # Create Org
        org_name = f"Test Org {uuid.uuid4().hex[:4]}"
        res = await client.post("/organizations/", headers=headers, json={
            "name": org_name,
            "slug": org_name.lower().replace(" ", "-")
        })
        org_id = res.json()["data"]["id"]
        
        # Switch Org
        res = await client.post(f"/organizations/{org_id}/switch", headers=headers)
        token = res.json()["data"]["access_token"]
        headers = {"Authorization": f"Bearer {token}"}
        
        # Create Project
        res = await client.post("/projects/", headers=headers, json={
            "name": "Access Control Project",
            "description": "Project for testing AC"
        })
        project_id = res.json()["data"]["id"]
        
        # Create Note
        print("Step 2: Creating a note...")
        res = await client.post(f"/notes/?project_id={project_id}", headers=headers, json={
            "title": "Access Control Note",
            "content": "Original Content"
        })
        note_id = res.json()["data"]["id"]
        
        # 2. Test View-Only Access
        print("\nStep 3: Testing View-Only Access...")
        res = await client.post(f"/notes/{note_id}/share?project_id={project_id}&access_level=view", headers=headers)
        print(f"DEBUG Response Text: {res.text}")
        view_data = res.json()["data"]
        view_token = view_data["share_token"]
        print(f"Generated View Token: {view_token}")
        
        # Verify access level
        if view_data.get("access_level") != "view":
            print(f"FAILED: Expected access_level='view'. Got response data: {view_data}")
        else:
            print("SUCCESS: Access level correct in generation response.")
            
        # Get Shared Note
        res = await client.get(f"/notes/shared/{view_token}")
        shared_note = res.json()["data"]
        if shared_note.get("access_level") != "view":
             print(f"FAILED: Shared note response missing correct access_level. Got: {shared_note.get('access_level')}. Full data: {shared_note}")
        
        # Try to Edit with View Token
        print("Attempting to edit with view token (should fail)...")
        res = await client.put(f"/notes/shared/{view_token}", json={
            "content": "HACKED CONTENT"
        })
        if res.status_code == 403: # Or 403/401
            print(f"SUCCESS: Edit denied as expected (Status: {res.status_code})")
        else:
            print(f"FAILED: Edit should have been denied. Status: {res.status_code}")
            
        # 3. Test Edit Access
        print("\nStep 4: Testing Edit Access...")
        # Update permissions to Edit
        res = await client.post(f"/notes/{note_id}/share?project_id={project_id}&access_level=edit", headers=headers)
        edit_data = res.json()["data"]
        edit_token = edit_data["share_token"]
        print(f"Generated Edit Token: {edit_token} (Should be same as view token but updated perm)")
        
        if edit_data.get("access_level") != "edit":
            print("FAILED: Expected access_level='edit'")
            
        # Try to Edit with Edit Token
        print("Attempting to edit with edit token (should succeed)...")
        new_content = "UPDATED CONTENT VIA LINK"
        res = await client.put(f"/notes/shared/{edit_token}", json={
            "content": new_content
        })
        
        if res.status_code == 200:
            print("SUCCESS: Edit succeeded.")
            if res.json()["data"]["content"] == new_content:
                 print("SUCCESS: Content updated correctly.")
            else:
                 print("FAILED: Content mismatch.")
        else:
            print(f"FAILED: Edit failed. Status: {res.status_code} - {res.text}")

        print("\n--- ALL TESTS COMPLETED ---")

if __name__ == "__main__":
    asyncio.run(test_access_controls())
