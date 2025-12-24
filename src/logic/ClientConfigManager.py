# ClientConfigManager.py
import urllib


class ClientConfigManager:
    """アクション設定（YAML）とプレースホルダ置換を管理"""

    def replace_placeholder(self, session_state, target_str, results=[]):
        """
        プレースホルダー（例: ＜user_input_0＞）を
        session_state 内のユーザー入力値で置換する。

        Args:
            session_state (dict): Streamlitのセッション状態
            target_str (str): プレースホルダーを含む文字列
            results(list): 実行途中の結果

        Returns:
            str: プレースホルダーが置換された文字列
        """
        replaced_str = target_str

        # replace target using user_input
        num_inputs = session_state.get("num_inputs", 0)
        for i in range(num_inputs):
            key = f"user_input_{i}"
            if key in session_state:
                value = urllib.parse.quote(str(session_state[key]))
                replaced_str = replaced_str.replace(f"＜{key}＞", value)

        # replace target using results
        # _results = session_state.get("results", [])
        # _results = results
        num_results = len(results)
        for i in range(num_results):
            key = f"action_result_{i}"
            value = str(results[i])
            # _value = urllib.parse.quote(str(results[i]))
            # value = _value.replace('"', " ").replace("'", " ")
            replaced_str = replaced_str.replace(f"＜{key}＞", value)

        return replaced_str

    def replace_action_config(self, session_state, action_config, results=[]):
        """
        指定されたアクション設定（action_config）を置換する。

        Args:
            session_state (dict): `st.session_state`
            action_config (dict): YAML設定ファイルなどから読み込まれた
            results (list): 実行途中の結果
        Side Effects:
            - `action_state`の値の特定キーワードを置換する
            - 置換対象：
                - config_file
                - user_input_{i}
            - 対象外：
                - method, uri, num_inputs
                - use_dynamic_inputs, user_property_path
        """
        _replaced_config = {}
        if "method" in action_config:
            _replaced_config["method"] = action_config.get("method", "")
        if "uri" in action_config:
            _replaced_config["uri"] = action_config.get("uri", "")
        if "config_file" in action_config:
            # _replaced_config["config_file"] = action_config.get(
            #     "config_file", ""
            # )
            _replaced_config["config_file"] = self.replace_placeholder(
                session_state=session_state,
                target_str=action_config.get("config_file", ""),
                results=results,
            )

        # replace request body (user_input key)
        _num_inputs = action_config.get("num_inputs", 0)
        _replaced_config["num_inputs"] = _num_inputs
        for i in range(_num_inputs):
            key = f"user_input_{i}"
            if key in action_config:
                # _replaced_config[key] = action_config.get(key, "")
                _replaced_config[key] = self.replace_placeholder(
                    session_state=session_state,
                    target_str=action_config.get(key, ""),
                    results=results,
                )

        if "use_dynamic_inputs" in action_config:
            if action_config.get("use_dynamic_inputs") == "false":
                _replaced_config["use_dynamic_inputs"] = False
            else:
                _replaced_config["use_dynamic_inputs"] = True
        if "user_property_path" in action_config:
            _replaced_config["user_property_path"] = action_config.get(
                "user_property_path", "."
            )

        return _replaced_config

    def replace_extract_config(self, session_state, action_config, results=[]):
        _replaced_config = action_config

        # for action of `extract` type
        if "target" in action_config:
            _replaced_config["target"] = self.replace_placeholder(
                session_state=session_state,
                target_str=action_config.get("target", ""),
                results=results,
            )

        return _replaced_config
