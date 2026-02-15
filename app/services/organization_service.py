from typing import List, Optional
import secrets
import hashlib
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.models.organization import Organization
from app.models.membership import Membership
from app.models.user import User
from app.schemas.organization import OrganizationCreate, OrganizationUpdate

class OrganizationService:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def create_organization(self, user: User, org_in: OrganizationCreate) -> Organization:
        # Auto-generate slug from name if not provided
        if not org_in.slug:
            import re
            # Convert to lowercase, replace spaces with hyphens, remove special chars
            slug = org_in.name.lower().strip()
            slug = re.sub(r'[^\w\s-]', '', slug)
            slug = re.sub(r'[-\s]+', '-', slug)
            # Ensure uniqueness by appending random suffix if needed
            base_slug = slug
            counter = 1
            while True:
                result = await self.db.execute(select(Organization).where(Organization.slug == slug))
                if not result.scalars().first():
                    break
                slug = f"{base_slug}-{counter}"
                counter += 1
        else:
            slug = org_in.slug
        
        db_org = Organization(name=org_in.name, slug=slug)
        self.db.add(db_org)
        await self.db.commit()
        await self.db.refresh(db_org)

        # Add creator as owner
        membership = Membership(user_id=user.id, organization_id=db_org.id, role="owner")
        self.db.add(membership)
        await self.db.commit()
        
        return db_org

    async def get_user_organizations(self, user_id: str) -> List[Organization]:
        # Join Membership and Organization
        stmt = (
            select(Organization)
            .join(Membership)
            .where(Membership.user_id == user_id)
        )
        result = await self.db.execute(stmt)
        return result.scalars().all()

    async def get_organization(self, org_id: str) -> Optional[Organization]:
        result = await self.db.execute(select(Organization).where(Organization.id == org_id))
        return result.scalars().first()

    async def generate_invite_token(self, org_id: str) -> str:
        """Generate a simple invite token for the organization.
        In production, this should be stored with expiry and be single-use."""
        # For simplicity, we'll create a token that encodes org_id
        # Format: base64(org_id + random_secret)
        # In real app, store this in a separate table with expiry
        import base64
        secret = secrets.token_urlsafe(16)
        token_data = f"{org_id}:{secret}"
        token = base64.urlsafe_b64encode(token_data.encode()).decode()
        return token

    async def join_organization_via_token(self, user_id: str, token: str) -> Optional[Membership]:
        """Join an organization using an invite token.
        In production, validate token expiry and single-use from database."""
        import base64
        try:
            # Decode token
            token_data = base64.urlsafe_b64decode(token.encode()).decode()
            org_id = token_data.split(':')[0]

            # Verify organization exists
            org = await self.get_organization(org_id)
            if not org:
                return None

            # Check if user is already a member
            result = await self.db.execute(
                select(Membership).where(
                    Membership.user_id == user_id,
                    Membership.organization_id == org_id
                )
            )
            existing_membership = result.scalars().first()
            if existing_membership:
                return existing_membership

            # Create membership
            membership = Membership(
                user_id=user_id,
                organization_id=org_id,
                role="member"
            )
            self.db.add(membership)
            await self.db.commit()
            await self.db.refresh(membership)
            return membership

        except Exception:
            return None
