# Define a tool by writing a function, and annotating with @tool decorator.
from typing import Type, Optional

from langchain_community.tools.asknews.tool import SearchInput
from langchain_community.utilities import GoogleSearchAPIWrapper
from langchain_core.callbacks import CallbackManagerForToolRun, AsyncCallbackManagerForToolRun
from langchain_core.tools import tool, BaseTool
from pydantic.v1 import BaseModel


# See https://python.langchain.com/v0.1/docs/modules/tools/custom_tools/


@tool
def add(a, b):
    """Add two numbers together"""
    return a + b
#
# @tool
# def search_fastapi_docs(query: str):
#     """Searches fast api documentation"""
#     return elasticsearch.query(query, "fastapidocs")
#

@tool
def create_api_template() -> str:
    """Create a Fast API template"""

    return """
from typing import List
from fastapi import APIRouter, Body, Depends, HTTPException, status, Path
from sqlalchemy.orm import Session
from data.player_database import OrmSession
from models.player_model import PlayerModel
from services import player_service

api_router = APIRouter()

def get_orm_session():
    orm_session = OrmSession()
    try:
        yield orm_session
    finally:
        orm_session.close()

@api_router.post(
    "/players/",
    status_code=status.HTTP_201_CREATED,
    summary="Creates a new Player",
)
def post(
    player_model: PlayerModel = Body(...),
    orm_session: Session = Depends(get_orm_session),
):
    player = player_service.retrieve_by_id(orm_session, player_model.id)

    if player:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT)

    player_service.create(orm_session, player_model)

@api_router.get(
    "/players/",
    response_model=List[PlayerModel],
    status_code=status.HTTP_200_OK,
    summary="Retrieves a collection of Players"
)
def get_all(
    orm_session: Session = Depends(get_orm_session)
):
    players = player_service.retrieve_all(orm_session)
    return players

@api_router.get(
    "/players/{player_id}",
    response_model=PlayerModel,
    status_code=status.HTTP_200_OK,
    summary="Retrieves a Player by its Id"
)
def get_by_id(
    player_id: int = Path(..., title="The Id of the Player"),
    orm_session: Session = Depends(get_orm_session)
):
    player = player_service.retrieve_by_id(orm_session, player_id)

    if not player:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)

    return player

@api_router.get(
    "/players/squadnumber/{squad_number}",
    response_model=PlayerModel,
    status_code=status.HTTP_200_OK,
    summary="Retrieves a Player by its Squad Number"
)
def get_by_squad_number(
    squad_number: int = Path(..., title="The Squad Number of the Player"),
    orm_session: Session = Depends(get_orm_session)
):
    player = player_service.retrieve_by_squad_number(orm_session, squad_number)

    if not player:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)

    return player

@api_router.put(
    "/players/{player_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Updates an existing Player"
)
def put(
    player_id: int = Path(..., title="The Id of the Player"),
    player_model: PlayerModel = Body(...),
    orm_session: Session = Depends(get_orm_session),

):
    player = player_service.retrieve_by_id(orm_session, player_id)

    if not player:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)

    player_service.update(orm_session, player_model)

@api_router.delete(
    "/players/{player_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Deletes an existing Player"
)
def delete(
    player_id: int = Path(..., title="The Id of the Player"),
    orm_session: Session = Depends(get_orm_session)
):
    player = player_service.retrieve_by_id(orm_session, player_id)

    if not player:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Player not found")

    player_service.delete(orm_session, player_id)
"""


# Search tools
# See https://python.langchain.com/v0.2/docs/integrations/tools/google_search/
@tool
def google_search(query):
    """
    Run a Google search for the query
    """
    search = GoogleSearchAPIWrapper()
    return search.run(query)

#  TODO - Vector search / Elasticsearch tool (index documents, enable search)
# See knowledge/document_loaders.py

# class SearchFastApiDocs(BaseTool):
#     name = "search_fast_api_docs"
#     description = "useful for when you need to answer questions about current events"
#     args_schema: Type[BaseModel] = SearchInput
#
#     def __init__(self):
#         fast_api_docs_loader = RecursiveUrlLoader(
#             "https://fastapi.tiangolo.com/tutorial/"
#         )
#         fast_api_docs_loader.load()
#
#     def _run(
#         self, query: str, run_manager: Optional[CallbackManagerForToolRun] = None
#     ) -> str:
#         """Use the tool."""
#         return "LangChain"
#
#     async def _arun(
#         self, query: str, run_manager: Optional[AsyncCallbackManagerForToolRun] = None
#     ) -> str:
#         """Use the tool asynchronously."""
#         raise NotImplementedError("custom_search does not support async")
#

