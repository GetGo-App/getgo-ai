import os
from fastapi import APIRouter, HTTPException, Depends
from fastapi.security import APIKeyHeader

from agents.models import service
from agents_framework.tools import create_execution_wout_edit_template, data_prompts
from .schemas import MessageInput ,ChatAgentResponse, OutputLocation


header_scheme = APIKeyHeader(name="X-API-Key", auto_error=False)
API_HEADER_KEY = os.getenv("API_HEADER_KEY")

# Router basic information
router = APIRouter(
    prefix = "/agents",
    tags = ["Chat"],
    responses = {404: {"description": "Not found"}}
)

# Root endpoint for the router.
@router.get("/")
async def agents_root():
    return {"message": "Hello there conversational ai!"}


@router.post("/chat-agent")
async def chat_completion(
    message: MessageInput,
    user_status,
    api_key: APIKeyHeader = Depends(header_scheme)
                    
) -> ChatAgentResponse:
    """
    Get a response from the AI model given a question and history conversation from the client 
    using the chat completion endpoint.

    The response is a json object with the following structure:
    ```
    {
        "text": "string",
        "ids_location": "list",
    }
    ```
    """

    check_api_key(api_key)
    
    message = message.model_dump()
    if not message:
        return HTTPException(
            status_code = 404,
            detail = "Messages not found. Please provide the messages with history."
        )
    
    user_question = message["question"]
    hist_messages = message["history"]

    chat_history = []
    if hist_messages and len(hist_messages[0]) > 0:
        chat_history = hist_messages
    
    question_type = classify_question_type(user_question)
    if question_type == "search_web" and user_status != "Premium":
        return ChatAgentResponse(texts_message="Rất tiếc, hiện tại bạn chưa thể sử dụng tính năng này. Hãy nâng cấp lên gói Premium ngay hôm nay để có thể trải nghiệm không giới hạn và mở khóa những tính năng tuyệt vời khác cho chuyến đ cho mình!")

    text_message, location_message = await service.answer_to_messages(query=user_question, chat_history=chat_history, question_type=question_type)
    # log.info(f"Agent response: {response['text']}, Sources: {response['ids_location']}")

    return ChatAgentResponse(texts_message=text_message, locations_message=location_message) 
    # return {"text": text, "ids_location": ids_location}

def classify_question_type(query: str): 
    question_type = create_execution_wout_edit_template(query, data_prompts["question_type_classification"]).content.replace('`', "").replace("Tags", "").strip()
    # question_type = classifer_question_execution.invoke(query).content.replace('`', "").replace("Tags", "").strip()
    print(question_type)
    return question_type



def check_api_key(api_key: str = Depends(header_scheme)):
    if api_key not in API_HEADER_KEY:
        raise HTTPException(
            status_code = 403,
            detail = "Invalid API"
        )