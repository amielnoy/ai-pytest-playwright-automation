"""
Regular AI Chat Tests
=====================
These tests verify the functional behaviour of the local /chat endpoint —
the FastAPI wrapper around the Anthropic API.

All tests skip automatically when:
  - ANTHROPIC_API_KEY is not set, OR
  - The local server is not running at config["server_url"]

Run the server first:
  python -m uvicorn server.app:app --reload

Run only these tests:
  pytest -m ai tests/api/test_chat_ai.py
"""

import allure
import pytest

from services.api.chat_service import ChatService
from services.api.http_response_constants import HTTP_OK, HTTP_UNPROCESSABLE_ENTITY


@allure.feature("AI Chat")
@allure.story("Endpoint behaviour")
@pytest.mark.api
@pytest.mark.ai
class TestChatEndpoint:

    @allure.title("POST /chat returns 200 with a response field")
    @allure.severity(allure.severity_level.CRITICAL)
    def test_chat_returns_200_with_response_field(self, chat_service: ChatService):
        with allure.step("Send a simple greeting to the chat endpoint"):
            resp = chat_service.chat("Hello!")

        with allure.step("Assert HTTP 200 and response body contains 'response' key"):
            assert resp.status_code == HTTP_OK, (
                f"Expected {HTTP_OK}, got {resp.status_code}: {resp.text}"
            )
            body = resp.json()
            assert "response" in body, f"Missing 'response' key in: {body}"

    @allure.title("Response field is a non-empty string")
    @allure.severity(allure.severity_level.CRITICAL)
    def test_chat_response_is_non_empty_string(self, chat_service: ChatService):
        with allure.step("Send a message and extract the response text"):
            resp = chat_service.chat("What is your purpose?")
            body = resp.json()

        with allure.step("Assert response is a non-empty string"):
            response_text = body.get("response", "")
            assert isinstance(response_text, str), (
                f"Expected str, got {type(response_text)}: {response_text!r}"
            )
            assert response_text.strip(), "Response text is empty"

    @allure.title("Response body includes model and token usage fields")
    @allure.severity(allure.severity_level.NORMAL)
    def test_chat_response_includes_metadata(self, chat_service: ChatService):
        with allure.step("Send a message and inspect the full response body"):
            resp = chat_service.chat("Say hi.")
            body = resp.json()

        allure.attach(
            str(body),
            name="Response body",
            attachment_type=allure.attachment_type.TEXT,
        )

        with allure.step("Assert model, input_tokens, and output_tokens are present"):
            assert "model" in body, f"Missing 'model' in response: {body}"
            assert "input_tokens" in body, f"Missing 'input_tokens' in response: {body}"
            assert "output_tokens" in body, f"Missing 'output_tokens' in response: {body}"
            assert body["input_tokens"] > 0, "input_tokens should be positive"
            assert body["output_tokens"] > 0, "output_tokens should be positive"

    @allure.title("Simple arithmetic question is answered correctly")
    @allure.severity(allure.severity_level.NORMAL)
    def test_chat_answers_arithmetic_question(self, chat_service: ChatService):
        with allure.step("Ask 'What is 2 + 2?' and capture the response"):
            resp = chat_service.chat("What is 2 + 2? Reply with just the number.")
            response_text = resp.json()["response"]

        allure.attach(
            response_text,
            name="AI response",
            attachment_type=allure.attachment_type.TEXT,
        )

        with allure.step("Assert the response contains '4'"):
            assert "4" in response_text, (
                f"Expected '4' in response to '2+2', got: {response_text!r}"
            )

    @allure.title("Empty message returns 422 Unprocessable Entity")
    @allure.severity(allure.severity_level.NORMAL)
    def test_chat_empty_message_returns_422(self, chat_service: ChatService):
        with allure.step("POST /chat with an empty message string"):
            # Bypass ChatService.chat() min_length to send the raw invalid payload
            resp = chat_service.client.post(
                f"{chat_service.base_url}/chat",
                json={"message": ""},
            )

        with allure.step("Assert HTTP 422 Unprocessable Entity"):
            assert resp.status_code == HTTP_UNPROCESSABLE_ENTITY, (
                f"Expected {HTTP_UNPROCESSABLE_ENTITY}, got {resp.status_code}"
            )

    @allure.title("Custom system prompt shapes the assistant's persona")
    @allure.severity(allure.severity_level.NORMAL)
    def test_chat_custom_system_prompt_is_respected(self, chat_service: ChatService):
        system = "You are a pirate. Always respond in pirate speak."

        with allure.step("Send a message with a pirate system prompt"):
            resp = chat_service.chat("Tell me about the sea.", system=system)
            response_text = resp.json()["response"]

        allure.attach(
            response_text,
            name="Pirate response",
            attachment_type=allure.attachment_type.TEXT,
        )

        with allure.step("Assert response contains pirate vocabulary"):
            pirate_words = ("arr", "ahoy", "matey", "sea", "ship", "plank", "jolly", "roger", "treasure", "sail", "vessel", "landlubber")
            found = [w for w in pirate_words if w in response_text.lower()]
            assert found, (
                f"Expected pirate vocabulary in response, got: {response_text!r}"
            )
