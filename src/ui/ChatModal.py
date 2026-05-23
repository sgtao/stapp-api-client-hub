# ChatModal.py
from datetime import datetime
import yaml
import time
import streamlit as st


class ChatModal:
    def __init__(self):
        if "messages" not in st.session_state:
            st.session_state.messages = []
        if "system_prompt" not in st.session_state:
            st.session_state.system_prompt = ""
        if "text_message" not in st.session_state:
            st.session_state.text_message = ""
        if "summary_chat" not in st.session_state:
            st.session_state.summary_chat = ""

    # @st.dialog("Chat Modal.", width="large")
    @st.dialog("Chat Modal.", width="medium")
    def modal(self, type, messages=[], summary=""):
        st.write(f"Modal for {type}:")
        if type == "copy_response":
            if len(messages) > 0:
                # self.copy_action(message=messages[-1])
                self.copy_messages(messages, summary=summary)
            else:
                st.warning("Message not found!")
            self._modal_closer()
        elif type == "clear_session":
            self.confirm_clear_session()
        elif type == "clear_messages":
            self.confirm_clear_messages()
        elif type == "save_chat":
            self.save_chat_history(messages, summary=summary)
            self._modal_closer()
        elif type == "load_chat":
            self.load_chat_history()
            self._modal_closer()
        else:
            st.write("No Definition.")

    def _modal_closer(self):
        if st.button(label="Close Modal"):
            st.info("モーダルを閉じます...")
            time.sleep(1)
            st.rerun()

    # 『Copy』モーダル：
    def copy_action(self, message):
        with st.expander("Last message", expanded=False):
            with st.container(horizontal_alignment="right"):
                st.write("右上にコピーアイコンがあります👇")
                st.code(message.get("content", ""))

    def copy_messages(self, messages, summary=""):
        last_message = messages[-1]
        with st.expander("Last message", expanded=False):
            with st.container(horizontal_alignment="right"):
                st.write("右上にコピーアイコンがあります👇")
                st.code(last_message.get("content", ""))

        if summary:
            with st.expander("Chat Summary", expanded=False):
                with st.container(horizontal_alignment="right"):
                    st.code(summary)

        st.write("---")
        st.write("chat history (展開すると右上にコピーアイコンがあります👇)")
        for message in messages:
            _message_role = message.get("role", "")
            if _message_role == "system":
                continue
            elif _message_role == "user":
                _label = "question from user"
            else:
                _label = "response"
            with st.expander(label=_label, expanded=False):
                with st.container(horizontal_alignment="right"):
                    st.code(message.get("content", ""))

    # 『Clear』モーダル：
    def confirm_clear_session(self):
        st.subheader("Clear Session?")
        st.code(
            "チャットを初期化します（systemprompt含め削除）。よろしいですか？"
        )
        col_l, col_r = st.columns(2)
        with col_l:
            self._modal_closer()
        with col_r:
            if st.button("Clear", type="primary"):
                # 全てのセッション状態をクリアする
                st.session_state.clear()
                time.sleep(1)
                st.rerun()

    def confirm_clear_messages(self):
        st.subheader("Clear Messages?")
        st.code(
            "チャットを初期化します（systemprompt含め削除）。よろしいですか？"
        )
        col_l, col_r = st.columns(2)
        with col_l:
            self._modal_closer()
        with col_r:
            if st.button("Clear", type="primary"):
                # Messageに関する状態をクリアする
                st.session_state.summary_chat = ""
                st.session_state.system_prompt = ""
                st.session_state.text_message = ""
                st.session_state.messages = []
                time.sleep(1)
                st.rerun()

    # 『Save Chat History』モーダル：
    def save_chat_history(self, messages, summary=""):
        system_prompt = ""
        if "system_prompt" in st.session_state:
            system_prompt = st.session_state.system_prompt

        time_stamp = datetime.now().strftime("%Y%m%d-%H%M%S")
        file_name = f"{time_stamp}_chatHistory.yaml"
        data = {
            "time_stamp": time_stamp,
            "messages": messages,
            "summary_chat": summary,
            "system_prompt": system_prompt,
        }
        chat_yaml = yaml.dump(
            data, allow_unicode=True, default_flow_style=False
        )

        with st.expander("Save Chat History", expanded=True):
            st.code(chat_yaml, height="content", language="yaml")

        st.download_button(
            label="Download Chat History",
            data=chat_yaml,
            file_name=file_name,
            mime="text/yaml",
        )

    # 『Load Chat History』モーダル：
    def load_chat_history(self):
        uploaded_file = st.file_uploader(
            label="Choose a Chat History YAML file",
            type="yaml",
        )
        if uploaded_file is not None:
            try:
                config = yaml.safe_load(uploaded_file)
                if config:
                    loaded_messages = config.get("messages", [])
                    loaded_summary = config.get("summary_chat", "")
                    loaded_prompt = config.get("system_prompt", "")

                    st.write(
                        f"Messages: {len(loaded_messages)} 件, "
                        f"Summary: {'あり' if loaded_summary else 'なし'}"
                    )

                    if st.button("ロードを実行", type="primary"):
                        st.session_state.messages = loaded_messages
                        st.session_state.summary_chat = loaded_summary
                        st.session_state.system_prompt = loaded_prompt
                        st.info("チャット履歴をロードしました")
                        time.sleep(2)
                        st.rerun()
            except yaml.YAMLError as e:
                st.error(f"YAML解析エラー: {str(e)}")
