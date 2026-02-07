# 13_chat_with_config.py
import time

import streamlit as st

from ui.ApiRequestHeader import ApiRequestHeader
from ui.ApiRequestInputs import ApiRequestInputs
from ui.ChatMessage import ChatMessage
from ui.ChatModal import ChatModal
from ui.ClientController import ClientController
from ui.ConfigFiles import ConfigFiles
from ui.SideMenus import SideMenus
from ui.utils.config_mode_selector import config_mode_selector

from logic.AppLogger import AppLogger
from logic.ConfigProcess import ConfigProcess
from logic.LlmAPI import LlmAPI

# APP_TITLE = "APIクライアントアプリ"
APP_TITLE = "Chat with Config"


def initialize_session_state():
    if "config_loaded" not in st.session_state:
        st.session_state.config_loaded = False


# モーダルの定義
@st.dialog("Show Configed Request.")
def modal_request_viewer(request_header, request_inputs):
    def _modal_closer():
        if st.button(label="Close Modal"):
            st.info("モーダルを閉じます...")
            time.sleep(1)
            st.rerun()

    st.write("Configurated Request inputs:")
    # ユーザー入力：APIリクエストの指定項目
    request_inputs.render_method_selector()
    request_inputs.render_use_dynamic_checkbox()
    request_inputs.render_uri_input()

    # ヘッダー入力セクション
    with st.expander("リクエストヘッダー設定"):
        request_header.render_editor()

    # リクエストボディ入力（POST, PUTの場合のみ表示）
    request_inputs.render_body_input()

    # Close button for modal
    _modal_closer()


# def main():
def main():
    st.page_link("main.py", label="Back to Home", icon="🏠")

    st.title(f"💬 {APP_TITLE}")
    # インスタンス化
    client_controller = ClientController()
    request_header = ApiRequestHeader()
    api_request_inputs = ApiRequestInputs()

    message = ChatMessage()
    config_process = ConfigProcess()

    # assets/privatesフォルダからyamlファイルを選択
    config_mode = config_mode_selector(
        mode_options=["default", "single", "test"]
    )
    config_files = ConfigFiles(config_mode=config_mode)

    if not config_files:
        st.warning(
            "No YAML config files in assets and private. Please add some."
        )
        return

    selected_config_file = config_files.render_config_selector()

    # 選択されたコンフィグファイルを読み込む
    if selected_config_file:
        config = config_files.load_config_from_yaml(selected_config_file)
        config_files.render_config_viewer(selected_config_file, config)

    # Load Config and show Request settings
    col1, col2, col3 = st.columns(3)
    with col1:
        if st.button("Load Config File", icon="📤"):
            # 読み込んだコンフィグをセッションステートに適用
            client_controller.set_session_state(config)
            config_process.set_config(config)
            req_body_dict = config_process.get_request_body()
            if "messages" in req_body_dict:
                # st.write(req_body_dict["messages"])
                message.set_messages(req_body_dict["messages"])

            st.session_state.config_loaded = True
            st.rerun()
    with col2:
        if st.button("Show Config. Request", icon="ℹ️"):
            # response = test_post_service(port)
            modal_request_viewer(
                request_header=request_header,
                request_inputs=api_request_inputs,
            )
    with col3:
        if st.button("Clear Session States", icon="🔄"):
            # 全てのセッション状態をクリアする場合はこちらを使用
            st.session_state.clear()
            st.rerun()
    # with col4:
    #     pass
    # with col5:
    #     pass

    # Chat with Config
    with st.container(height="stretch"):
        message.display_chat_history()

        user_input = st.chat_input(
            placeholder="After load config, Submit any message",
            disabled=not st.session_state.config_loaded,
            max_chars=8000,
        )
        if user_input:
            # get response from LlmAPI
            if api_request_inputs.get_method() == "GET":
                st.warning(
                    "GETメソッドは、リクエストボディを送信しません。"
                    "リクエストヘッダーとURIのみが使用されます。"
                )
                time.sleep(3)
                st.rerun()

            message.add("user", user_input)
            uri = api_request_inputs.get_uri()
            header_dict = request_header.get_header_dict()
            request_body = api_request_inputs.get_req_body()
            # URIとリクエストボディのJSON形式検証

            try:
                user_property_path = st.session_state.user_property_path
                llm = LlmAPI(
                    # uri=sent_uri,
                    uri=uri,
                    header_dict=header_dict,
                    # req_body=req_body,
                    req_body=request_body,
                    # user_property_path=st.session_state.user_property_path,
                    user_property_path=user_property_path,
                )

                # replace llm request
                if st.session_state.use_dynamic_inputs:
                    llm.prepare_dynamic_request(st.session_state)

                # send message:
                response = llm.single_response(message.get_messages())

                message.add("assistant", response)

            except Exception as e:
                st.error(f"APIリクエストに失敗しました: {e}")
                time.sleep(3)

            finally:
                st.rerun()

    # page footer
    cols = st.columns(5)
    with cols[0]:
        if st.button(
            label="",
            help="Copy Response",
            icon="📋",
        ):
            ChatModal().modal(
                type="copy_response", messages=message.get_messages()
            )

    with cols[1]:
        pass
    with cols[2]:
        pass
    with cols[3]:
        pass
    with cols[4]:
        pass


# render page
if __name__ == "__main__":
    initialize_session_state()
    app_logger = AppLogger(APP_TITLE)
    app_logger.app_start()
    side_menus = SideMenus()
    side_menus.render_api_client_menu()
    main()
