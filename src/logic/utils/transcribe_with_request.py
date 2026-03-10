# transcribe_with_requests.py
import base64
import io
import requests


def transcribe_with_requests(
    audio_data,
    api_key,
    is_base64=False,
    url="https://api.groq.com/openai/v1/audio/transcriptions",
    model="whisper-large-v3",
    language="ja",
    response_format="json",
):
    """
    Groq APIのWhisperモデルを使用して、音声データをテキストに文字起こしします。

    物理的なファイルを作成せず、メモリ上のバイナリデータ（BytesIO）を
    multipart/form-data形式で送信します。

    Args:
        audio_data (bytes or str): 音声のバイナリデータ、またはBase64エンコードされた文字列。
        api_key (str): Groq APIの認証キー。
        is_base64 (bool, optional): audio_dataがBase64文字列である場合はTrue。デフォルトはFalse。
        url (str, optional): Groqの文字起こしAPIエンドポイント。
        model (str, optional): 使用するWhisperモデル名。デフォルトは "whisper-large-v3"。
        language (str, optional): 音声の言語コード（ISO 639-1）。デフォルトは "ja"（日本語）。
        response_format (str, optional): APIからのレスポンス形式。デフォルトは "json"。

    Returns:
        str: 文字起こしされたテキスト。エラーが発生した場合はエラーメッセージを返します。
    """
    # 1. データがBase64ならバイナリに変換
    if is_base64:
        binary_audio = base64.b64decode(audio_data)
    else:
        binary_audio = audio_data  # すでにバイナリ（bytes）の場合

    # 2. BytesIOを使って「ファイルオブジェクト」として扱う
    # multipart/form-dataのリクエストにおいて、(ファイル名, データ本体, コンテントタイプ) の形式で指定します
    files = {"file": ("speech.wav", io.BytesIO(binary_audio), "audio/wav")}

    # 3. リクエストパラメータの設定
    data = {
        "model": model,
        "language": language,
        "response_format": response_format,
    }

    headers = {"Authorization": f"Bearer {api_key}"}

    try:
        # 4. POSTリクエストを送信
        response = requests.post(url, headers=headers, files=files, data=data)

        # ステータスコードが200以外の場合は例外を発生させる
        response.raise_for_status()

        return response.json().get("text", "")

    except requests.exceptions.RequestException as e:
        return f"通信エラーが発生しました: {str(e)}"
    except Exception as e:
        return f"予期しないエラーが発生しました: {str(e)}"
