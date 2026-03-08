import streamlit as st

"""
## Welcome to simple-api-client App!

任意のAPIサービスにアクセスする[streamlit](https://streamlit.io/)アプリです。
"""

# サイドバーのページに移動
# st.page_link("pages/example_app.py", label="Go to Example App")
st.page_link(
    "pages/11_simple_api_client.py",
    label="Go to simple_api_client App",
    icon="🧪",
)
st.page_link(
    "pages/12_config_api_client.py",
    label="Go to config_api_client App",
    icon="🚀",
)
st.page_link(
    "pages/13_chat_with_config.py",
    label="Go to ChatBot with config App",
    icon="💬",
)

# API Serverページへのリンク
st.page_link(
    "pages/21_api_server_control.py",
    label="Go to control page of api server",
    icon="⚙️",
)
st.page_link(
    "pages/22_serviced_api_client.py",
    label="Go to Serviced API Client page",
    icon="🙏",
)
st.page_link(
    "pages/23_action_config_client.py",
    label="Go to Serviced Action Config Client page",
    icon="🏃",
)
st.page_link(
    "pages/24_chat_with_actions.py",
    label="Go to Chatbot with Action Config page",
    icon="💬",
)

# ログ表示ページへのリンク
st.page_link("pages/91_logs_viewer.py", label="View Logs", icon="📄")
