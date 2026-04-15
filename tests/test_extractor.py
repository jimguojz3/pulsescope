import os
from unittest.mock import patch, MagicMock
import pytest

from pulsescope.extraction.extractor import extract_events, ExtractionError


@patch.dict(os.environ, {"OPENAI_API_KEY": "dummy"})
def test_extract_events_returns_structured_events():
    mock_completion = MagicMock()
    mock_completion.choices = [
        MagicMock(
            message=MagicMock(
                content='[{"事件": "伊朗封锁霍尔木兹海峡", "类型": "地缘政治", "影响领域": "航运"}]'
            )
        )
    ]

    with patch("pulsescope.extraction.extractor.OpenAI") as MockOpenAI:
        instance = MockOpenAI.return_value
        instance.chat.completions.create.return_value = mock_completion
        events = extract_events(["Iran has closed the Strait of Hormuz."])

    assert len(events) == 1
    assert events[0]["事件"] == "伊朗封锁霍尔木兹海峡"
    assert "类型" in events[0]
    assert "影响领域" in events[0]


@patch.dict(os.environ, {"OPENAI_API_KEY": "dummy"})
def test_extract_events_strips_markdown_fences():
    mock_completion = MagicMock()
    mock_completion.choices = [
        MagicMock(
            message=MagicMock(
                content='Here is the JSON:\n```json\n[{"事件": "A", "类型": "自然灾害", "影响领域": "能源"}]\n```'
            )
        )
    ]

    with patch("pulsescope.extraction.extractor.OpenAI") as MockOpenAI:
        instance = MockOpenAI.return_value
        instance.chat.completions.create.return_value = mock_completion
        events = extract_events(["Earthquake in region."])

    assert len(events) == 1
    assert events[0]["事件"] == "A"


@patch.dict(os.environ, {"OPENAI_API_KEY": "dummy"})
def test_extract_events_raises_on_invalid_json():
    mock_completion = MagicMock()
    mock_completion.choices = [MagicMock(message=MagicMock(content='not json'))]

    with patch("pulsescope.extraction.extractor.OpenAI") as MockOpenAI:
        instance = MockOpenAI.return_value
        instance.chat.completions.create.return_value = mock_completion
        with pytest.raises(ExtractionError):
            extract_events(["Some text."])


@patch.dict(os.environ, {"OPENAI_API_KEY": "dummy"})
def test_extract_events_raises_on_non_list_json():
    mock_completion = MagicMock()
    mock_completion.choices = [MagicMock(message=MagicMock(content='{"事件": "X"}'))]

    with patch("pulsescope.extraction.extractor.OpenAI") as MockOpenAI:
        instance = MockOpenAI.return_value
        instance.chat.completions.create.return_value = mock_completion
        with pytest.raises(ExtractionError):
            extract_events(["Some text."])


@patch.dict(os.environ, {}, clear=True)
def test_extract_events_raises_when_api_key_missing():
    with pytest.raises(RuntimeError, match="OPENAI_API_KEY not set"):
        extract_events(["Any text."])


@patch.dict(os.environ, {"OPENAI_API_KEY": "dummy"})
def test_extract_events_returns_empty_list_for_empty_input():
    mock_completion = MagicMock()
    mock_completion.choices = [MagicMock(message=MagicMock(content="[]"))]

    with patch("pulsescope.extraction.extractor.OpenAI") as MockOpenAI:
        instance = MockOpenAI.return_value
        instance.chat.completions.create.return_value = mock_completion
        events = extract_events([])

    assert events == []
