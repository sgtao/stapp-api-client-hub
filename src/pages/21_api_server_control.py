# api_server_control.py
# import json
# import os
import requests
import time

import streamlit as st

# import subprocess
# import signal

from ui.SideMenus import SideMenus
from ui.ResponseViewer import ResponseViewer
from ui.utils.config_mode_selector import config_mode_selector

from logic.ApiRequestor import ApiRequestor
from logic.AppLogger import AppLogger
from logic.ProcessManager import ProcessManager


# ページ設定
st.set_page_config(
    page_title="API Server Control",
    page_icon="⚙️",
)

APP_TITLE = "API Server Control"


def initial_session_state():
    # API サーバーの起動・停止を管理するセッション状態の初期化
    if "api_process" not in st.session_state:
        st.session_state.api_process = None
    if "port_number" not in st.session_state:
        st.session_state.port_number = 3000
    if "response" not in st.session_state:
        st.session_state.response = None
    if "config_files" not in st.session_state:
        st.session_state.config_files = []
    if "selected_config" not in st.session_state:
        st.session_state.selected_config = ""
    if "servers" not in st.session_state:
        st.session_state.servers = {}
    if "api_key" not in st.session_state:
        st.session_state.api_key = ""


def test_api_hello(port):
    """
    APIサーバーへの接続をテストします。
    """
    uri = f"http://localhost:{port}/api/v0/hello"
    method = "GET"
    header_dict = {
        "Content-Type": "application/json",
    }
    try:
        # response = requests.get(uri)
        api_requestor = ApiRequestor()
        response = api_requestor.send_request(
            uri,
            method,
            header_dict,
        )
        response.raise_for_status()  # HTTPエラーをチェック
        st.success(
            f"""
            Successfully connected to API Server on port {port}.
            """
        )
        return response
    except requests.exceptions.RequestException as e:
        st.error(f"Failed to connect to API Server: {e}")


def test_get_config_files(port):
    """
    APIサーバーへの接続をテストします。
    """
    uri = f"http://localhost:{port}/api/v0/configs"
    method = "GET"
    header_dict = {
        "Content-Type": "application/json",
    }
    try:
        # if st.button("Test Configs(get list)"):
        # response = requests.get(uri)
        api_requestor = ApiRequestor()
        response = api_requestor.send_request(
            uri,
            method,
            header_dict,
        )
        response.raise_for_status()  # HTTPエラーをチェック
        st.success(
            f"""
            Successfully connected to API Server on port {port}.
            """
        )
        # st.write(response.json())
        response_json = response.json()
        st.session_state.config_files = response_json.get("results")
        return response
    except requests.exceptions.RequestException as e:
        st.error(f"Failed to connect to API Server: {e}")


def test_config_title(port, config_file="assets/001_get_simple_api_test.yaml"):
    """
    APIサーバーへの接続をテストします。
    """
    uri = f"http://localhost:{port}/api/v0/config-title"
    method = "POST"
    header_dict = {"Content-Type": "application/json"}
    # リクエストボディ入力（POST, PUTの場合のみ表示）
    # request_body = """
    #     {
    #         "config_file": "assets/001_get_simple_api_test.yaml"
    #     }
    # """
    request_body = {
        "config_file": config_file,
    }
    try:
        # response = requests.get(uri)
        api_requestor = ApiRequestor()
        response = api_requestor.send_request(
            uri,
            method,
            header_dict,
            request_body,
        )
        response.raise_for_status()  # HTTPエラーをチェック
        return response
    except requests.exceptions.RequestException as e:
        # st.error(f"Failed to `POST` to API Server: {e}")
        raise e


# モーダルの定義
@st.dialog("Setting Info.")
def modal_post_service(port, config_files):
    st.write("Modal for POST service:")
    if len(config_files):
        st.info("Select Config file and Click `POST`.")
        config_file = render_config_selector(config_files)
        if st.button(label="POST", icon="🚀"):
            try:
                # POST リクエストを送信
                response = test_post_service(
                    port=port, config_file=config_file
                )
                # if response:
                st.success("POSTに成功しました")
                st.session_state.response = response
                st.info("モーダルを閉じます...")
                time.sleep(3)
                st.rerun()
            except Exception as e:
                st.error(f"Failed to `POST` to API Server: {e}")
    else:
        st.warning("At 1st, Click `Test Configs`.")
    _modal_closer()


def _update_selected_config():
    st.session_state.selected_config = st.session_state._config_selector


def render_config_selector(config_files):
    return st.selectbox(
        label="HTTPメソッド",
        options=config_files,
        index=0,
        key="_config_selector",
        on_change=_update_selected_config,
    )


def _modal_closer():
    if st.button(label="Close Modal"):
        st.info("モーダルを閉じます...")
        time.sleep(1)
        st.rerun()


def test_post_service(port, config_file="assets/001_get_simple_api_test.yaml"):
    """
    APIサーバーへの接続をテストします。
    """
    uri = f"http://localhost:{port}/api/v0/service"
    method = "POST"
    header_dict = {"Content-Type": "application/json"}
    # リクエストボディ入力（POST, PUTの場合のみ表示）
    # request_body = """
    #     {
    #         "config_file": "assets/001_get_simple_api_test.yaml"
    #     }
    # """
    request_body = {
        "config_file": config_file,
        "num_user_inputs": st.session_state.num_inputs,
        "user_inputs": {},
    }
    for i in range(st.session_state.num_inputs):
        user_key = f"user_input_{i}"
        # value = st.session_state[f"user_input_{i}"].replace('"', "'")
        # request_body["user_inputs"].append({{user_key: f"{value}"}})
        if user_key in st.session_state:
            value = st.session_state[user_key]
            request_body["user_inputs"][user_key] = value
        else:
            st.warning(f"Session state key '{user_key}' not found.")
    # body_json = json.loads(request_body)
    # body_json = json.dumps(request_body)
    body_json = request_body

    try:
        # response = requests.get(uri)
        api_requestor = ApiRequestor()
        response = api_requestor.send_request(
            uri,
            method,
            header_dict,
            body_json,
        )
        response.raise_for_status()  # HTTPエラーをチェック
        st.success(
            f"""
            Successfully connected to API Server on port {port}.
            """
        )
        return response
    except requests.exceptions.RequestException as e:
        # st.error(f"Failed to `POST` to API Server: {e}")
        raise e


def main():
    pm = ProcessManager()
    pm.set_servers(st.session_state.servers)
    # UI
    st.page_link("main.py", label="Back to Home", icon="🏠")

    st.title(f"⚙️ {APP_TITLE}")

    # ポート番号の入力
    port = st.number_input(
        "Base Port Number",
        min_value=1024,
        max_value=65535,
        value=st.session_state.port_number,
        step=1,
    )
    config_mode = config_mode_selector()

    # APIサーバーの起動・停止ボタン
    cols = st.columns(3)
    with cols[0]:
        if st.button("Rerun (`R`)", icon="🔃"):
            st.rerun()
    with cols[1]:
        # _use_package = st.toggle("Use packaged api-server", value=False)
        _use_package = st.toggle("Use packaged api-server", value=True)
    with cols[2]:
        if st.button(
            label=f"Run api-server({port})",
            disabled=(st.session_state.api_process is not None),
            type="primary",
            icon="🚀",
        ):
            # start_api_server(port, _use_package)
            pm.start_server(
                port=port,
                use_package=_use_package,
                config_mode=config_mode,
                api_key=st.session_state.api_key,
            )
            st.session_state.servers = pm.get_servers()
            st.rerun()

    # 起動プロセス
    st.divider()
    pm_list_servers = pm.list_servers()
    if len(pm_list_servers) <= 0:
        return

    st.subheader("launched Processes")
    response = None
    for server_id in pm_list_servers:  # pm.list_servers():
        # st.write(pm.get_status(server_id))
        info = pm.get_status(server_id)
        _exp_label = (
            f"{server_id}: port {info['port']}, cfg.={info['config_mode']}"
        )
        with st.expander(
            # label=f"{server_id}: port {info['port']}", key=f"exp_{server_id}"
            label=_exp_label,
            expanded=True,
        ):
            cols = st.columns(4)
            with cols[0]:
                if st.button(
                    label="Test Hello", key=f"hello_{server_id}", icon="🖐"
                ):
                    response = test_api_hello(info["port"])
            with cols[1]:
                if st.button(
                    "Config list",
                    key=f"config_list_{server_id}",
                    icon="🗒️",
                ):
                    response = test_get_config_files(info["port"])
            with cols[2]:
                st.link_button(
                    label="Swag. docs",
                    url=f'http://localhost:{info["port"]}/docs',
                    icon="🫣",
                )
            with cols[3]:
                if st.button(
                    label="Stop Proc.",
                    key=f"stop_{server_id}",
                    icon="🛑",
                ):
                    pm.stop_server(server_id)
                    st.rerun()

    # API接続テストレスポンス
    st.divider()
    # if st.session_state.api_process:
    # instantiation
    response_viewer = ResponseViewer("results")
    try:
        # st.subheader("Test API Server")
        # col1, col2 = st.columns(2)
        # response = None
        # with col1:
        #     if response is None:
        #         response = test_api_hello(port)
        #     if response is None:
        #         response = test_get_config_files(port)
        #     if response is None:
        #         if st.button("Test Service(post config)"):
        #             # response = test_post_service(port)
        #             modal_post_service(
        #                 port=port,
        #                 config_files=st.session_state.config_files,
        #             )
        # with col2:
        #     if st.button("Rerun (`R`)", icon="🏃"):
        #         st.rerun()

        st.subheader("Response:")
        # st.write(response)
        # st.write(st.session_state.response)
        if response is not None:
            response_viewer.render_viewer(response)
            st.session_state.response = response
        elif st.session_state.response is not None:
            response_viewer.render_viewer(st.session_state.response)
        else:
            st.info("You can access to API Server via Test Buttons")

    except Exception as e:
        st.error(f"Failed to connect to API Server: {e}")


if __name__ == "__main__":
    app_logger = AppLogger(APP_TITLE)
    app_logger.app_start()
    initial_session_state()
    side_menus = SideMenus()
    side_menus.set_user_property_path("results")
    side_menus.render_api_client_menu()
    main()
