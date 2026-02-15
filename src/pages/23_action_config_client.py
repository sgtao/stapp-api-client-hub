# action_config_client.py
# import json
import streamlit as st

from ui.ApiClient import ApiClient
from ui.ConfigFiles import ConfigFiles

# from ui.ResponseViewer import ResponseViewer
from ui.SideMenus import SideMenus
from ui.utils.config_mode_selector import config_mode_selector

# from functions.ApiRequestor import ApiRequestor
from logic.AppLogger import AppLogger
from logic.ChatService import ChatService
from logic.utils.read_yaml_file import read_yaml_file

# APP_TITLE = "APIクライアントアプリ"
APP_TITLE = "Action Config Client"


def initial_session_state():
    # セッション状態の初期化
    if "config_file" not in st.session_state:
        st.session_state.config_file = ""


def main():
    st.page_link("main.py", label="Back to Home", icon="🏠")

    st.title(f"🙏 {APP_TITLE}")
    # インスタンス化
    chat_service = ChatService()
    # response_viewer = ResponseViewer()
    # api_requestor = ApiRequestor()
    api_client = ApiClient()
    # assets/privatesフォルダからyamlファイルを選択
    config_mode = config_mode_selector(mode_options=["actions"])
    config_files = ConfigFiles(config_mode=config_mode)

    if not config_files:
        st.warning(
            "No YAML config files in assets and private. Please add some."
        )
        return

    try:
        # Setup to access API-Server
        config_file_path = config_files.render_config_selector()
        if config_file_path == "":
            st.warning("Please check to access API Server!")
            return
        else:
            config_data = read_yaml_file(config_file_path)
            config_title = config_data.get("title", None)
            config_note = config_data.get("note", None)
            if config_title:
                st.write(f"##### Title: {config_title}")
            if config_note:
                st.info(f"Note: {config_title}")

            cols = st.columns(4)
            with cols[0]:
                if st.button("Set Config", type="primary"):
                    st.session_state.config_file = config_file_path
                    api_client.clr_api_response()
                    st.rerun()
            with cols[1]:
                if st.button("Rerun (`R`)", icon="🔃"):
                    st.rerun()
            with cols[2]:
                pass
            with cols[3]:
                pass

        # リクエスト送信ボタン
        if st.session_state.config_file == config_file_path:
            st.write(f"used config file: {st.session_state.config_file}")
            with st.expander("config file date"):
                st.write(config_data)

            api_response = api_client.get_api_response()
            messages = []
            results = []
            user_message = st.text_area(
                label="User Message",
                placeholder="Please input message , when request message",
            )
            col1, col2, col3 = st.columns(3)
            try:
                with col1:
                    if st.button("Start actions", type="secondary", icon="🏃"):
                        # APIリクエスト作成・送信
                        action_configs = chat_service.read_action_config(
                            config_file_path
                        )
                        if user_message != "":
                            messages.append(
                                {"role": "user", "content": user_message}
                            )
                        user_input_state = {}
                        num_user_inputs = st.session_state.get(
                            "num_user_inputs", 0
                        )
                        user_input_state["num_inputs"] = num_user_inputs
                        for i in range(num_user_inputs):
                            user_input_state[f"user_input_{i}"] = (
                                st.session_state.get(f"user_input_{i}", "")
                            )

                        results = chat_service.post_messages_with_configs(
                            messages=messages,
                            session_state=user_input_state,
                            action_configs=action_configs,
                        )
                        # セッションに保存
                        st.session_state.api_response = api_response
                with col2:
                    pass
                with col3:
                    pass

            except Exception as e:
                # ユーザー向けメッセージ
                st.error(
                    "リクエスト中にエラー発生。詳細は以下をご確認ください。"
                )
                # 詳細な例外情報を表示
                st.exception(e)

            # レスポンス表示
            # st.write(results)
            # 修正ポイント: リストが渡された場合は、最後のアクション結果を対象にする
            target_res = (
                results[-1]
                if isinstance(results, list)
                else results
            )
            # --- レスポンス表示セクション ---
            if target_res:
                st.subheader("Final Result")
                
                # データの抽出（resultsキーがあれば取得、なければ全体）
                # YAMLの設定により results キーの中に実際の回答が入る構造に対応
                display_data = target_res.get("results") if isinstance(target_res, dict) else target_res
                
                if display_data:
                    # st.tabsによる表示モードの切り替え
                    tab1, tab2, tab3 = st.tabs([
                        "📝 View",
                        "📋 Copy Mode",
                        "📁 Results"
                    ])
                    with tab1:
                        # 人間が読みやすい形式。Markdownとして解釈させる
                        st.markdown(display_data)
                    with tab2:
                        # コピー可能なコードブロック形式。言語指定なしで汎用的に。
                        st.code(display_data, language=None)
                    with tab3:
                        # resultsすべてを表示
                        st.json(results, expanded=True)
                else:
                    st.warning("No valid data found in the response results.")

    except Exception as e:
        st.error(f"Error occured! {e}")


if __name__ == "__main__":
    initial_session_state()
    app_logger = AppLogger(APP_TITLE)
    app_logger.app_start()
    side_menus = SideMenus()
    side_menus.set_user_property_path("results")
    side_menus.render_api_client_menu()
    main()
