from sqlalchemy import select

from database import new_session
from models.claims_orm import ClaimsOrm


class ClaimRepository:
    @classmethod
    async def add_claim(cls, claim: ClaimsOrm) -> int:
        async with new_session() as session:
            new_claim = claim
            session.add(claim)
            await session.flush()
            await session.commit()
            return new_claim.claim_id

    @classmethod
    async def get_all_claims(cls) -> list[ClaimsOrm]:
        async with new_session() as session:
            query = select(ClaimsOrm)
            result = await session.execute(query)
            claim_models = result.scalars().all()
            claims = [claim_model for claim_model in claim_models]
            return claims
