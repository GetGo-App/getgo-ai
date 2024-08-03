from typing import List
from pydantic import BaseModel

from langchain.docstore.document import Document
from typing import Optional

# # #########################################
# # Internal schemas
# # #########################################

class MessageInput(BaseModel):
    question: str
    history: None | List[dict] 


# # #########################################
# # API schemas
# # #########################################

class OutputLocation(BaseModel):
    locations: List[int]
    message: str

class ChatAgentResponse(BaseModel):
    texts_message: str | None
    locations_message: Optional[None | OutputLocation] = None

