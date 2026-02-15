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
        org = await self.get_organization(org_id)
        if not org:
            return None

        if org.invite_token:
            return org.invite_token

        token = secrets.token_urlsafe(16)
        org.invite_token = token
        await self.db.commit()
        return token

    async def join_organization_via_token(self, user_id: str, token: str) -> Optional[Membership]:
        result = await self.db.execute(
            select(Organization).where(Organization.invite_token == token)
        )
        org = result.scalars().first()
        if not org:
            return None

        result = await self.db.execute(
            select(Membership).where(
                Membership.user_id == user_id,
                Membership.organization_id == org.id
            )
        )
        existing_membership = result.scalars().first()
        if existing_membership:
            return existing_membership

        admins_result = await self.db.execute(
            select(Membership).where(
                Membership.organization_id == org.id,
                Membership.role.in_(["owner", "admin"])
            )
        )
        admins = admins_result.scalars().all()

        role = org.default_role if org.default_role else "member"
        if len(admins) == 0:
            role = "admin"

        membership = Membership(
            user_id=user_id,
            organization_id=org.id,
            role=role
        )
        self.db.add(membership)
        await self.db.commit()
        await self.db.refresh(membership)
        return membership

    async def remove_member(self, org_id: str, user_id: str, requestor_role: str) -> bool:
        if requestor_role not in ["owner", "admin"]:
            return False

        result = await self.db.execute(
            select(Membership).where(
                Membership.user_id == user_id,
                Membership.organization_id == org_id
            )
        )
        membership = result.scalars().first()
        if not membership:
            return False

        members_result = await self.db.execute(
            select(Membership).where(Membership.organization_id == org_id)
        )
        all_members = members_result.scalars().all()

        if len(all_members) > 1:
            if membership.role in ["owner", "admin"]:
                admins_result = await self.db.execute(
                    select(Membership).where(
                        Membership.organization_id == org_id,
                        Membership.role.in_(["owner", "admin"]),
                        Membership.id != membership.id
                    )
                )
                other_admins = admins_result.scalars().all()
                if len(other_admins) == 0:
                    return False

        await self.db.delete(membership)
        await self.db.commit()
        return True

    async def change_role(self, org_id: str, user_id: str, new_role: str, requestor_role: str) -> Optional[Membership]:
        if requestor_role not in ["owner", "admin"]:
            return None

        if new_role not in ["member", "admin", "owner"]:
            return None

        result = await self.db.execute(
            select(Membership).where(
                Membership.user_id == user_id,
                Membership.organization_id == org_id
            )
        )
        membership = result.scalars().first()
        if not membership:
            return None

        membership.role = new_role
        await self.db.commit()
        await self.db.refresh(membership)
        return membership

    async def leave_organization(self, org_id: str, user_id: str) -> bool:
        result = await self.db.execute(
            select(Membership).where(
                Membership.user_id == user_id,
                Membership.organization_id == org_id
            )
        )
        membership = result.scalars().first()
        if not membership:
            return False

        members_result = await self.db.execute(
            select(Membership).where(Membership.organization_id == org_id)
        )
        all_members = members_result.scalars().all()

        if len(all_members) == 1:
            await self.db.delete(membership)
            await self.db.commit()
            return True

        if membership.role in ["owner", "admin"]:
            admins_result = await self.db.execute(
                select(Membership).where(
                    Membership.organization_id == org_id,
                    Membership.role.in_(["owner", "admin"]),
                    Membership.id != membership.id
                )
            )
            other_admins = admins_result.scalars().all()
            if len(other_admins) == 0:
                return False

        await self.db.delete(membership)
        await self.db.commit()
        return True
