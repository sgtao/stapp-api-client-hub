# config_api_client.py
import json

import streamlit as st

from ui.ApiRequestHeader import ApiRequestHeader
from ui.ApiRequestInputs import ApiRequestInputs
from ui.ResponseViewer import ResponseViewer
from ui.ClientController import ClientController
from ui.ConfigFiles import ConfigFiles
from ui.SideMenus import SideMenus

# from ui.utils.config_mode_selector import config_mode_selector
from logic.ApiRequestor import ApiRequestor
from logic.AppLogger import AppLogger

APP_TITLE = "Config Api Client"


def initialize_session_state():
    # if "config_loaded" not in st.session_state:
    #     st.session_state.config_loaded = False
    pass


def main():
    st.page_link("main.py", label="Back to Home", icon="🏠")

    st.title(f"🚀 {APP_TITLE}")
    """
    `assets`と`privates`配下のconfigファイル(YAML)の定義に沿って実行します。
    - `session_state`: APIリクエスト発行。`action_state`: config_fileのリクエストを実行
    """

    # 以下は11_simple_api_client.pyと同様のAPIリクエスト部分
    request_header = ApiRequestHeader()
    request_inputs = ApiRequestInputs()
    response_viewer = ResponseViewer()
    api_requestor = ApiRequestor()
    client_controller = ClientController()

    # assets/privatesフォルダからyamlファイルを選択
    # config_mode = config_mode_selector(
    #     mode_options=["default", "single", "test"]
    # )
    # config_files = ConfigFiles(config_mode=config_mode)
    config_files = ConfigFiles()
    config_files.render_config_mode(mode_options=["default", "single", "test"])

    if not config_files:
        st.warning(
            "No YAML config files in assets and private. Please add some."
        )
        return

    # selected_config_file = st.selectbox("Select a config file", config_files)
    selected_config_file = config_files.render_config_selector()

    # 選択されたコンフィグファイルを読み込む
    if selected_config_file:
        config = config_files.load_config_from_yaml(selected_config_file)
        config_files.render_config_viewer(selected_config_file, config)

    if st.button(label="Load Config File", icon="📤"):
        # 読み込んだコンフィグをセッションステートに適用
        client_controller.set_session_state(config)
        st.session_state.config_loaded = True
        st.rerun()

    if st.session_state.config_loaded:
        # ユーザー入力：APIリクエストの指定項目
        method = request_inputs.render_method_selector()
        request_inputs.render_use_dynamic_checkbox()
        uri = request_inputs.render_uri_input()

        # ヘッダー入力セクション
        header_dict = {}
        with st.expander("リクエストヘッダー設定"):
            request_header.render_editor()
            # ヘッダー情報を辞書形式で取得
            header_dict = request_header.get_header_dict()

        # リクエストボディ入力（POST, PUTの場合のみ表示）
        request_body = request_inputs.render_body_input()

    if st.button(
        "リクエストを送信",
        disabled=not st.session_state.config_loaded,
    ):
        try:
            # URIとリクエストボディのJSON形式検証
            uri = request_inputs.get_uri()
            method = request_inputs.get_method()
            header_dict = request_header.get_header_dict()
            request_body = request_inputs.get_req_body()
            sent_uri = uri
            sent_body = request_body
            if st.session_state.use_dynamic_inputs:
                sent_uri = api_requestor.replace_uri(st.session_state, uri)
                if request_body:
                    sent_body = api_requestor.replace_body(
                        st.session_state, request_body
                    )

            # st.text(sent_body)
            body_json = json.loads(sent_body) if request_body else None

            response = api_requestor.send_request(
                sent_uri, method, header_dict, body_json, timeout=90,
            )

            if response:
                st.subheader("レスポンス")
                response_viewer.render_viewer(response)
        except Exception as e:
            st.error(
                "リクエスト中にエラーが発生しました。詳細は以下をご確認ください。"
            )
            st.exception(e)


if __name__ == "__main__":
    initialize_session_state()
    app_logger = AppLogger(APP_TITLE)
    app_logger.app_start()
    side_menus = SideMenus()
    side_menus.render_api_client_menu()
    main()
