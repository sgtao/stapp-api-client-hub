# ConfigApiSelector.py
import time

import streamlit as st

from ui.ApiRequestInputs import ApiRequestInputs
from ui.ResponseViewer import ResponseViewer
from logic.ApiRequestor import ApiRequestor


class ConfigApiSelector:
    def __init__(self):
        # セッション状態の初期化
        if "api_origin" not in st.session_state:
            st.session_state.api_origin = "http://localhost:3000"
        if "config_list" not in st.session_state:
            st.session_state.config_list = []

    def _update_api_origin(self):
        """
        _update_api_origin: Callback function of "API Server Origin" input
        """
        st.session_state.api_origin = st.session_state._api_origin_input
        st.session_state.config_list = []
        st.warning("Clear config list")
        # time.sleep(3)
        st.rerun()

    def render_selector(self):
        """
        render Config Selector of config_lists from API Server
        return: config_file
        """
        # インスタンス化
        request_inputs = ApiRequestInputs(api_origin="http://localhost:3000")
        response_viewer = ResponseViewer()
        api_requestor = ApiRequestor()
        _config_file = ""

        # Setup to access API-Server
        st.text_input(
            label="API Server Origin",
            key="_api_origin_input",
            value=st.session_state.api_origin,
            on_change=self._update_api_origin,
        )

        if len(st.session_state.config_list) == 0:
            if st.button("Check Ready to access API-Server", type="primary"):
                try:
                    uri = request_inputs.make_uri(path="/api/v0/hello")
                    response = api_requestor.send_request(
                        url=uri, method="GET"
                    )
                    # response_viewer.render_viewer(response)
                    st.success("Success: Access to API Server")
                except Exception as e:
                    st.error(f"Cannot Access to API Searver: {e}")
                    st.info("Please Run API Server!!")

                try:
                    # Get a list of Config files
                    uri = request_inputs.make_uri(path="/api/v0/configs")
                    response = api_requestor.send_request(
                        url=uri, method="GET"
                    )
                    # st.session_state.config_list = (
                    _config_list = response_viewer.extract_response_value(
                        response=response, path="results"
                    )
                    st.session_state.config_list = _config_list
                    # reloase This Screen
                    time.sleep(3)
                    st.rerun()

                except Exception as e:
                    st.warning(f"Not Found Config list: {e}")
        else:
            _config_file = st.selectbox(
                "Select Config file",
                st.session_state.config_list,
            )

        return _config_file

    def render_config_title(self, config_file=""):
        """
        render Config Title and note
        return: None
        """
        # インスタンス化
        request_inputs = ApiRequestInputs(
            api_origin=st.session_state.api_origin
        )
        response_viewer = ResponseViewer()
        api_requestor = ApiRequestor()

        if config_file == "":
            st.warning("Please check to access API Server!")
            return
        else:
            # Get a list of Config files
            uri = request_inputs.make_uri(path="/api/v0/config-title")
            method = "POST"
            header_dict = {"Content-Type": "application/json"}
            # リクエストボディ入力（POST, PUTの場合のみ表示）
            # request_body = """
            #     {
            #         "config_file": "assets/001_get_simple_api_test.yaml"
            #     }
            # """
            request_body = {"config_file": config_file}
            try:
                response = api_requestor.send_request(
                    uri,
                    method,
                    header_dict,
                    request_body,
                )
                response.raise_for_status()  # HTTPエラーをチェック

                title = response_viewer.extract_response_value(
                    response=response, path="results.title"
                )
                note = response_viewer.extract_response_value(
                    response=response, path="results.note"
                )
                st.info(f"Title: {title}")
                st.warning(f"- Note: {note}")
            except Exception as e:
                st.warning(f"Cannot find Title or Note in config_file: {e}")
