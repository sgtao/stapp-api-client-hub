import time

# import os

import streamlit as st

from ui.ChatMessage import ChatMessage
from ui.ChatModal import ChatModal
from ui.InputSupporter import InputSupporter
from ui.SideMenus import SideMenus

from logic.AppLogger import AppLogger
from logic.ChatService import ChatService

# from ui.ChatMessage import ChatMessage

# APP_TITLE = "Action Config チャットアプリ"
APP_TITLE = "Chatbot with Action Config"

CONFIG_WO_IMAGE = "assets/actions/200_chat_with_response_summary.yaml"
CONFIG_WITH_IMAGE = "assets/actions/210_chat_with_image_explation.yaml"


def initial_session_state():
    # セッション状態の初期化
    if "results" not in st.session_state:
        st.session_state.results = []
    if "system_prompt" not in st.session_state:
        st.session_state.system_prompt = ""
    if "text_message" not in st.session_state:
        st.session_state.text_message = ""
    if "summary_chat" not in st.session_state:
        st.session_state.summary_chat = ""


def main():
    st.page_link("main.py", label="Back to Home", icon="🏠")

    st.header(f"💬+🏃 {APP_TITLE}")
    st.info(
        """会話履歴を要約を使ってチャットします。\n
    - `assets/actions/102_chat_with_response_summary.yaml`を利用します\n
    - 画像添付すると`assets/actions/112_chat_with_image_explation.yaml`を利用します\n
    - 事前に3000 port で `single` config のAPI-Serverを起動して下さい
    - サイドメニューの`user_input`は無視されます
    """
    )
    # 1. セッション状態の初期化 [14-16]
    input_supporter = InputSupporter()
    # chat_manager = ChatMessage()
    chat_service = ChatService()
    message = ChatMessage()
    # Setup to access API-Server
    config_file_path = CONFIG_WO_IMAGE
    action_configs = chat_service.read_action_config(config_file_path)
    system_prompt = ""
    prompt = ""

    # Chat with Config
    with st.container(height="stretch"):
        # 2. チャット履歴の表示
        # for msg in st.session_state.messages:
        #     with st.chat_message(msg["role"]):
        #         st.markdown(msg["content"])
        message.display_chat_history()

        # 会話履歴
        with st.expander("Summary of Chat."):
            if st.session_state.summary_chat != "":
                st.write(st.session_state.summary_chat)
            else:
                st.info("ここにチャットの要約を記します。")

    # 2. システムプロンプトの入力
    with st.expander("System Prompt:", expanded=False):
        system_prompt = st.text_area(
            label="System Prompt (Max. 8,000 chars.)",
            placeholder="Input System Prompt (Optional)",
            value=st.session_state.system_prompt,
            height="content",
            max_chars=8000,
        )

    # 3. ユーザー入力の受付
    input_supporter.render_buttons()
    supporter_state = input_supporter.get_supporter_state()
    if supporter_state.get("has_image", False):
        st.image(supporter_state.get("image_data", None))

    with st.form(key="prompt_form", clear_on_submit=True):
        prompt = st.text_area(
            label="User Message (Max. 4,000 chars.)",
            placeholder="Please input message , and press `submit`",
            value=st.session_state.text_message,
            max_chars=4000,
        )

        # if st.button("submit", icon="🏃"):
        submit_button = st.form_submit_button(label="submit", icon="🏃")

    if submit_button:
        if prompt == "":
            st.warning("Please input message, before submit")
            time.sleep(3)
            return

        # st.write(prompt)
        with st.chat_message("user"):
            # st.markdown(prompt.text)
            st.markdown(prompt)
        user_message = {"role": "user", "content": prompt}
        st.session_state.messages.append(user_message)

        # 4. アクションAPIの実行 (YAMLの指示に従って連鎖実行) [2, 19]
        input_supporter.set_api_running()
        with st.spinner("思考中..."):
            messages = []
            assistant_content = st.session_state.summary_chat
            # if len(messages) > 0:
            #     assistant_content += messages[-1].content
            if assistant_content != "":
                messages.append(
                    {"role": "assistant", "content": assistant_content}
                )

            messages.append(user_message)
            # st.session_state.text_message = None

            user_input_state = {}
            # num_user_inputs = st.session_state.get("num_user_inputs", 0)
            # user_input_state["num_inputs"] = num_user_inputs
            # for i in range(num_user_inputs):
            #     user_input_state[f"user_input_{i}"] = st.session_state.get(
            #         f"user_input_{i}", ""
            #     )
            supporter_state = input_supporter.get_supporter_state()
            if supporter_state.get("has_image", False):
                config_file_path = CONFIG_WITH_IMAGE
                action_configs = chat_service.read_action_config(
                    config_file_path
                )
                user_input_state["num_inputs"] = 2
                user_input_state["user_input_0"] = system_prompt
                user_input_state["user_input_1"] = supporter_state.get(
                    "image_base64", ""
                )
            else:
                user_input_state["num_inputs"] = 1
                user_input_state["user_input_0"] = system_prompt

            # user_inputs にユーザーの入力を渡す
            results = chat_service.post_messages_with_configs(
                messages=messages,
                session_state=user_input_state,
                action_configs=action_configs,
            )

            # 最終ステップの結果を回答として取得
            st.session_state.results = results
            # answer = results[0].get("result")
            answer = results[-2]
            st.session_state.summary_chat = results[-1]

        # 5. 回答の表示と保存
        with st.chat_message("assistant"):
            st.markdown(answer)
        st.session_state.messages.append(
            {"role": "assistant", "content": answer}
        )
        st.session_state.system_prompt = system_prompt
        st.session_state.text_message = ""
        input_supporter.clear_states()
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
                type="copy_response",
                messages=message.get_messages(),
                summary=st.session_state.summary_chat,
            )

    with cols[1]:
        if st.button(
            help="Clear Messages",
            label="🆑",
        ):
            ChatModal().modal(type="clear_messages")
    with cols[2]:
        pass
    with cols[3]:
        pass
    with cols[4]:
        pass


if __name__ == "__main__":
    initial_session_state()
    app_logger = AppLogger(APP_TITLE)
    app_logger.app_start()
    side_menus = SideMenus()
    side_menus.set_user_property_path("results")
    side_menus.render_api_client_menu()
    main()
