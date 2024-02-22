from sqlalchemy import select

from database import new_session
from models.claims_orm import ClaimsOrm


class ClaimRepository:
    @classmethod
    async def add_claim(cls, claim: ClaimsOrm) -> int:
        async with new_session() as session:
            new_claim = claim
            claim.invoice_id = int(claim.invoice_id)
            session.add(claim)
            await session.flush()
            await session.commit()
            return new_claim.claim_id
