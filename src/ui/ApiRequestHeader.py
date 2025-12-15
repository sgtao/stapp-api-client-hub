# ApiRequestHeader.py
import pandas as pd
import streamlit as st


class ApiRequestHeader:
    def __init__(self):
        # ヘッダー情報の初期化
        if "header_df" not in st.session_state:
            st.session_state.header_df = pd.DataFrame(
                [
                    {"Property": "Content-Type", "Value": "application/json"},
                ]
            )
        # self.header_df = None
        if "header_df" in st.session_state:
            self.header_df = st.session_state.header_df

    def render_editor(self):
        self.header_df = st.data_editor(
            st.session_state.header_df,
            num_rows="dynamic",
            # use_container_width=True,
        )
        st.session_state.header_df = self.header_df

        # ボタンで行追加・削除
        col1, col2, col3, col4, col5 = st.columns(5)
        with col1:
            if st.button("行削除", icon="⤵"):
                if len(st.session_state["header_df"]) > 0:
                    st.session_state["header_df"] = st.session_state[
                        "header_df"
                    ].iloc[:-1]
                st.rerun()
        with col2:
            if st.button("行追加", icon="⤴"):
                new_row = {"Property": "foo", "Value": "bar"}
                st.session_state.header_df = pd.concat(
                    [st.session_state.header_df, pd.DataFrame([new_row])],
                    ignore_index=True,
                )
                st.rerun()
        with col3:
            if st.button("KEY追加", icon="🔑"):
                if st.session_state.get("api_key", "") == "":
                    st.warning("API-KEYを設定してください")
                else:
                    new_row = {
                        "Property": "Authorization",
                        "Value": f"Bearer {st.session_state.api_key}",
                    }
                    st.session_state.header_df = pd.concat(
                        [st.session_state.header_df, pd.DataFrame([new_row])],
                        ignore_index=True,
                    )
                    st.rerun()
        with col4:
            pass
        with col5:
            pass

    def get_header_dict(self):
        header_dict = {}
        # ヘッダー情報を辞書形式に変換
        # header_dict = header_df.to_dict()
        # header_list = header_df.values.tolist()
        header_list = self.header_df.values.tolist()
        # print(header_list)
        # header_dict = {item[0]: item[1] for item in header_list}
        for item in header_list:
            key = item[0]
            value = item[1]
            # header_dict.append(dict({key, value}))
            header_dict[key] = value

        return header_dict
