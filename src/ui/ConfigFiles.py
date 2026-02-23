# ConfigFiles.py
import glob
import os
import re
import yaml

import streamlit as st

ASSETS_DIR = "assets"
PRIVATES_DIR = "privates"


class ConfigFiles:
    def __init__(self, config_mode="default"):
        self.config_mode = config_mode
        self.config_files = self._load_config_files()
        # session state
        if "config_loaded" not in st.session_state:
            st.session_state.config_loaded = False

    def _build_dirs(self):
        if self.config_mode == "default":
            return [
                ASSETS_DIR,
                PRIVATES_DIR,
            ]
        return [
            os.path.join(ASSETS_DIR, self.config_mode),
            os.path.join(PRIVATES_DIR, self.config_mode),
        ]

    def _load_config_files(self):
        files = []
        for base_dir in self._build_dirs():
            if not os.path.isdir(base_dir):
                continue
            files.extend(
                sorted(
                    glob.glob(os.path.join(base_dir, "*.yaml")),
                    key=self.natural_keys,
                )
            )
        return files

    # def __init__(self) -> None:
    #     self.config_file = []
    #     # assetsフォルダからyamlファイルを選択
    #     self.config_files = sorted(
    #         glob.glob(os.path.join(ASSETS_DIR, "*.yaml")),
    #         key=self.natural_keys,
    #     )
    #     private_configs = sorted(
    #         glob.glob(os.path.join(APPEND_DIR, "*.yaml")),
    #         key=self.natural_keys,
    #     )
    #     for private_config in private_configs:
    #         self.config_files.append(private_config)

    # atoi and natural_keys is for Sort files loaded with glob.glob.
    # reference : https://teshi-learn.com/2021-04/python-glob-glob-sorted/
    # Convert text to integer if it is a digit, otherwise return the text
    def atoi(self, text):
        return int(text) if text.isdigit() else text

    #
    # Split text into natural keys, handling both digits and non-digit parts
    def natural_keys(self, text):
        return [self.atoi(c) for c in re.split(r"(\d+)", text)]

    def get_config_files_list(self):
        return self.config_files

    def load_config_from_yaml(self, config_path):
        with open(config_path, "r", encoding="utf-8") as f:
            return yaml.safe_load(f)

    # copied from def config_mode_selector
    def _on_change_config_mode(self):
        st.session_state.config_loaded = False

    def render_config_mode(
        self, mode_options=["default", "single", "actions", "test"]
    ):
        """
        assets/privatesフォルダのサブフォルダをを選択
        """
        config_mode = st.radio(
            "Which config file mode(other than default are subfolder)",
            options=mode_options,
            index=0,
            horizontal=True,
            on_change=self._on_change_config_mode,
        )
        self.config_mode = config_mode
        self.config_files = self._load_config_files()
        return self.config_mode

    def _on_change_config_selector(self):
        st.session_state.config_loaded = False

    def render_config_selector(self):
        return st.selectbox(
            label="Select a config file",
            options=self.config_files,
            on_change=self._on_change_config_selector,
        )

    def render_config_viewer(self, config_path, config):
        if "title" in config:
            st.info(f"{config.get('title')}")
        if "note" in config:
            st.warning(f"{config.get('note')}")
        # st.write("##### Config states")
        with st.expander(
            label="##### Config states",
            expanded=False,
            icon="📝",
        ):
            st.code(config_path)
            st.write(config)
