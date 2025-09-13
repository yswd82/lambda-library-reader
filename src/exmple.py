from app import lambda_handler

event = {
    "queryStringParameters": {
        "area": "suginami",
        "userid": "xxxxxxxx",
        "password": "xxxxxxxx",
    }
}
res = lambda_handler(event, None)
print(res)
