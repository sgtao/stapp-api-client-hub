# ConfigProcess.py
import json


class ConfigProcess:
    def __init__(self, config=None):
        self.config = {}
        self.session_state = {}
        if config is not None:
            # config must be a dictionary
            self.set_config(config)
        if "session_state" in self.config:
            self.session_state = self.get_config("session_state")

    def get_config(self, key=None):
        if key:
            return self.config.get(key, None)
        else:
            return self.config.copy()

    def get_from_session_sts(self, key=None):
        if key:
            if key in self.session_state:
                return self.session_state[key]
            else:
                return None
        else:
            return self.session_state.copy()

    def get_request_body(self):
        """return request body as dict. object
        Returns:
            dict: req_body_dict
        """
        req_body_dict = {}  # 初期化
        if self.has_session_sts("req_body"):
            req_body_data = self.get_from_session_sts("req_body")

            # req_body_dataの型をチェック
            if isinstance(req_body_data, str):
                try:
                    # 文字列であれば、json.loads()で辞書に変換
                    req_body_dict = json.loads(req_body_data)
                except json.JSONDecodeError:
                    # JSONとして不正な形式だった場合のエラー処理
                    raise (
                        "設定ファイル内の 'req_body' は有効なJSON形式の文字列ではありません。"
                    )
                    # req_body_dict = {}
            elif isinstance(req_body_data, dict):
                # もともと辞書であれば、そのまま使用
                req_body_dict = req_body_data
            else:
                # 想定外の型だった場合の警告
                # raise (f"'req_body' が予期せぬ型です: {type(req_body_data)}")
                req_body_dict = {}

        return req_body_dict

    def has_session_sts(self, key=None):
        if "session_state" not in self.config:
            return False
        else:
            if key:
                return key in self.session_state
            else:
                return bool(self.session_state)

    def set_config(self, config):
        self.config = config
        self.session_state = self.get_config("session_state")
