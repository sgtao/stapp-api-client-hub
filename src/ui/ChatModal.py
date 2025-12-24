# ChatModal.py
# ui/ChatModalUI.py
import time
import streamlit as st


class ChatModal:
    @st.dialog("Chat Modal.", width="large")
    def modal(self, type, messages):
        st.write(f"Modal for {type}:")
        if type == "copy_response":
            if len(messages) > 0:
                # self.copy_action(message=messages[-1])
                self.copy_messages(messages)
            else:
                st.warning("Message not found!")
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

    def copy_messages(self, messages):
        last_message = messages[-1]
        with st.expander("Last message", expanded=False):
            with st.container(horizontal_alignment="right"):
                st.write("右上にコピーアイコンがあります👇")
                st.code(last_message.get("content", ""))

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
