import tempfile

# import os
import streamlit as st

from ui.SideMenus import SideMenus

from logic.AppLogger import AppLogger
from logic.ChatService import ChatService

# from ui.ChatMessage import ChatMessage

# APP_TITLE = "Action Config チャットアプリ"
APP_TITLE = "Chatbot with Action Config"


def initial_session_state():
    # セッション状態の初期化
    if "results" not in st.session_state:
        st.session_state.results = []
    if "summary_chat" not in st.session_state:
        st.session_state.summary_chat = ""


def save_audio_data(audio):
    # 音声データがあれば一時ファイルとして保存
    audio_data = audio.getvalue()
    if audio_data:
        # .wav や .mp3 など、元の形式に合わせる場合は suffix を調整してください
        with tempfile.NamedTemporaryFile(
            delete=False, suffix=".wav"
        ) as tmp_file:
            tmp_file.write(audio_data)
            st.session_state.audio_file_path = tmp_file.name  # パスを保存！
            return tmp_file.name
    else:
        return None


def main():
    st.page_link("main.py", label="Back to Home", icon="🏠")

    st.title(f"💬+🏃 {APP_TITLE}")
    st.info(
        """チャットしながら履歴要約を表示します
            - `102_chat_with_response_summary.yaml`を利用
            - 事前に3000 port で `single` config のAPI-Serverを起動して下さい
            """
    )
    # 1. セッション状態の初期化 [14-16]
    if "messages" not in st.session_state:
        st.session_state.messages = []

    # chat_manager = ChatMessage()
    chat_service = ChatService()
    # Setup to access API-Server
    config_file_path = "assets/actions/102_chat_with_response_summary.yaml"
    action_configs = chat_service.read_action_config(config_file_path)

    # 2. チャット履歴の表示
    for msg in st.session_state.messages:
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])

    # 会話履歴
    with st.expander("Summary of Chat."):
        if st.session_state.summary_chat != "":
            st.write(st.session_state.summary_chat)
        else:
            st.info("ここにチャットの要約を記します。")

    # 3. ユーザー入力の受付
    # if prompt := st.chat_input("何か入力してください"):
    prompt = st.chat_input(
        placeholder="何か入力してください",
        accept_audio=True,
    )

    if prompt and prompt.audio:
        st.audio(prompt.audio)
        # audio_file_path = save_audio_data(prompt.audio)
        # st.code(audio_file_path)
        # prompt.audio.getvalue() は bytes 型なのでそのまま渡せる
        audio_bytes = prompt.audio.getvalue()

        # API呼び出し
        result_text = chat_service.transcribe_audio_data(audio_bytes)
        st.write("Transcribed text:")
        st.code(result_text)

    if prompt and prompt.text:
        # st.write(prompt)
        st.session_state.messages.append(
            {"role": "user", "content": prompt.text}
        )
        with st.chat_message("user"):
            st.markdown(prompt.text)

        # 4. アクションAPIの実行 (YAMLの指示に従って連鎖実行) [2, 19]
        with st.spinner("思考中..."):
            messages = []
            assistant_content = st.session_state.summary_chat
            if len(messages) > 0:
                assistant_content += messages[-1].content
            if st.session_state.summary_chat != "":
                messages.append(
                    {"role": "assistant", "content": assistant_content}
                )
            messages.append({"role": "user", "content": prompt.text})

            user_input_state = {}
            num_user_inputs = st.session_state.get("num_user_inputs", 0)
            user_input_state["num_inputs"] = num_user_inputs
            for i in range(num_user_inputs):
                user_input_state[f"user_input_{i}"] = st.session_state.get(
                    f"user_input_{i}", ""
                )

            # user_inputs にユーザーの入力を渡す
            results = chat_service.post_messages_with_configs(
                messages=messages,
                session_state=user_input_state,
                action_configs=action_configs,
            )

            # 最終ステップの結果を回答として取得
            st.session_state.results = results
            # answer = results[0].get("result")
            answer = results[0]
            st.session_state.summary_chat = results[-1]

        # 5. 回答の表示と保存
        with st.chat_message("assistant"):
            st.markdown(answer)
        st.session_state.messages.append(
            {"role": "assistant", "content": answer}
        )
        st.rerun()


if __name__ == "__main__":
    initial_session_state()
    app_logger = AppLogger(APP_TITLE)
    app_logger.app_start()
    side_menus = SideMenus()
    side_menus.set_user_property_path("results")
    side_menus.render_api_client_menu()
    main()
