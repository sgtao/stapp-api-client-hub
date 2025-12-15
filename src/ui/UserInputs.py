# UserInputs.py
import streamlit as st


class UserInputs:
    def __init__(self, user_property_path=None):
        self.user_property_path = ""
        # プリセット確認
        if "user_property_path" in st.session_state:
            self.user_property_path = st.session_state.user_property_path
        else:
            if user_property_path is not None:
                self.user_property_path = user_property_path
                st.session_state.user_property_path = user_property_path
            else:
                self.user_property_path = ""

    def render_property_path(self):
        # レスポンスの抽出プロパティパス指定
        st.session_state.user_property_path = st.text_input(
            label="Response Prop. Path:",
            type="default",
            placeholder="抽出するプロパティパス",
            help="例: tags[0].completion.value or . (全てのプロパティ)",
            value=self.user_property_path,
        )

    def set_user_property_path(self, user_property_path):
        self.user_property_path = user_property_path
        st.session_state.user_property_path = user_property_path

    def render_dynamic_inputs(self):
        st.session_state.num_inputs = st.number_input(
            "Request 入力指定数", min_value=1, max_value=10, value=1, step=1
        )

        # 動的にテキスト入力を生成
        for i in range(st.session_state.num_inputs):
            st.session_state[f"user_input_{i}"] = st.text_input(
                f"user_input_{i} の値", f"user_input_{i}の初期値"
            )
