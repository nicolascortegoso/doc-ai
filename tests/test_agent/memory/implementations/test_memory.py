from uuid import uuid4

import pytest

from common.models import Message
from agent.memory.implementations.memory import InMemoryMemory


@pytest.fixture
def memory() -> InMemoryMemory:
    return InMemoryMemory()


class TestInMemoryMemoryAdd:
    def test_add_stores_message(self, memory):
        session_id = uuid4()
        message = Message(role="user", content="hello")
        memory.add(message, session_id)
        result = memory.get(session_id)
        assert len(result) == 1
        assert result[0].content == "hello"

    def test_add_multiple_messages_in_order(self, memory):
        session_id = uuid4()
        memory.add(Message(role="user", content="first"), session_id)
        memory.add(Message(role="assistant", content="second"), session_id)
        result = memory.get(session_id)
        assert result[0].content == "first"
        assert result[1].content == "second"


class TestInMemoryMemoryGet:
    def test_get_returns_empty_list_for_unknown_session(self, memory):
        assert memory.get(uuid4()) == []

    def test_get_returns_correct_messages(self, memory):
        session_id = uuid4()
        memory.add(Message(role="user", content="hello"), session_id)
        result = memory.get(session_id)
        assert result[0].role == "user"
        assert result[0].content == "hello"

    def test_get_returns_copy_not_reference(self, memory):
        session_id = uuid4()
        memory.add(Message(role="user", content="hello"), session_id)
        result = memory.get(session_id)
        result.append(Message(role="user", content="injected"))
        assert len(memory.get(session_id)) == 1


class TestInMemoryMemoryClear:
    def test_clear_removes_messages(self, memory):
        session_id = uuid4()
        memory.add(Message(role="user", content="hello"), session_id)
        memory.clear(session_id)
        assert memory.get(session_id) == []

    def test_clear_is_noop_for_unknown_session(self, memory):
        memory.clear(uuid4())

    def test_clear_does_not_affect_other_sessions(self, memory):
        session_a = uuid4()
        session_b = uuid4()
        memory.add(Message(role="user", content="a"), session_a)
        memory.add(Message(role="user", content="b"), session_b)
        memory.clear(session_a)
        assert len(memory.get(session_b)) == 1


class TestInMemoryMemoryIsolation:
    def test_sessions_are_isolated(self, memory):
        session_a = uuid4()
        session_b = uuid4()
        memory.add(Message(role="user", content="session a"), session_a)
        memory.add(Message(role="user", content="session b"), session_b)
        assert memory.get(session_a)[0].content == "session a"
        assert memory.get(session_b)[0].content == "session b"