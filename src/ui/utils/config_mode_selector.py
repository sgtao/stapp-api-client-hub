# config_mode_selector.py
import streamlit as st


def config_mode_selector():
    """
    assets/privatesフォルダのサブフォルダをを選択
    """
    mode_options = ["default", "single", "actions", "test"]
    return st.radio(
        "Which config file mode(select subfolder)",
        options=mode_options,
        index=0,
        horizontal=True,
    )
