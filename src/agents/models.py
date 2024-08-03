import os
from agents_framework.integrations import AgentIntegrationService

# Accessing values from the config file


api_key = os.getenv("OPENAI_API_KEY")
os.environ["OPENAI_API_KEY"] = api_key

MODEL_SIMPLE_NAME="gpt-4o-mini"
MODEL_EMBED_NAME="text-embedding-ada-002"

# Initialize the service
service = AgentIntegrationService(
    model_simple_name   = MODEL_SIMPLE_NAME,
    model_embed_name = MODEL_EMBED_NAME
)

