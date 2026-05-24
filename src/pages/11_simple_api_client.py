# 11_trial_simple_api.py
import json

import streamlit as st

from ui.ApiRequestHeader import ApiRequestHeader
from ui.ApiRequestInputs import ApiRequestInputs
from ui.ClientController import ClientController
from ui.ResponseViewer import ResponseViewer
from ui.SideMenus import SideMenus
from logic.ApiRequestor import ApiRequestor
from logic.AppLogger import AppLogger

# APP_TITLE = "APIクライアントアプリ"
APP_TITLE = "Simple Api Client"


def main():
    st.page_link("main.py", label="Back to Home", icon="🏠")

    st.title(f"🧪 {APP_TITLE}")
    # インスタンス化
    request_header = ApiRequestHeader()
    request_inputs = ApiRequestInputs()
    response_viewer = ResponseViewer()
    api_requestor = ApiRequestor()
    client_controller = ClientController()

    # ユーザー入力：APIリクエストの指定項目
    method = request_inputs.render_method_selector()
    use_dynamic_inputs = request_inputs.render_use_dynamic_checkbox()
    uri = request_inputs.render_uri_input()

    # ヘッダー入力セクション
    header_dict = {}
    with st.expander("リクエストヘッダー設定"):
        request_header.render_editor()
        # ヘッダー情報を辞書形式で取得
        header_dict = request_header.get_header_dict()

    # リクエストボディ入力（POST, PUTの場合のみ表示）
    request_body = request_inputs.render_body_input()

    # リクエスト送信ボタン
    if st.button("リクエストを送信", type="primary"):
        try:
            # 確定情報のセット
            st.session_state.uri = uri
            st.session_state.method = method
            st.session_state.req_body = request_body
            st.session_state.use_dynamic_inputs = use_dynamic_inputs

            # URIとリクエストボディのJSON形式検証
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

            # APIリクエスト送信
            response = api_requestor.send_request(
                sent_uri, method, header_dict, body_json
            )

            # レスポンス表示
            if response:
                st.subheader("レスポンス")
                response_viewer.render_viewer(response)
        except Exception as e:
            # ユーザー向けメッセージ
            st.error(
                "リクエスト中にエラーが発生しました。詳細は以下をご確認ください。"
            )
            # 詳細な例外情報を表示
            st.exception(e)

    st.markdown("###### Tool:")
    cols = st.columns(5)
    with cols[0]:
        if st.button(
            label="Rerun",
            help="Rerun Streamlit (shortcut: `Ctrl+R`)",
            icon="🔃",
        ):
            st.rerun()
    with cols[1]:
        if st.button(
            label="Save",
            help="Save Session State",
            icon="📥",
        ):
            client_controller.modal("save_state")
    with cols[2]:
        # if st.button(
        #     label="Load", help="Load Session State", icon="📤"
        # ):
        #     client_controller.modal("load_state")
        pass
    with cols[3]:
        pass
    with cols[4]:
        pass


if __name__ == "__main__":
    app_logger = AppLogger(APP_TITLE)
    app_logger.app_start()
    side_menus = SideMenus()
    side_menus.render_api_client_menu()
    main()
