# ApiRequestInputs.py
import json
import yaml
# import re

import streamlit as st

METHODS = ["GET", "POST", "PUT", "DELETE"]


class ApiRequestInputs:
    def __init__(self, method=None, api_origin=None, uri=None, body=None):
        # Method, URI, RequestBodyの初期化
        if "method" not in st.session_state:
            # st.session_state.method = "GET"
            if method is not None:
                st.session_state.method = method
            else:
                st.session_state.method = METHODS[0]
        if "api_origin" not in st.session_state:
            if api_origin is not None:
                st.session_state.api_origin = api_origin
            else:
                st.session_state.api_origin = "http://localhost:3000"
        if "uri" not in st.session_state:
            if uri is not None:
                st.session_state.uri = uri
            else:
                st.session_state.uri = self.make_uri("/api/v0/hello")
        if "req_body" not in st.session_state:
            st.session_state.req_body = "{}"
            if body is not None:
                st.session_state.req_body = body
            else:
                st.session_state.req_body = "{}"
        if "use_dynamic_inputs" not in st.session_state:
            # st.session_state.use_dynamic_inputs = False
            st.session_state.use_dynamic_inputs = True

    def _update_method(self):
        st.session_state.method = st.session_state._method_selector

    def _update_uri(self):
        st.session_state.uri = st.session_state._uri_input

    def _update_req_body(self):
        st.session_state.req_body = st.session_state._body_input
        # st.rerun()

    def _update_use_dynamic_inputs(self):
        st.session_state.use_dynamic_inputs = (
            st.session_state._use_dynamic_checkbox
        )

    def get_method(self):
        return st.session_state.method

    def get_api_origin(self):
        return st.session_state.api_origin

    def get_uri(self):
        return st.session_state.uri

    def make_uri(self, path, origin=None):
        if "api_origin" in st.session_state:
            return st.session_state.api_origin + path
        else:
            if origin is not None:
                return path
            else:
                return origin + path

    def get_req_body(self):
        return st.session_state.req_body

    def get_use_dynamic_inputs(self):
        return st.session_state.use_dynamic_inputs

    def render_method_selector(self):
        return st.selectbox(
            label="HTTPメソッド",
            options=METHODS,
            index=METHODS.index(st.session_state.method),
            key="_method_selector",
            on_change=self._update_method,
        )

    def render_uri_input(self):
        return st.text_input(
            label="URI",
            key="_uri_input",
            value=st.session_state.uri,
            on_change=self._update_uri,
        )

    def _parse_to_dict(self, data_str):
        # 1. JSON のチェック
        try:
            data = json.loads(data_str)
            return data, "JSON"
        except (json.JSONDecodeError, TypeError, ValueError):
            pass

        # 2. YAML のチェック
        try:
            data = yaml.safe_load(data_str)
            # 構造体（辞書/リスト）であり、かつTOONとして判定されなかった場合
            if isinstance(data, (dict, list)):
                return data, "YAML"
        except yaml.YAMLError:
            pass

        # 3. 他の形式の場合
        return None, "Unknown"

    def render_req_body(self, req_body):
        body_dict, body_type = self._parse_to_dict(req_body)
        st.write(f"Body format: {body_type}")
        st.json(body_dict)
        return json.dumps(body_dict, ensure_ascii=False, indent=4)

    def render_body_input(self):
        ext_url_json = "https://tools.m-bsys.com/dev_tools/json-beautifier.php"
        ext_url_yaml = "https://www.site24x7.com/ja/tools/json-to-yaml.html"
        label_str = (
            f"ツール：JSON形式整形 ([JSONきれい]({ext_url_json})）"
            f" / YAML形式へ変換（[YAML変換]({ext_url_yaml})）"
        )
        # リクエストボディ入力（POST, PUTの場合のみ表示）
        if st.session_state.method in ["POST", "PUT"]:
            with st.expander("リクエストボディ設定（JSON/YAML形式で入力して下さい)"):
                _req_body = st.text_area(
                    label=label_str,
                    key="_body_input",
                    value=st.session_state.req_body,
                    on_change=self._update_req_body,
                    height=200,
                )
                body_dict = self.render_req_body(_req_body)
                return body_dict
        else:
            return None

    def render_use_dynamic_checkbox(self):
        return st.checkbox(
            label="動的な入力を利用する",
            key="_use_dynamic_checkbox",
            value=st.session_state.use_dynamic_inputs,
            on_change=self._update_use_dynamic_inputs,
        )
