from fastapi import FastAPI

from api.routes import router as ai_agents
# from agents_framework.loggers import setup_applevel_logger

# log = setup_applevel_logger(file_name = 'agents.log')

app = FastAPI()
app.include_router(router = ai_agents)

@app.get("/")
async def root():
    return {"message": "Hello there recommend locations ai from user's demand here!"}
