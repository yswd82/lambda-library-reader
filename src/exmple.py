from app import lambda_handler

event = {
    "queryStringParameters": {
        "area": "nakano",
        "userid": "xxxx",
        "password": "xxxx",
    }
}
res = lambda_handler(event, None)
res = res["body"]
lent_items = res["lent_items"]
for lent in lent_items:
    print(lent)
reserve_items = res["reserve_items"]
for reserve in reserve_items:
    print(reserve)
