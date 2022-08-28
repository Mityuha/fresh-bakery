"""Service views."""

from copy import copy
from typing import Dict, Optional, TypedDict

from bakery import Cakeable
from fastapi import APIRouter, Depends
from fastapi.responses import JSONResponse

from ..bakery import MainBakery
from ..controllers.controller import PersonIn, PersonOut, ServiceController


router: APIRouter = APIRouter()


@router.post(
    '/person',
    response_model=TypedDict("PersonId", {"person_id": int}),  # type: ignore
    status_code=201,
    responses={code: {"model": Dict} for code in (400, 500)},
)
async def create_person(
    request: PersonIn,
    controller: ServiceController = Depends(MainBakery.controller),
) -> Dict:
    """Creating person.."""

    person_id: int = await controller.insert_person(request)
    return {"person_id": person_id}


@router.get(
    '/person/{person_id}',
    response_model=PersonOut,
    status_code=200,
    responses={code: {"model": Dict} for code in (400, 404, 500)},
)
async def fetch_person(
    person_id: int,
    controller_cake: Cakeable[ServiceController] = Depends(lambda: copy(MainBakery.controller)),
) -> PersonOut | JSONResponse:
    """Fetching person by id."""

    async with controller_cake as controller:
        person: Optional[PersonOut] = await controller.fetch_person(person_id)

    if not person:
        return JSONResponse({}, status_code=404)

    return person
