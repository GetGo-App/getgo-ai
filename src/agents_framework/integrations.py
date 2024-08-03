import os
# import json
from langchain_openai import ChatOpenAI, OpenAIEmbeddings
from langchain.chains import RetrievalQA
import yaml

from langchain_core.messages import AIMessage, HumanMessage
from langchain_core.prompts import ChatPromptTemplate
# import agents_framework.loggers as logger
# from api.schemas import ChatAgentResponse
import datetime

from .tools import (
    load_retrieval_tool,
    search_searxng_engine,
    generate_response_base_context,
    openai_client_answer,
    data_prompts,
    create_execution_w_custom_message
)
from api.schemas import OutputLocation
from .utils import get_data
from typing import List, Dict, Tuple, Union

# log = logger.get_logger(__name__)

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")




class AgentIntegrationService:
    def __init__(self, model_simple_name="gpt-4o-mini", model_complex_name="gpt4o", model_embed_name="text-embedding-ada-002") -> None:
        self.model_simple_name = model_simple_name
        self.model_complex_name = model_complex_name
        self.llm_model = ChatOpenAI(model=model_simple_name, temperature=0)

        self.embedding_model = OpenAIEmbeddings(model=model_embed_name, chunk_size=1)
        self.retriever_tool = load_retrieval_tool(self.embedding_model)

        self.qa_baseline = RetrievalQA.from_chain_type(
            llm=self.llm_model,
            chain_type="stuff",
            retriever=self.retriever_tool,
            return_source_documents=True,
        )

    async def answer_to_messages(self, query: List[list], chat_history: List[dict] | None, question_type: str) -> Union[str, OutputLocation | None]:
        agent_using = self._route(question_type)
        if agent_using == self.answer_based_search:
            query_reformat = openai_client_answer(
                query, 
                chat_history, 
                model="gpt-4o-mini", 
                template=data_prompts["rephrase_query"]
            )
            if query == 'not_need': query_reformat = query
            answer = agent_using(query_reformat)
        else:
            answer = agent_using(query, chat_history)

        text_message, location_message = "", None
        if question_type in ["ask_personal", "search_web"]: text_message = answer
        else:
            text_message = f"Chào bạn, đây là một lịch trình tham quan thành phố Hồ Chí Minh trong một ngày mà bạn có thể tham khảo:"
            bonus_message = "Đây chỉ là một gợi ý lịch trình, bạn có thể điều chỉnh theo sở thích và thời gian của mình. Chúc bạn có một chuyến tham quan thú vị ở thành phố Hồ Chí Minh!"
            location_message = OutputLocation(locations=answer, message=bonus_message)
        return text_message, location_message

    
    def answer_based_retrieval(self, query, chat_history):
        max_turns = 3
        turn = 0
        while turn < max_turns:
            try:
                batch = self.create_questions(query, chat_history)
                break
            except Exception as e:
                print("Error in creating questions, run again")
                turn += 1
            if turn == max_turns:
                raise e
            else:
                continue
        num_questions, questions = batch["number_of_locations"], batch["questions"]
        locations_index = set()
        print(questions)
        for question in questions:
            locations_index.add(self._retrieval_places(question))
        return list(locations_index)


    def _retrieval_places(self, query):
        response = self.qa_baseline.invoke({"query": query})
        location_index = response["source_documents"][0].metadata["seq_num"] - 1
        return location_index
    
    
    def answer_based_search(self, query):
        results = search_searxng_engine(query)
        context = f"User question: {query}\n\nDocument Retrieved:\n"
        for result in results:
            context += result['snippet'] + "\n"
        date = datetime.datetime.now().isoformat()
        print(context)
        answer = generate_response_base_context(context.strip(), date=date, template=data_prompts['interpreter_web'])
        # print(answer.content)
        return answer.content

    
    def answer_normal(self, user_input: str, chat_history, model_name="gpt-4o-mini") -> str:
        """Extract the token name or name from the user input"""

        messages = [{"role": "system", "content": data_prompts['normal_conversation']}]
        if chat_history and len(chat_history) > 0:
            for mes in chat_history:
                messages.append({"role": "user", "content": mes['question']})
                messages.append({"role": "assistant", "content": mes['answer']})
        messages.append({"role": "user", "content": user_input})

        answer = create_execution_w_custom_message(messages).content

        return answer


    def create_questions(self, user_input: str, chat_history) -> str:
        """Create questions from the user input"""
        messages = [{"role": "system", "content": data_prompts['questions_generation']}]
        if chat_history:
            for mes in chat_history:
                messages.append({"role": "user", "content": mes['question']})
                messages.append({"role": "assistant", "content": mes['answer']})
        messages.append({"role": "user", "content": user_input})

        answer = create_execution_w_custom_message(messages).content

        print(answer)
        data_loaded = yaml.safe_load(answer.replace("```", "").replace("yaml", ""))
        return data_loaded


    def _route(self, question_type):
        match question_type:
            case "plan_trip":
                return self.answer_based_retrieval
            case "ask_personal":
                return self.answer_normal
            case "search_web":
                return self.answer_based_search