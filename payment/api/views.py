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
    """
    sample object
    payment_request = {
    'order_id': 1922658446,
    'amount': 123,
    'items': [
        {
            'name': 'Order item name',
            'qty': '1',
            'price': '123',
        },
    ],
    'currency': 'usd',
    'billing_fname': 'billing fname',
    'billing_lname': 'billing lname',
    'billing_email': 'test@gmail.com',
    'redirect_to': 'http://localhost:3000/success',
    'notify_url': 'http://localhost:4000/response',  // PayerURL will send a callback to this URL once the payment is successfully completed.
    'cancel_url': 'http://localhost:3000/cancel',
    'type': 'php',
}
    """
    # sort the data according to keys
    sorted_data = {k: data[k] for k in sorted(data)}
    encoded_data = encode_dict(sorted_data)
    print(urlencode(encoded_data))
    args_string = urlencode(encoded_data)
    print(args_string)
    secret_key = "0a634fc47368f55f1f54e472283b3acd"
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


########################  contact us telegram : @payerurl to get response function
    pass
