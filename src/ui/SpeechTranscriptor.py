# SpeechTranscriptor.py
from datetime import datetime

import streamlit as st

from logic.Transcriptor import Transcriptor


class SpeechTranscriptor:
    """録音UIと音声文字起こしをまとめて管理するクラス。"""

    LANGS = {
        "日本語 (ja-JP)": "ja-JP",
        "English - US (en-US)": "en-US",
        "English - UK (en-GB)": "en-GB",
        "English - India (en-IN)": "en-IN",
        "中文 台灣 (cmn-Hant-TW)": "cmn-Hant-TW",
    }

    def _render_lang_selector(self) -> str:
        label = st.selectbox(
            "Recognized Language", list(self.LANGS.keys()), index=0
        )
        return self.LANGS[label]

    def _render_audio_input(self) -> bytes | None:
        audio_file = st.audio_input(
            "Record (開始->発話->停止をすると、文字起こしします。)"
        )
        if audio_file is None:
            return None
        st.audio(audio_file)
        return audio_file.read()

    def render_transcriptor(self, display=True) -> str | None:
        """言語セレクタ・録音ウィジェットを表示し、文字起こし結果を返す。

        Returns:
            文字起こしテキスト。録音前は None。

        Raises:
            sr.UnknownValueError: 音声を認識できなかった場合
            sr.RequestError: 音声認識サービスへの接続エラーの場合
        """
        lang = self._render_lang_selector()
        audio_bytes = self._render_audio_input()
        if audio_bytes is None:
            return None
        # with st.spinner("文字起こし中..."):
        with st.spinner("Transcripting..."):
            transcriptor = Transcriptor(lang)
            datetime_str = datetime.now().strftime("%y%m%d_%H:%M:%S")
            try:
                text = transcriptor.transcribe(audio_bytes)
                if text:
                    if display:
                        st.subheader("Transcript:")
                        st.text_area(
                            label=f"DateTime: {datetime_str}",
                            value=text,
                            height=200,
                        )
                    return text
            except Exception as e:
                st.warning(f"{datetime_str}: {e}")

        return None
