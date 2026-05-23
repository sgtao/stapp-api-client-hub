# InputSupporter.py
import time
import io

# import os
import urllib.parse

import streamlit as st

# import streamlit.components.v1 as stc
from streamlit_paste_button import paste_image_button as pbutton

from ui.SpeechTranscriptor import SpeechTranscriptor

from logic.ProcessImage import ProcessImage

# from ui.ChatMessage import ChatMessage


class InputSupporter:
    def __init__(self) -> None:
        if "api_running" not in st.session_state:
            st.session_state.api_running = False
        if "pasted_image" not in st.session_state:
            st.session_state.pasted_image = None
        if "image_data" not in st.session_state:
            st.session_state.image_data = None
        if "image_base64" not in st.session_state:
            st.session_state.image_base64 = None

    def get_input_data(self):
        return st.session_state.image_data

    def set_api_running(self):
        st.session_state.api_running = True

    def clear_states(self):
        st.session_state.api_running = False
        st.session_state.pasted_image = None
        st.session_state.image_data = None
        st.session_state.image_base64 = None

    def get_supporter_state(self) -> dict:
        """ChatBot処理で使う入力データをまとめて返す"""
        has_image = st.session_state.image_data is not None
        image_base64 = st.session_state.image_base64

        # URIエンコードされている場合はデコード
        if image_base64 is not None:
            image_base64 = urllib.parse.unquote(image_base64)

        return {
            "has_image": has_image,
            "image_data": st.session_state.image_data,
            "image_base64": image_base64,
        }

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
            # process_image.resize_image(target_height=240)
            # process_image.resize_image(target_height=160)
            process_image.resize_image()

        # session_stateから表示（再描画時にも対応）
        resized_image = process_image.get_resized_image()
        if resized_image is not None:
            st.success("画像を縮小しました。")
            st.image(resized_image)
            # st.write(f"Base64(head 50 char.): {str_base64[:50]}...")
            str_base64 = process_image.convert_to_base64(resized_image)
            st.code(str_base64)

        cols = st.columns(3)
        with cols[0]:
            if resized_image is not None:
                if st.button("確定して閉じる", type="primary"):
                    st.session_state.image_data = resized_image
                    st.session_state.image_base64 = (
                        process_image.convert_to_base64(resized_image)
                    )
                    st.rerun()
        with cols[1]:
            pass
        with cols[2]:
            self._modal_closer()

    def render_buttons(self):
        st.write("###### Input Options:")
        cols = st.columns(10)
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

        # remain cols
        for _col in cols[2:]:
            with _col:
                pass
