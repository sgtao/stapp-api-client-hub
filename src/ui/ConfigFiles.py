# ConfigFiles.py
import glob
import os
import re
import yaml

import streamlit as st

ASSETS_DIR = "assets"
APPEND_DIR = "privates"


class ConfigFiles:
    def __init__(self) -> None:
        self.config_file = []
        # assetsフォルダからyamlファイルを選択
        self.config_files = sorted(
            glob.glob(os.path.join(ASSETS_DIR, "*.yaml")),
            key=self.natural_keys,
        )
        # for private_config in glob.glob(os.path.join(APPEND_DIR, "*.yaml")):
        private_configs = sorted(
            glob.glob(os.path.join(APPEND_DIR, "*.yaml")),
            key=self.natural_keys,
        )
        for private_config in private_configs:
            self.config_files.append(private_config)

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

    def render_config_selector(self):
        return st.selectbox("Select a config file", self.config_files)

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
