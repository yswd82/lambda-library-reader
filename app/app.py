from dataclasses import asdict
from library_reader import (
    SuginamiLibraryReader,
    MinatoLibraryReader,
    NerimaLibraryReader,
)


def lambda_handler(event, context):
    # クエリパラメータを取得
    param = event.get("queryStringParameters")
    area = param["area"]
    userid = param["userid"]
    password = param["password"]

    # リーダーを設定
    if area == "suginami":
        lib_reader = SuginamiLibraryReader(userid, password)
    elif area == "minato":
        lib_reader = MinatoLibraryReader(userid, password)
    elif area == "nerima":
        lib_reader = NerimaLibraryReader(userid, password)
    else:
        raise Exception

    # 取得結果を受け取る
    contents = {
        "lent_items": [asdict(_) for _ in lib_reader.lent],
        "reserve_items": [asdict(_) for _ in lib_reader.reserve],
    }

    # lambdaのresponseはjson.dumps()されているのでdictをそのまま渡す
    return {
        "statusCode": 200,
        "body": contents,
    }
