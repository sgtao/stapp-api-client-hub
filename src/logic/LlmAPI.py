# LlmAPI.py
import json

from logic.ApiRequestor import ApiRequestor
from logic.ResponseOperator import ResponseOperator

# APP_TITLE = "APIクライアントアプリ"
APP_TITLE = "LlmAPI"


class LlmAPI:
    def __init__(
        self,
        uri: str = "https://api.groq.com/openai/v1/chat/completions",
        model_name: str = "llama-3.3-70b-versatile",
        header_dict: dict = None,
        req_body: dict = None,
        user_property_path: str = "choices[0].message.content",
    ):
        self.model_name = model_name
        self.url = uri
        self.header_dict = header_dict or {}
        self.req_body = req_body or {}
        self.api_requestor = ApiRequestor()
        self.user_property_path = user_property_path
        self.response_op = ResponseOperator()

    def prepare_dynamic_request(self, session_state):
        """URIとリクエストボディの動的変数置換を行う"""
        self.url = self.api_requestor.replace_uri(session_state, self.url)
        _req_body = self.api_requestor.replace_body(
            session_state, self.req_body
        )
        # print(f"req_body: {_req_body}")
        self.req_body = json.loads(_req_body)

    def response(self, messages=[]):
        headers = self.header_dict.copy()
        payload = self.req_body
        # st.write(f"payload: {payload}")
        if "messages" not in payload:
            payload["messages"] = messages
        else:
            _messages = payload.get("messages")
            if type(_messages) is list:
                for message in messages:
                    _messages.append(message)
            else:
                _messages = messages

            payload["messages"] = _messages

        response = self.api_requestor.send_request(
            # self.api_url, headers=headers, json=payload, stream=True
            url=self.url,
            method="POST",
            headers=headers,
            # json=payload,
            body=payload,
        )
        response.raise_for_status()
        return response

    def single_response(self, messages=[]):
        try:
            response = self.response(messages)
            # return response.json()["choices"][0]["message"]["content"]
            response_json = response.json()
            return self.response_op.extract_property_from_json(
                response_json,
                self.user_property_path,
            )
        # except requests.exceptions.RequestException as e:
        except Exception as e:
            # st.error(f"APIリクエストに失敗しました: {e}")
            # time.sleep(3)
            # st.rerun()
            raise f"APIリクエストに失敗しました: {e}"
