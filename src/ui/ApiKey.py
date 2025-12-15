# ApiKey.py
import os
import streamlit as st


class ApiKey:
    def __init__(self):
        if "api_key" not in st.session_state:
            st.session_state.api_key = ""

        self.api_key = ""

        # API-KEYのプリセット確認
        if self.has_key():
            self.api_key = st.session_state.api_key
        elif os.getenv("API_KEY"):
            st.session_state.api_key = os.getenv("API_KEY")
            self.api_key = st.session_state.api_key
        else:
            self.api_key = ""

    def input_key(self):
        # API-KEY入力部品
        st.session_state.api_key = st.text_input(
            "API Key",
            type="password",
            placeholder="i.e.) gsk_...",
            value=self.api_key,
        )
        # return self.api_key

    def has_key(self):
        return st.session_state.get("api_key", "") != ""

    def get_key(self):
        return st.session_state.get("api_key", "")

    def set_key(self, api_key):
        st.session_state.api_key = api_key
        self.api_key = api_key
