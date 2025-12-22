# ApiClient.py
# import json
import streamlit as st

from logic.ApiRequestor import ApiRequestor


class ApiClient:
    def __init__(self):
        # セッション状態の初期化
        if "api_response" not in st.session_state:
            # st.session_state.api_response = None
            self.clr_api_response()
        if "action_resps" not in st.session_state:
            st.session_state.action_resps = []
        if "num_resps" not in st.session_state:
            st.session_state.num_resps = len(st.session_state.action_resps)

    def post_api_server(self, uri, config_file="", messages=[]):
        """
        APIサーバーへconfig_fileのPOSTリクエストを発行します
        - 内部は、ApiRequestor.send_api_request を呼び出すラッパー
        """
        st.session_state.api_response = None
        num_inputs = st.session_state.get("num_inputs", 0)
        user_inputs = {}

        for i in range(num_inputs):
            user_key = f"user_input_{i}"
            if user_key in st.session_state:
                user_inputs[user_key] = st.session_state[user_key]
            else:
                self.show_warning_ui(
                    f"Session state key '{user_key}' not found."
                )

        try:
            api_requestor = ApiRequestor()
            response = api_requestor.send_api_request(
                uri=uri,
                method="POST",
                config_file=config_file,
                num_inputs=num_inputs,
                user_inputs=user_inputs,
                messages=messages,
            )
            # if success, set parameters to session_state for save YAML
            self.show_success_ui(
                "Successfully connected to API Server.",
                uri=uri,
                response=response,
            )

            return response
        except Exception as e:
            raise e

    def show_warning_ui(self, message):
        """ユーザー入力キーが欠けている場合の警告"""
        st.warning(message)

    def show_success_ui(self, message, uri="", response=None):
        """成功時のUI表示とセッション更新"""
        if uri != "":
            st.session_state.uri = uri
            st.session_state.method = "POST"
        if response is not None:
            self.save_api_response(response)
        st.success(message)

    def post_msg_with_action_config(self, action_config, messages=[]):
        """
        APIサーバーへ`action_config`のPOSTリクエストを発行します
        - 内部は、ApiRequestor.send_api_request を呼び出すラッパー
        """
        # st.session_state.api_response = None
        # print(f"action_config: {action_config}")
        uri = action_config.get("uri", "")
        num_inputs = action_config.get("num_inputs", 0)
        config_file = action_config.get("config_file", "")
        user_inputs = {}

        for i in range(num_inputs):
            user_key = f"user_input_{i}"
            if user_key in action_config:
                user_inputs[user_key] = action_config.get(user_key, "")
            else:
                self.show_warning_ui(
                    f"Session state key '{user_key}' not found."
                )

        try:
            api_requestor = ApiRequestor()
            response = api_requestor.send_api_request(
                uri=uri,
                method="POST",
                config_file=config_file,
                num_inputs=num_inputs,
                user_inputs=user_inputs,
                messages=messages,
            )
            # if success, set parameters to session_state for save YAML
            self.show_success_ui(
                "Successfully connected to API Server.",
                uri=uri,
                response=response,
            )
            return response
        except Exception as e:
            raise e

    def get_api_response(self):
        return st.session_state.api_response

    def get_num_resps(self):
        return st.session_state.num_resps

    # def get_action_resps(self):
    #     return st.session_state.action_resps

    def get_action_response(self, index):
        return st.session_state.action_resps[index]

    def save_api_response(self, response):
        prev_num_resps = len(st.session_state.action_resps)
        st.session_state.api_response = response
        st.session_state.action_resps.append(response.json())
        st.session_state.num_resps = prev_num_resps + 1

    def clr_api_response(self):
        st.session_state.api_response = None

    def render_action_resps(self):
        with st.popover(
            label="Open previous response",
            width="stretch",
            disabled=(self.get_num_resps() <= 0),
        ):
            for i in range(self.get_num_resps()):
                with st.expander(f"Action: {i}:", expanded=False):
                    st.write(self.get_action_response(i))
