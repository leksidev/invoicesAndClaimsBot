from aiogram import Router, F
from aiogram.types import Message

from repositories.claim import ClaimRepository

router = Router()


@router.message(F.text == "Посмотреть претензии")
async def get_climes_list(message: Message):
    claims = await ClaimRepository.get_all_claims()
    for claim in claims:
        await message.answer(f"Номер претензии: {claim.claim_id}\n"
                             f"описание претензии: {claim.description}\n"
                             f"сумма претензии: {claim.amount}\n"
                             f"email:{claim.email}")

