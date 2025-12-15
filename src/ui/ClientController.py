# ClientController.py
from datetime import datetime
import json
import time
import yaml

import pandas as pd
import streamlit as st


class ClientController:
    def __init__(self) -> None:
        if "api_running" not in st.session_state:
            st.session_state.api_running = False

    @st.dialog("Setting Info.")
    def modal(self, type):
        st.write(f"Modal for {type}:")
        if type == "save_state":
            self.save_session_state()
            self._modal_closer()
        elif type == "load_state":
            self.load_session_state()
            self._modal_closer()
        else:
            st.write("No Definition.")

    def _modal_closer(self):
        if st.button(label="Close Modal"):
            st.info("モーダルを閉じます...")
            time.sleep(1)
            st.rerun()

    # 『保存』モーダル：
    def _header_df_to_dict(self, header_df):
        dict_list = []
        records_list = header_df.to_dict(orient="records")
        for item in records_list:
            if item["Property"] == "Authorization":
                # auth_value = item["Value"].replace(
                #     "Bearer .*", "Bearer ＜API_KEY＞"
                # )
                auth_value = item["Value"].replace(
                    st.session_state.api_key, "＜API_KEY＞"
                )
                # dict_list.append({item["Property"]: auth_value})
                dict_list.append(
                    {"Property": item["Property"], "Value": auth_value}
                )
            else:
                # dict_list.append({item["Property"]: item["Value"]})
                dict_list.append(
                    {"Property": item["Property"], "Value": item["Value"]}
                )

        return dict_list

    def save_session_state(self):
        with st.expander("Save Session State ?", expanded=False):
            pad = "stappApiClientState.yaml"
            time_stamp = datetime.now().strftime("%Y%m%d-%H%M%S")
            file_name_conf = (
                f"{datetime.now().strftime('%Y%m%d-%H%M%S')}_{pad}"
            )
            pad = "stappApiClientMessages.yaml"
            file_name_msgs = (
                f"{datetime.now().strftime('%Y%m%d-%H%M%S')}_{pad}"
            )
            # セッション状態からパラメータを取得
            conf_data = {
                "time_stamp": time_stamp,
                "session_state": {
                    "method": st.session_state.method,
                    "uri": st.session_state.uri,
                    # "header_df": st.session_state.header_df,
                    "header_df": self._header_df_to_dict(
                        st.session_state.header_df
                    ),
                    "req_body": st.session_state.req_body,
                    "use_dynamic_inputs": st.session_state.use_dynamic_inputs,
                    "user_property_path": st.session_state.user_property_path,
                },
            }
            messages = []
            if "messages" in st.session_state:
                if len(st.session_state.messages) > 0:
                    messages = st.session_state.messages.copy()

            # YAMLに変換
            conf_yaml = yaml.dump(
                conf_data, allow_unicode=True, default_flow_style=False
            )
            msgs_yaml = yaml.dump(
                data={"time_stamp": time_stamp, "messages": messages},
                allow_unicode=True,
                default_flow_style=False,
            )

            # ダウンロードボタンを表示
            st.download_button(
                label="Download YAML for config",
                data=conf_yaml,
                file_name=file_name_conf,
                mime="text/yaml",
            )
            if len(messages) > 0:
                st.download_button(
                    label="Download Messages",
                    data=msgs_yaml,
                    file_name=file_name_msgs,
                    mime="text/yaml",
                )

    # 『読込み』モーダル：
    def _on_file_upload(self):
        # st.session_state.config = None
        pass

    def _load_config(self, uploaded_yaml):
        """
        YAMLファイルを読み込み、ユーザー入力を初期化する

        Args:
            uploaded_file: Streamlitのfile_uploaderから受け取るファイルオブジェクト

        Returns:
            Dict[str, Any]: 処理済みの設定データ
        """
        try:
            config = yaml.safe_load(uploaded_yaml, "r", encoding="utf-8")
            # st.session_state.user_inputs = []
            # st.session_state.min_user_inputs =
            # _initialize_user_inputs(config)
            return config
        except yaml.YAMLError as e:
            st.error(f"YAML解析エラー: {str(e)}")
            return {}
        except Exception as e:
            st.error(f"設定ファイルの処理に失敗しました: {str(e)}")
            return {}

    def set_session_state(self, config):
        if "session_state" not in config:
            return

        cfg_session_state = config.get("session_state", {})
        # "method": st.session_state.method,
        # "uri": st.session_state.uri,
        # "header_df": st.session_state.header_df,
        # "req_body": st.session_state.req_body,
        # "use_dynamic_inputs": st.session_state.use_dynamic_inputs,
        # "user_property_path": st.session_state.user_property_path,
        if "method" in cfg_session_state:
            st.session_state.method = cfg_session_state.get("method")
        if "uri" in cfg_session_state:
            st.session_state.uri = cfg_session_state.get("uri")
        # if "header_df" in cfg_session_state:
        #     st.session_state.uri = cfg_session_state.get("header_df")

        if "header_df" in cfg_session_state:
            get_header = cfg_session_state.get("header_df")
            header_list = []
            for header_item in get_header:
                auth_value = header_item["Value"].replace(
                    "＜API_KEY＞", st.session_state.api_key
                )
                header_list.append(
                    {
                        "Property": header_item["Property"],
                        "Value": auth_value,
                    }
                )
            header_df = pd.DataFrame(header_list)
            st.session_state.header_df = header_df

        if "req_body" in cfg_session_state:
            # st.session_state.req_body = _req_body
            _req_body = cfg_session_state.get("req_body")
            # print(f"req_body type: {type(_req_body)}")
            if type(_req_body) is str:
                # 文字列の場合はそのまま使用
                st.session_state.req_body = _req_body
            else:
                # 辞書/リストの場合はJSON形式に変換
                # st.session_state.req_body = yaml.dump(
                #     _req_body, allow_unicode=True, default_flow_style=False
                # )
                st.session_state.req_body = json.dumps(
                    _req_body, ensure_ascii=False, indent=4
                )
        if "use_dynamic_inputs" in cfg_session_state:
            if cfg_session_state.get("use_dynamic_inputs") == "false":
                st.session_state.use_dynamic_inputs = False
            else:
                st.session_state.use_dynamic_inputs = True
        if "user_property_path" in cfg_session_state:
            st.session_state.user_property_path = cfg_session_state.get(
                "user_property_path"
            )

    def load_session_state(self):

        uploaded_file = st.file_uploader(
            label="Choose a YAML config file",
            type="yaml",
            on_change=self._on_file_upload,
        )

        # if uploaded_file is not None and st.session_state.config is None:
        if uploaded_file is not None:
            try:
                config = self._load_config(uploaded_file)
                if config:
                    # st.session_state.config = config
                    self.set_session_state(config)
                    # main_viewer.config_viewer(st.session_state.config)
                    st.rerun()
            except yaml.YAMLError as e:
                st.error(f"Error loading YAML file: {e}")

    def _clear_states(self):
        st.session_state.api_running = False

    def render_buttons(self):
        st.write("##### Runner Ctrl.")
        (
            col1,
            col2,
            col3,
            col4,
            col5,
        ) = st.columns(5)
        with col1:
            if st.button(
                help="Stop Running",
                label="⏹️",
                disabled=(st.session_state.api_running is False),
            ):
                self._clear_states()
                st.rerun()
        with col2:
            if st.button(
                help="Save Session States",
                label="📥",
                disabled=st.session_state.api_running,
            ):
                self.modal("save_state")
        with col3:
            if st.button(
                help="Load Session States",
                label="📤",
                disabled=st.session_state.api_running,
            ):
                self.modal("load_state")
        with col4:
            if st.button(
                help="Clear Session States",
                label="🔄",
            ):
                # 全てのセッション状態をクリアする場合はこちらを使用
                st.session_state.clear()
                st.rerun()
        with col5:
            pass
