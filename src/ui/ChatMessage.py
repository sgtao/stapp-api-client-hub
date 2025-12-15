# ChatMessage.py
# from pathlib import Path

import streamlit as st

# APP_TITLE = "APIクライアントアプリ"
APP_TITLE = "ChatMessage"


class ChatMessage:
    system_prompt: str = (
        """あなたは聡明なAIです。ユーザの入力に全て日本語で返答を生成してください"""
    )

    def __init__(self, system_prompt: str = system_prompt):
        if "messages" not in st.session_state:
            self.reset()

    def reset(self):
        st.session_state.messages = [
            {
                "role": "system",
                "content": self.system_prompt,
            },
        ]

    def add(self, role: str, content: str):
        st.session_state.messages.append({"role": role, "content": content})
        with st.chat_message(role):
            st.markdown(content)

    def set_messages(self, messages):
        st.session_state.messages = []
        for message in messages:
            st.session_state.messages.append(
                {
                    "role": message["role"],
                    "content": message["content"],
                }
            )

    def get_messages(self):
        response = []
        for message in st.session_state.messages:
            response.append(
                {
                    "role": message["role"],
                    "content": message["content"],
                }
            )
        # return st.session_state.messages
        return response

    def display_chat_history(self):
        for message in st.session_state.messages:
            if message["role"] == "system":
                continue
            with st.chat_message(message["role"]):
                st.markdown(message["content"])
