import base64
import datetime
import hashlib
import hmac
import json
from urllib.parse import urlencode, quote

import requests
from rest_framework.decorators import api_view, permission_classes, authentication_classes
from rest_framework.response import Response


def encode_dict(dictionary, prefix=""):
    items = []
    for key, value in dictionary.items():
        new_key = f"{prefix}[{key}]" if prefix else key
        if isinstance(value, dict):
            items.extend(encode_dict(value, new_key).items())
        elif isinstance(value, list):
            for idx, item in enumerate(value):
                items.extend(encode_dict(item, f"{new_key}[{idx}]").items())
        else:
            items.append((new_key, str(value)))
    return dict(items)


def verify_signature(signature, data, secret_key):
    computed_signature = hmac.new(secret_key.encode('utf-8'), data.encode('utf-8'),
                                  digestmod=hashlib.sha256).hexdigest()
    return signature == computed_signature


@api_view(['POST'])
@permission_classes([])
@authentication_classes([])
def request_view(req):
    data = json.loads(req.body)
    # create a unique order id
    data['order_id'] = int(datetime.datetime.now().timestamp() * 1000)
    # data['order_id'] = 1699075379007
    # sort the data according to keys
    sorted_data = {k: data[k] for k in sorted(data)}
    encoded_data = encode_dict(sorted_data)
    print(urlencode(encoded_data))
    args_string = urlencode(encoded_data)
    print(args_string)
    secret_key = b"0a634fc47368f55f1f54e472283b3acd"
    public_key = "de1e85e8a087fed83e4a3ba9dfe36f08"

    signature = hmac.new(key=secret_key, msg=args_string.encode('utf-8'), digestmod=hashlib.sha256).hexdigest()
    print(signature)
    # Combine the public key and signature with a colon
    combined_string = f"{public_key}:{signature}"

    # Encode the combined string to Base64
    auth_str = base64.b64encode(combined_string.encode('utf-8')).decode('utf-8')

    print(auth_str)

    url = "https://test.payerurl.com/api/payment"

    headers = {
        "Content-Type": "application/x-www-form-urlencoded;charset=UTF-8",
        "Authorization": f"Bearer {auth_str}",
    }

    data = args_string

    response = requests.post(url, headers=headers, data=data)

    context = {}

    if response.status_code == 200:
        re_data = response.json()
        print(re_data)
        context['redirectTO'] = re_data['redirectTO']

    # print(query_params)
    return Response(context, 200)


def response_view(request):
    payerurl_secret_key = "0a634fc47368f55f1f54e472283b3acd"
    payerurl_public_key = "de1e85e8a087fed83e4a3ba9dfe36f08"
    data = json.loads(request.body)
    print("data", data)
    auth_str = request.META.get("HTTP_AUTHORIZATION")

    if not auth_str or not auth_str.startswith("Bearer "):
        auth_str_post = base64.b64decode(request.data.get("authStr")).decode('utf-8')
        auth = auth_str_post.split(":")
    else:
        auth_str_decoded = base64.b64decode(auth_str.replace("Bearer ", "")).decode('utf-8')
        auth = auth_str_decoded.split(":")

    if payerurl_public_key != auth[0]:
        response = {"status": 2030, "message": "Public key doesn't match"}
        return Response(response, status=200)

    GETDATA = {
        "order_id": data.get("order_id"),
        "ext_transaction_id": data.get("ext_transaction_id"),
        "transaction_id": data.get("transaction_id"),
        "status_code": data.get("status_code"),
        "note": data.get("note"),
        "confirm_rcv_amnt": data.get("confirm_rcv_amnt"),
        "confirm_rcv_amnt_curr": data.get("confirm_rcv_amnt_curr"),
        "coin_rcv_amnt": data.get("coin_rcv_amnt"),
        "coin_rcv_amnt_curr": data.get("coin_rcv_amnt_curr"),
        "txn_time": data.get("txn_time"),
    }

    if not GETDATA["transaction_id"]:
        response = {"status": 2050, "message": "Transaction ID not found"}
        return Response(response, status=200)
    elif not GETDATA["order_id"]:
        response = {"status": 2050, "message": "Order ID not found"}
        return Response(response, status=200)
    elif GETDATA["status_code"] == 20000:
        response = {"status": 20000, "message": "Order Cancelled"}
        return Response(response, status=200)
    elif GETDATA["status_code"] != 200:
        response = {"status": 2050, "message": "Order not complete"}
        return Response(response, status=200)

    # Add advanced security checks if needed

    # Uncomment the following section if you want to check the signature
    # sorted_args_keys = {}
    # for key in sorted(GETDATA.keys()):
    #     sorted_args_keys[key] = GETDATA[key]
    #
    # if not verify_signature(auth[1], sorted_args_keys, payerurl_secret_key):
    #     response = {"status": 2030, "message": "Signature not matched."}
    #     return Response(response, status=200)

    data = {"status": 2040, "message": GETDATA}

    # Your custom code here

    filename = "payerurl.log"
    with open(filename, "a") as log_file:
        log_file.write(json.dumps(data))
        log_file.write("\n")

    return Response(data, status=200)
    pass
