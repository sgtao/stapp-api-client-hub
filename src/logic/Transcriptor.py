# Transcriptor.py
import io
import speech_recognition as sr


class Transcriptor:
    def __init__(self, language="ja-JP"):
        self.recognizer = sr.Recognizer()
        self.language = language

    def transcribe(self, audio_bytes: bytes) -> str:
        with sr.AudioFile(io.BytesIO(audio_bytes)) as source:
            audio_data = self.recognizer.record(source)

            try:
                return self.recognizer.recognize_google(
                    audio_data,
                    language=self.language,
                )

            except sr.UnknownValueError:
                raise sr.UnknownValueError(
                    "音声を認識できませんでした。もう一度試してください。"
                )
            except sr.RequestError as e:
                raise sr.RequestError(f"音声認識サービスへの接続エラー: {e}")
