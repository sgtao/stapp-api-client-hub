# config_mode_selector.py
import streamlit as st


def config_mode_selector(
    mode_options = ["default", "single", "actions", "test"]
):
    """
    assets/privatesフォルダのサブフォルダをを選択
    """
    return st.radio(
        "Which config file mode(other than default are subfolder)",
        options=mode_options,
        index=0,
        horizontal=True,
    )
