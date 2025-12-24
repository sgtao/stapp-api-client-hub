# 12_chat_with_config.py
# import time
import streamlit as st

from ui.ChatMessage import ChatMessage
from ui.ChatModal import ChatModal
from ui.ClientController import ClientController
from ui.ConfigFiles import ConfigFiles
from ui.SideMenus import SideMenus

# from functions.ApiRequestor import ApiRequestor
from logic.AppLogger import AppLogger
from logic.ChatService import ChatService

# APP_TITLE = "APIクライアントアプリ"
APP_TITLE = "Chat via API Server"


def initial_session_state():
    # セッション状態の初期化
    if "config_file_path" not in st.session_state:
        st.session_state.config_file_path = ""


def main():
    st.page_link("main.py", label="Back to Home", icon="🏠")

    st.title(f"💬 {APP_TITLE}")
    # インスタンス化
    chat_message = ChatMessage()
    client_controller = ClientController()
    config_files = ConfigFiles()
    chat_service = ChatService()

    # assets/privatesフォルダからyamlファイルを選択
    if not config_files:
        st.warning(
            "No YAML config files in assets and private. Please add some."
        )
        return

    selected_config_file = config_files.render_config_selector()

    # 選択されたコンフィグファイルを読み込む
    if st.button("Load Config."):
        config = config_files.load_config_from_yaml(selected_config_file)
        config_files.render_config_viewer(selected_config_file, config)
        client_controller.set_action_configs(config)
        st.session_state.config_file_path = selected_config_file
        chat_message.reset()

    # Chat with Config
    with st.container(height="stretch"):
        chat_message.display_chat_history()

        # ユーザー入力
        diff_config = st.session_state.config_file_path != selected_config_file
        if prompt := st.chat_input(
            placeholder="メッセージを入力してください:",
            disabled=diff_config,
        ):
            chat_message.add(role="user", content=prompt)

            # アシスタントの応答
            with st.chat_message("assistant"):
                with st.spinner("考え中..."):
                    # assistant_response = post_messages_with_config(
                    #     messages=chat_message.get_messages(),
                    # )
                    results = chat_service.post_messages_with_configs(
                        session_state=st.session_state,
                        messages=chat_message.get_messages(),
                        action_configs=st.session_state.action_configs,
                    )
                    assistant_response = results[-1] if results else None
                    chat_message.add(
                        role="assistant",
                        content=assistant_response,
                    )
                    st.rerun()
    # page footer
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        if st.button(
            label="",
            help="Copy Response",
            icon="📋",
        ):
            ChatModal().modal(
                type="copy_response", messages=chat_message.get_messages()
            )

    with col2:
        pass
    with col3:
        pass
    with col4:
        pass


if __name__ == "__main__":
    initial_session_state()
    app_logger = AppLogger(APP_TITLE)
    app_logger.app_start()
    side_menus = SideMenus()
    side_menus.render_api_client_menu()
    main()
