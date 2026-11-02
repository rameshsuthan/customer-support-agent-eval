import pytest
from langchain_core.messages import AIMessage
from langchain_core.runnables import RunnableLambda
from pydantic import ValidationError
from support_eval.agent import Prediction, build_agent
from support_eval.config import Settings
from support_eval.dataset import CATEGORIES


@pytest.mark.parametrize('category', CATEGORIES)
def test_agent_accepts_five_categories(category):
    assert Prediction(category=category, explanation='A concise reason').category == category


def test_agent_rejects_invalid_category():
    with pytest.raises(ValidationError):
        Prediction(category='unknown', explanation='Reason')


def test_reference_labels_never_enter_messages():
    seen = []
    def respond(messages):
        seen.extend(messages)
        return {'parsed': Prediction(category='account_help', explanation='Login problem'),
                'raw': AIMessage(content='', usage_metadata={'input_tokens': 12, 'output_tokens': 6, 'total_tokens': 18}),
                'parsing_error': None}
    graph = build_agent(Settings(), 'Classify the ticket.', structured_model=RunnableLambda(respond))
    result = graph.invoke({'ticket_text': 'Cannot log in', 'expected_category': 'SECRET_LABEL'})
    assert result['prediction']['category'] == 'account_help'
    assert result['usage']['input_tokens'] == 12
    assert all('SECRET_LABEL' not in m.content for m in seen)


def test_provider_failure_is_not_other():
    def fail(_):
        raise TimeoutError('timed out')
    graph = build_agent(Settings(), 'Classify.', structured_model=RunnableLambda(fail))
    with pytest.raises(TimeoutError):
        graph.invoke({'ticket_text': 'Hi'})


def test_parse_failure_retains_usage():
    raw = AIMessage(content='bad', usage_metadata={'input_tokens': 10, 'output_tokens': 1, 'total_tokens': 11})
    graph = build_agent(Settings(), 'Classify.', structured_model=RunnableLambda(
        lambda _: {'parsed': None, 'raw': raw, 'parsing_error': ValueError('bad output')}))
    result = graph.invoke({'ticket_text': 'Hi'})
    assert result['prediction'] is None
    assert result['usage']['output_tokens'] == 1
    assert result['error'] == 'Invalid structured response'


def test_settings_do_not_serialize_keys():
    settings = Settings(fireworks_api_key='private-fireworks', langsmith_api_key='private-langsmith')
    assert 'private-' not in repr(settings)
    assert 'private-' not in settings.model_dump_json()


def test_invalid_workspace_id_rejected_locally():
    with pytest.raises(ValidationError, match='workspace'):
        Settings(workspace_id='workspace display name')
