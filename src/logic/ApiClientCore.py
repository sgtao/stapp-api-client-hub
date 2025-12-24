# ApiClientCore.py

# from components.ApiClient import ApiClient
from logic.AppLogger import AppLogger
from logic.ApiRequestor import ApiRequestor

APP_TITLE = "ApiClientCore"


class ApiClientCore:
    def __init__(self, logger: AppLogger = None):
        self.logger = logger or AppLogger(APP_TITLE)
        # self.api_client_comp = ApiClient()

    def post_msgs_with_config(self, config, messages=[]):
        """
        APIサーバーへ`config`のPOSTリクエストを発行します
        - 内部は、ApiRequestor.send_api_request を呼び出すラッパー
        """
        # st.session_state.api_response = None
        # print(f"config: {config}")
        uri = config.get("uri", "")
        num_inputs = config.get("num_inputs", 0)
        config_file = config.get("config_file", "")
        user_inputs = {}

        for i in range(num_inputs):
            user_key = f"user_input_{i}"
            if user_key in config:
                user_inputs[user_key] = config.get(user_key, "")
            else:
                raise f"Session state key '{user_key}' not found."

        try:
            api_requestor = ApiRequestor()
            response = api_requestor.send_api_request(
                uri=uri,
                method="POST",
                config_file=config_file,
                num_inputs=num_inputs,
                user_inputs=user_inputs,
                messages=messages,
            )
            self.logger.info_log(f"Request Success of {config_file}.")
            return response
        except Exception as e:
            self.logger.error_log(f"Error occur: {e}")
            raise e
