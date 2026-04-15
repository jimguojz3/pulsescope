import os
from unittest.mock import patch, MagicMock

from pulsescope.extraction.extractor import extract_events


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
