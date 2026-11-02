"""The {{PROJECT_NAME}} Agent."""

import os

import httpx
from dotenv import load_dotenv
from langchain.agents import create_agent
from langchain_core.language_models import BaseChatModel
from langchain_core.tools import tool
from langchain_openai import ChatOpenAI
from pydantic import SecretStr

load_dotenv(override=True)

BACKEND_URL = "http://localhost:8000"
OPENROUTER_BASE_URL = "https://openrouter.ai/api/v1"
DEFAULT_MODEL = "{{MODEL}}"
SYSTEM_PROMPT = """You are the {{PROJECT_NAME}} Agent.
Check that the backend is running, then say hello."""


def backend() -> httpx.Client:
    """Return a client for the backend."""
    return httpx.Client(base_url=BACKEND_URL, timeout=10)


@tool
def check_backend() -> str:
    """Check whether the backend is running."""
    with backend() as client:
        response = client.get("/api/health")
    response.raise_for_status()
    return response.json()["status"]


def model() -> ChatOpenAI:
    """Return the model named in MODEL_NAME, or the default model."""
    return ChatOpenAI(
        model=os.getenv("MODEL_NAME") or DEFAULT_MODEL,
        base_url=OPENROUTER_BASE_URL,
        api_key=SecretStr(os.environ["OPENROUTER_API_KEY"]),
    )


def run(request: str, thread_id: str, llm: BaseChatModel | None = None) -> str:
    """Run the agent on one request and return its final reply."""
    agent = create_agent(
        llm or model(), tools=[check_backend], system_prompt=SYSTEM_PROMPT
    )
    result = agent.invoke(
        {"messages": [{"role": "user", "content": request}]},
        config={"configurable": {"thread_id": thread_id}},
    )
    return result["messages"][-1].text
