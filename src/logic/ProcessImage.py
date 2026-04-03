# ProcessImage.py
import base64
import io
from PIL import Image  # 追加


class ProcessImage:
    def __init__(self):
        self.image_data = None
        self.resized_image = None

    def set_image_data(self, image_data):
        self.image_data = image_data

    def get_image_data(self):
        return self.image_data

    def resize_image(self, target_height=320):
        """画像データを処理して指定された高さにリサイズする関数"""
        if self.image_data is None:
            return None

        # bytes → BytesIO → PIL.Image
        image = Image.open(io.BytesIO(self.image_data))

        # PIL.Image の width/height を使う（self.image_data ではなく image）
        aspect_ratio = image.width / image.height
        new_width = int(target_height * aspect_ratio)
        resized_image = image.resize((new_width, target_height))

        # リサイズした画像をバイトデータに変換
        output = io.BytesIO()
        resized_image.save(output, format="PNG")
        self.resized_image = output.getvalue()
        return self.resized_image

    def get_resized_image(self):
        return self.resized_image

    def convert_to_base64(self, image_bytes):
        """画像データをbase64エンコードする関数"""
        return base64.b64encode(image_bytes).decode("utf-8")
