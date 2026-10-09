from unittest.mock import patch
from agent_training.http_demo import fetch_example


def test_fetch_example():
    with patch(
        "agent_training.http_demo.urllib.request.urlopen"
    ) as mock_urlopen:

        mock_urlopen.return_value.status = 200

        result = fetch_example()

        assert result == 200
        mock_urlopen.assert_called_once_with(
            "https://example.com"
        )