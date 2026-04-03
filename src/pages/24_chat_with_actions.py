import tempfile
import time

import io

# import os

import streamlit as st
from streamlit_paste_button import paste_image_button as pbutton

from ui.ChatMessage import ChatMessage
from ui.ChatModal import ChatModal
from ui.SideMenus import SideMenus
from ui.SpeechTranscriptor import SpeechTranscriptor

from logic.AppLogger import AppLogger
from logic.ChatService import ChatService
from logic.ProcessImage import ProcessImage

# from ui.ChatMessage import ChatMessage

# APP_TITLE = "Action Config チャットアプリ"
APP_TITLE = "Chatbot with Action Config"


class InputController:
    def __init__(self) -> None:
        if "api_running" not in st.session_state:
            st.session_state.api_running = False
        if "pasted_image" not in st.session_state:
            st.session_state.pasted_image = None
        if "image_data" not in st.session_state:
            st.session_state.image_data = None
        if "image_base64" not in st.session_state:
            st.session_state.image_base64 = None

    @st.dialog("Setting Info.")
    def modal(self, type):
        st.subheader(f"Modal for {type}:")
        if type == "audio":
            self.render_audio_input()
        elif type == "image":
            self.render_image_paste()
        else:
            st.write("No Definition.")
            self._modal_closer()

    def _modal_closer(self):
        if st.button(label="Close Modal"):
            st.info("モーダルを閉じます...")
            time.sleep(1)
            st.rerun()

    def _clear_states(self):
        st.session_state.api_running = False

    def render_audio_input(self):
        st.markdown("Google API 使用。**外務インターネットへ接続します。**")
        speech_transcriptor = SpeechTranscriptor()
        transcript = speech_transcriptor.render_transcriptor(display=False)
        if transcript:
            st.code(transcript)
        col_l, col_r = st.columns(2)
        with col_l:
            if transcript:
                if st.button("Append to prompt", type="primary"):
                    # 現在の入力を取得（未入力なら空文字）
                    raw_msg = st.session_state.get("text_message", "")
                    previous_msg = (
                        raw_msg if raw_msg is not None else ""
                    ).strip()
                    # 整形処理：各行の無駄な空白を削除
                    clean_transcript = "\n".join(
                        [
                            line.strip()
                            for line in transcript.strip().split("\n")
                        ]
                    )

                    # 追記するフォーマットを作成
                    # f-string内のインデントが反映されないよう左寄せにするのがコツです
                    append_text = f"\n---\n{clean_transcript}\n"

                    # セッション状態を更新
                    st.session_state.text_message = previous_msg + append_text

                    st.info("コピーしました。モーダルを閉じます...")
                    time.sleep(1)
                    st.rerun()
        with col_r:
            self._modal_closer()

    def render_image_paste(self):
        process_image = ProcessImage()
        st.markdown(
            "画像を貼り付けると、サイズ変更してBase64コードへ変換します。"
        )
        paste_result = pbutton(
            label="📋 Paste Image data",
            text_color="#ffffff",
            background_color="#3498db",
            hover_background_color="#2980b9",
            key="paste_button",
        )

        if paste_result.image_data is not None:
            img_byte_arr = io.BytesIO()
            paste_result.image_data.save(img_byte_arr, format="PNG")
            process_image.set_image_data(img_byte_arr.getvalue())
            resized_image = process_image.resize_image()
            st.session_state.image_data = resized_image

        # session_stateから表示（再描画時にも対応）
        if st.session_state.image_data is not None:
            st.success("画像が保存されました")
            st.image(st.session_state.image_data)
            st.session_state.image_base64 = process_image.convert_to_base64(
                st.session_state.image_data
            )
            st.code(
                st.session_state.image_base64[:100] + "..."
            )  # 先頭だけ表示

        col_l, col_r = st.columns(2)
        with col_l:
            if (
                st.session_state.image_data is not None
            ):  # pasted_image → image_data
                if st.button("確定して閉じる", type="primary"):
                    st.rerun()
        with col_r:
            self._modal_closer()

    def render_buttons(self):
        st.write("###### Input Options:")
        cols = st.columns(8)
        with cols[0]:
            if st.button(
                help="Audio Input",
                label="🎤",
                disabled=st.session_state.api_running,
            ):
                self.modal("audio")
        with cols[1]:
            if st.button(
                help="Image Paste",
                label="🖼",
                disabled=st.session_state.api_running,
            ):
                self.modal("image")
        with cols[2]:
            pass
        with cols[3]:
            pass
        with cols[4]:
            pass
        with cols[5]:
            pass
        with cols[6]:
            pass
        with cols[7]:
            pass


def initial_session_state():
    # セッション状態の初期化
    if "results" not in st.session_state:
        st.session_state.results = []
    if "text_message" not in st.session_state:
        st.session_state.text_message = None
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
        """会話履歴を要約を使ってチャットします。\n
    - `assets/actions/102_chat_with_response_summary.yaml`を利用します\n
    - 事前に3000 port で `single` config のAPI-Serverを起動して下さい
    """
    )
    # 1. セッション状態の初期化 [14-16]
    input_controller = InputController()
    # chat_manager = ChatMessage()
    chat_service = ChatService()
    message = ChatMessage()
    # Setup to access API-Server
    config_file_path = "assets/actions/102_chat_with_response_summary.yaml"
    action_configs = chat_service.read_action_config(config_file_path)

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

    # 3. ユーザー入力の受付
    input_controller.render_buttons()
    prompt = st.text_area(
        label="User Message",
        placeholder="Please input message , and press `submit`",
        value=st.session_state.text_message,
    )
    if prompt is not None:
        st.session_state.text_message = prompt

    # 音声入力切り替えのためコメントアウト：SpeechTranscriptor利用のため
    # if prompt and prompt.audio:
    #     st.audio(prompt.audio)
    #     # audio_file_path = save_audio_data(prompt.audio)
    #     # st.code(audio_file_path)
    #     # prompt.audio.getvalue() は bytes 型なのでそのまま渡せる
    #     audio_bytes = prompt.audio.getvalue()

    #     # API呼び出し
    #     result_text = chat_service.transcribe_audio_data(audio_bytes)
    #     st.write("Transcribed text:")
    #     st.code(result_text)

    # if prompt and prompt.text:
    if st.button("submit", icon="🏃"):
        if prompt == "":
            st.warning("Please input message, before submit")
            time.sleep(3)
            return

        # st.write(prompt)
        st.session_state.messages.append(
            # {"role": "user", "content": prompt.text}
            {"role": "user", "content": prompt}
        )
        with st.chat_message("user"):
            # st.markdown(prompt.text)
            st.markdown(prompt)

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
            # messages.append({"role": "user", "content": prompt.text})
            messages.append({"role": "user", "content": prompt})
            st.session_state.text_message = None

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
        st.session_state.text_message = None
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


if __name__ == "__main__":
    initial_session_state()
    app_logger = AppLogger(APP_TITLE)
    app_logger.app_start()
    side_menus = SideMenus()
    side_menus.set_user_property_path("results")
    side_menus.render_api_client_menu()
    main()
