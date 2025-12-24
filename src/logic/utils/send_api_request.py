# send_api_request.py
from logic.AppLogger import AppLogger

# from logic.utils.read_yaml_file import read_yaml_file
# from logic.utils.convert_config_to_header import convert_config_to_header
# from logic.ConfigProcess import ConfigProcess
from logic.ApiRequestor import ApiRequestor
from logic.ResponseOperator import ResponseOperator

APP_NAME = "api_server"


async def send_api_request(url, method, headers, req_body, response_path=None):
    """
    APIRequestorを使ってAPIリクエストを送信します。
    :param url: APIのURI
    :param method: HTTPメソッド (GET, POST, PUT, DELETE)
    :param headers: リクエストヘッダー (辞書形式)
    :param req_body: リクエストボディ (辞書形式)
    :return: レスポンスオブジェクト
    """
    api_logger = AppLogger(APP_NAME)
    api_requestor = ApiRequestor()
    response_op = ResponseOperator()
    response = api_requestor.send_request(url, method, headers, req_body)
    api_response_json = response.json()
    result = response_op.extract_property_from_json(
        api_response_json, response_path
    )
    api_logger.info_log(f"Return API response result: {result}")

    return {"results": result}
