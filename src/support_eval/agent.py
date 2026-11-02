"""Single-node classifier: reference labels never enter model messages."""
from typing import Literal, TypedDict
from pydantic import BaseModel, ConfigDict, Field
from langchain_core.messages import HumanMessage, SystemMessage
from langchain_fireworks import ChatFireworks
from langgraph.graph import StateGraph, START, END
from .config import Settings


class Prediction(BaseModel):
    model_config = ConfigDict(extra='forbid')
    category: Literal['order_status', 'refund_request', 'product_issue', 'account_help', 'other']
    explanation: str = Field(min_length=1, max_length=600, description='One concise sentence explaining the route')


class State(TypedDict, total=False):
    ticket_text: str
    prediction: dict | None
    usage: dict | None
    error: str | None
    finish_reason: str | None


def build_agent(settings: Settings, prompt: str, *, structured_model=None):
    if structured_model is None:
        if not settings.fireworks_api_key.get_secret_value():
            raise ValueError('FIREWORKS_API_KEY is missing')
        llm = ChatFireworks(model=settings.model, api_key=settings.fireworks_api_key,
                            temperature=settings.temperature, max_tokens=settings.max_tokens,
                            request_timeout=settings.timeout_seconds, max_retries=0)
        structured_model = llm.with_structured_output(Prediction, method='json_schema', include_raw=True)

    def classify(state: State) -> State:
        result = structured_model.invoke([SystemMessage(content=prompt), HumanMessage(content=state['ticket_text'])])
        raw = result.get('raw')
        usage = getattr(raw, 'usage_metadata', None)
        metadata = getattr(raw, 'response_metadata', {})
        parsed = result.get('parsed')
        if parsed is not None:
            parsed = Prediction.model_validate(parsed).model_dump()
        return dict(prediction=parsed, usage=usage, finish_reason=metadata.get('finish_reason'),
                    error='Invalid structured response' if parsed is None else None)

    graph = StateGraph(State)
    graph.add_node('classify', classify)
    graph.add_edge(START, 'classify')
    graph.add_edge('classify', END)
    return graph.compile()
