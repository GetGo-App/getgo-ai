import os
import json
import datetime

from openai import OpenAI

from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import Chroma
from langchain_openai import ChatOpenAI
from langchain.storage import LocalFileStore
from langchain.storage._lc_store import create_kv_docstore
from langchain.retrievers import ParentDocumentRetriever
from langchain_core.prompts import ChatPromptTemplate
from langchain_community.utilities import SearxSearchWrapper

from tenacity import (
    retry,
    stop_after_attempt,
    wait_random_exponential,
)  # for exponential backoff

from .utils import get_data

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
SEARXNG_PORT = os.getenv("SEARXNG_PORT")

os.environ["OPENAI_API_KEY"] = OPENAI_API_KEY

openai_client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))


PERSIST_DIRECTORY = "data/indexing/local_vectorstore"
LOCAL_STORE = "data/indexing/local_docstore"
collection_name = "hrpolicy"
PROJECT_ROOT = "./"  # insert your project root directory name here





paths = {
    "normal_conversation": "data/prompts/normal_conversation.txt",
    "question_type_classification": "data/prompts/question_type_classification.txt",
    "questions_generation": "data/prompts/questions_generation.txt",
    "interpreter_web": "data/prompts/interpreter_web.txt",
    "rephrase_query": "data/prompts/rephrase_query.txt",
}

# Load the data
data_prompts = get_data(paths)
current_date = datetime.datetime.now().isoformat()

# Initial search api
searxng_api = SearxSearchWrapper(searx_host=SEARXNG_PORT, k = 20)












def load_retrieval_tool(embedding_model):
    parent_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=0)
    child_splitter = RecursiveCharacterTextSplitter(chunk_size=200, chunk_overlap=0)

    # The vectorstore to use to index the child chunks
    vectorstore = Chroma(
        persist_directory=PERSIST_DIRECTORY,
        collection_name=collection_name,
        embedding_function=embedding_model,
    )

    # The storage layer for the parent documents
    local_store = LocalFileStore(LOCAL_STORE)
    store = create_kv_docstore(local_store)
    retriever_tool = ParentDocumentRetriever(
        vectorstore=vectorstore,
        docstore=store,
        child_splitter=child_splitter,
        parent_splitter=parent_splitter,
    )
    return retriever_tool


@retry(wait=wait_random_exponential(min=1, max=60), stop=stop_after_attempt(6))
def search_searxng_engine(query, engines: list=["google"], enabled_engines: list=["google", "apple_maps"]):
    results = searxng_api.results(
        query,
        num_results=5,
        language="en",
        enabled_engines=enabled_engines,
        engines=engines,
        disabled_engines=['duckduckgo', 'brave'],
    )
    return results


@retry(wait=wait_random_exponential(min=1, max=60), stop=stop_after_attempt(6))
def openai_client_answer(query, history=None, model="gpt-4o-mini", template=""):
    chat_completion = openai_client.chat.completions.create(
        messages=[
            {
                "role": "user",
                "content": template.format(query=query, history=history),
            }
        ],
        model=model,
    )
    return chat_completion.choices[0].message.content 


@retry(wait=wait_random_exponential(min=1, max=60), stop=stop_after_attempt(6))
def generate_response_base_context(context, date, template, model="gpt-4o-mini"):
    chat_completion = openai_client.chat.completions.create(
        messages=[
            {
                "role": "user",
                "content": template.format(context=context, date=date),
            }
        ],
        model=model,
    )
    return chat_completion.choices[0].message


@retry(wait=wait_random_exponential(min=1, max=60), stop=stop_after_attempt(6))
def create_execution_wout_edit_template(input_text, template, model="gpt-4o-mini"):
    chat_completion = openai_client.chat.completions.create(
        messages=[
            {"role": "system", "content": template},
            {"role": "user", "content": input_text}
        ],
        model=model,
        temperature=0
    )
    return chat_completion.choices[0].message


@retry(wait=wait_random_exponential(min=1, max=60), stop=stop_after_attempt(6))
def create_execution_w_custom_message(messages: list, model="gpt-4o-mini"):
    chat_completion = openai_client.chat.completions.create(
        messages=messages,
        model=model,
        temperature=0
    )
    return chat_completion.choices[0].message

# classifer_question_execution = ChatPromptTemplate.from_messages(
#     [
#         ("system", data['question_type_classification']),
#         ("human", "{input}"),
#     ]
# ) | ChatOpenAI(model="gpt-3.5-turbo", temperature=0)


# create_questions_execution = ChatPromptTemplate.from_messages(
#     [
#         ("system", data_prompts['questions_generation']),
#         ("human", "{input}"),
#     ]
# ) | ChatOpenAI(model="gpt-4o", temperature=0)


if __name__ == "__main__":

    question = "Cho tôi vài khách sạn ở gần phố đi bộ Nguyễn Huệ"
    results = search_searxng_engine(question)

    contexts = f"Question of user: {question}\n\n"
    contexts += "There is some contextual information from the web: \n\n"
    for result in results:
        contexts += f"{result['snippet']}\n\n"


    def generate_response(context: str) -> str:
        prompt = data_prompts["interpreter_web"].format(context=context, date=current_date)
        print(prompt)
        location_answer_execution = ChatPromptTemplate.from_messages(
            [
                ("human", "{input}"),
            ]
        ) | ChatOpenAI(model="gpt-4o-mini", temperature=0)


        response = location_answer_execution.invoke(input=prompt).content
        return response.strip()

    response = generate_response(contexts)
    print(response)