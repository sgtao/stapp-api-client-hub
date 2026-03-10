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
    # 1. データがBase64ならバイナリに変換
    if is_base64:
        binary_audio = base64.b64decode(audio_data)
    else:
        binary_audio = audio_data  # すでにバイナリ（bytes）の場合

    # 2. BytesIOを使って「ファイルオブジェクト」として扱う
    # 第2引数は (ファイル名, データ本体, コンテントタイプ) です
    files = {"file": ("speech.wav", io.BytesIO(binary_audio), "audio/wav")}

    # 3. その他のパラメータ
    data = {
        "model": model,
        "language": language,
        "response_format": response_format,
    }

    headers = {"Authorization": f"Bearer {api_key}"}

    # 4. POSTリクエストを送信
    response = requests.post(url, headers=headers, files=files, data=data)

    if response.status_code == 200:
        return response.json().get("text")
    else:
        return f"Error: {response.status_code} - {response.text}"
