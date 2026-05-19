# config_mode_selector.py
import streamlit as st


def config_mode_selector(
    # for packaged app, default to 'single' mode
    mode_options=["single", "actions", "test", "default"]
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
