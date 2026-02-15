from typing import List, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
import secrets
from app.models.note import Note
from app.schemas.note import NoteCreate, NoteUpdate, SharedNoteUpdate

class NoteService:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def create_note(self, project_id: str, org_id: str, user_id: str, note_in: NoteCreate) -> Note:
        db_note = Note(
            project_id=project_id,
            organization_id=org_id,
            title=note_in.title,
            content=note_in.content,
            created_by=user_id,
            version=1
        )
        self.db.add(db_note)
        await self.db.commit()
        await self.db.refresh(db_note)
        return db_note

    async def get_notes(self, project_id: str, org_id: str) -> List[Note]:
        result = await self.db.execute(select(Note).where(
            Note.project_id == project_id,
            Note.organization_id == org_id
        ))
        return result.scalars().all()

    async def get_note(self, note_id: str, project_id: str, org_id: str) -> Optional[Note]:
        result = await self.db.execute(select(Note).where(
            Note.id == note_id,
            Note.project_id == project_id,
            Note.organization_id == org_id
        ))
        return result.scalars().first()

    async def update_note(self, note_id: str, project_id: str, org_id: str, note_in: NoteUpdate) -> Optional[Note]:
        note = await self.get_note(note_id, project_id, org_id)
        if not note:
            return None
        
        update_data = note_in.model_dump(exclude_unset=True)
        for key, value in update_data.items():
            setattr(note, key, value)
        
        # Increment version
        note.version += 1

        self.db.add(note)
        await self.db.commit()
        await self.db.refresh(note)
        return note

    async def generate_share_token(self, note_id: str, project_id: str, org_id: str, access_level: str = "view") -> Optional[str]:
        """Generate a unique share token for a note"""
        note = await self.get_note(note_id, project_id, org_id)
        if not note:
            return None
        
        # If already has a share token, return it
        if note.share_token:
            # If access level changed, update it
            if note.share_access_level != access_level:
                note.share_access_level = access_level
                self.db.add(note)
                await self.db.commit()
                await self.db.refresh(note)
            return note.share_token
        
        # Generate a secure random token
        share_token = secrets.token_urlsafe(32)
        note.share_token = share_token
        note.share_access_level = access_level
        
        self.db.add(note)
        await self.db.commit()
        await self.db.refresh(note)
        
        return share_token

    async def revoke_share_token(self, note_id: str, project_id: str, org_id: str) -> bool:
        """Revoke the share token for a note"""
        note = await self.get_note(note_id, project_id, org_id)
        if not note:
            return False
        
        note.share_token = None
        note.share_access_level = "view" # Reset to default
        
        self.db.add(note)
        await self.db.commit()
        
        return True

    async def get_note_by_share_token(self, share_token: str) -> Optional[Note]:
        """Get a note by its share token (public access)"""
        result = await self.db.execute(select(Note).where(
            Note.share_token == share_token
        ))
        return result.scalars().first()

    async def update_shared_note(self, share_token: str, note_in: SharedNoteUpdate) -> Optional[Note]:
        """Update a shared note content if access level permits"""
        note = await self.get_note_by_share_token(share_token)
        if not note:
            return None
            
        if note.share_access_level != "edit":
            return None
            
        # Only allow content update for shared notes
        note.content = note_in.content
        note.version += 1
        
        self.db.add(note)
        await self.db.commit()
        await self.db.refresh(note)
        return note
