# ChatToolbar.py
import streamlit as st

from ui.ChatModal import ChatModal


class ChatToolbar:
    def __init__(self):
        if "messages" not in st.session_state:
            st.session_state.messages = []
        if "summary_chat" not in st.session_state:
            st.session_state.summary_chat = ""

    def render_footer(self):
        messages = st.session_state.messages.copy()
        summary = st.session_state.get("summary_chat", "")

        st.markdown("###### Chat Tool:")
        cols = st.columns(5)
        with cols[0]:
            if st.button(
                label="Rerun",
                help="Rerun Streamlit immediately (shortcut: `Ctrl+R`)",
                icon="🔃",
            ):
                st.rerun()
        with cols[1]:
            if st.button(
                label="Copy",
                help="Copy Chat Message",
                icon="📋",
            ):
                ChatModal().modal(
                    type="copy_response",
                    messages=messages,
                    summary=summary,
                )
        with cols[2]:
            if st.button(
                label="Save",
                help="Save Chat History",
                icon="📥",
            ):
                ChatModal().modal(
                    type="save_chat",
                    messages=messages,
                    summary=summary,
                )
        with cols[3]:
            if st.button(label="Load", help="Load Chat History", icon="📤"):
                ChatModal().modal(type="load_chat")
        with cols[4]:
            if st.button(
                label="🆑 Clear",
                help="Clear Messages",
            ):
                ChatModal().modal(type="clear_messages")
