# serviced_api_client.py
# import json
import streamlit as st

from ui.ApiClient import ApiClient
from ui.ApiRequestInputs import ApiRequestInputs
from ui.ConfigApiSelector import ConfigApiSelector
from ui.ResponseViewer import ResponseViewer
from ui.SideMenus import SideMenus

# from functions.ApiRequestor import ApiRequestor
from logic.AppLogger import AppLogger

# APP_TITLE = "APIクライアントアプリ"
APP_TITLE = "Serviced Api Client"


def initial_session_state():
    # セッション状態の初期化
    if "config_file" not in st.session_state:
        st.session_state.config_file = ""


def main():
    st.page_link("main.py", label="Back to Home", icon="🏠")

    st.title(f"🧪 {APP_TITLE}")
    # インスタンス化
    request_inputs = ApiRequestInputs(api_origin="http://localhost:3000")
    response_viewer = ResponseViewer()
    # api_requestor = ApiRequestor()
    config_api_selector = ConfigApiSelector()
    api_client = ApiClient()

    try:
        # Setup to access API-Server
        config_file = config_api_selector.render_selector()

        if config_file == "":
            st.warning("Please check to access API Server!")
            return
        else:
            # Render selected config tilte and note
            config_api_selector.render_config_title(config_file)

            if st.button("Set Config", type="primary"):
                st.session_state.config_file = config_file
                api_client.clr_api_response()

            # Render previous responses
            api_client.render_action_resps()

        # リクエスト送信ボタン
        if st.session_state.config_file != "":
            st.write(f"used config file: {st.session_state.config_file}")
            api_response = api_client.get_api_response()
            messages = []
            user_message = st.text_input(
                label="User Message",
                placeholder="Please input message , when request message",
            )
            col1, col2, col3 = st.columns(3)
            try:
                with col1:
                    if st.button("Rerun (`R`)", icon="🔃"):
                        st.rerun()
                with col2:
                    if st.button(
                        "Request service", type="secondary", icon="🚀"
                    ):
                        # APIリクエスト送信
                        uri = request_inputs.make_uri(path="/api/v0/service")
                        api_response = api_client.post_api_server(
                            uri=uri,
                            config_file=st.session_state.config_file,
                        )
                with col3:
                    if st.button(
                        "Request message", type="secondary", icon="🎟️"
                    ):
                        # APIリクエスト送信
                        if user_message != "":
                            messages.append(
                                {"role": "user", "content": user_message}
                            )
                        uri = request_inputs.make_uri(path="/api/v0/messages")
                        api_response = api_client.post_api_server(
                            uri=uri,
                            config_file=st.session_state.config_file,
                            messages=messages,
                        )

            except Exception as e:
                # ユーザー向けメッセージ
                st.error(
                    "リクエスト中にエラー発生。詳細は以下をご確認ください。"
                )
                # 詳細な例外情報を表示
                st.exception(e)

            # レスポンス表示
            if api_response:
                st.subheader("API レスポンス")
                response_viewer.render_viewer(api_response)

    except Exception as e:
        st.error(f"Error occured! {e}")


if __name__ == "__main__":
    initial_session_state()
    app_logger = AppLogger(APP_TITLE)
    app_logger.app_start()
    side_menus = SideMenus()
    side_menus.render_api_client_menu()
    main()
