# ResponseOperator.py
# import json

import jmespath


class ResponseOperator:
    """
    レスポンスデータを操作するクラス
    """

    def extract_property_from_json(self, json_data, property_path):
        """
        JSONデータから指定されたプロパティパスの値を取得します。

        Args:
            json_data (dict): JSONデータ
            property_path (str): プロパティパス (例: "completion.tags[0].value")

        Returns:
            any: プロパティパスに対応する値。エラーが発生した場合はNone
        """
        try:
            # print(f"Extracting property: {property_path}")
            if property_path == ".":
                # プロパティパスが "." の場合は全てのプロパティを返す
                return json_data

            # プロパティパスを分割し、各キーを順番に辿る
            keys = property_path.split(".")
            value = json_data

            # when property_path has wildcard like "data[*].id"
            # if "[*]" in property_path:
            if "*" in property_path:
                value = jmespath.search(property_path, value)
                return value

            # when there is not wildcard in property_path
            for key in keys:
                # リストのインデックスにアクセスする場合
                if "[" in key and "]" in key:
                    # キーとインデックスを分離
                    key_name, index = key.split("[")
                    index = int(index[:-1])  # 閉じ括弧を削除して整数に変換

                    # キーが存在しない場合はエラー
                    if key_name and key_name not in value:
                        raise KeyError(f"キー '{key_name}' が見つかりません。")

                    # インデックスが無効な場合はエラー
                    if not isinstance(value[key_name], list) or index >= len(
                        value[key_name]
                    ):
                        raise IndexError(
                            f"インデックス '{index}' が範囲外です。"
                        )

                    value = value[key_name][index]
                else:
                    # キーが存在しない場合はエラー
                    if key not in value:
                        raise KeyError(f"キー '{key}' が見つかりません。")
                    value = value[key]

            return value
        except (KeyError, TypeError, IndexError) as e:
            # プロパティが見つからない場合はエラーメッセージを返す
            raise f"プロパティの抽出に失敗しました: {e}"
