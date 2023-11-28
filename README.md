# PayerURL Integration for Python Applications

This guide provides step-by-step instructions for integrating PayerURL into your Python application, using DRF for demonstration purposes.

## Prerequisites

1. Obtain your API public key and secret key from the [PayerURL website](https://dashboard.payerurl.com/).

## Request Setup

### Step 1: Install Python and Set Up DRF

Follow the instructions at [DRF](https://www.django-rest-framework.org/) to set up your DRF application.
Create a app called payment.

### Step 2: Define Payment Route

Define a route for payment requests (e.g., "request" route).

### Step 3: Define Response Route

Define a response route to handle successful payment responses.

### Step 4: Prepare Request Object

Prepare an object with payment details:

```python
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
    'billing_fname': 'Mohi Uddin',
    'billing_lname': 'Mahim',
    'billing_email': 'mahim@gmail.com',
    'redirect_to': 'http://localhost:3000/success',
    'notify_url': 'http://localhost:4000/response',
    'cancel_url': 'http://localhost:3000/cancel',
    'type': 'php',
}
```
# "order_id" must be unique
Make sure the request object is containing all the parameters.
			 
You need to provide the success page and cancel page url of your frontend application as shown.
Make sure to send the response url (In which you will get the response from payerURL about the payment.) of your backend application as shown.

### Step 5: Write a View for the Request Route

In your payment app, create a view for the payment request route. Sort the object keys, build the query string, create an HMAC signature, and encode it in base64.

```python
# Sort the object keys in ascending order
sorted_data = {k: data[k] for k in sorted(data)}

# Build the required query string
encoded_data = encode_dict(sorted_data)
args_string = urlencode(encoded_data)
	
# Create HMAC signature with sha256 hash
signature = hmac.new(key=secret_key, msg=args_string.encode('utf-8'), digestmod=hashlib.sha256).hexdigest()

# Create auth string in base64 format
combined_string = f"{public_key}:{signature}"
auth_str = base64.b64encode(combined_string.encode('utf-8')).decode('utf-8')
```

### Step 6: Prepare Request Headers and Properties

In this step, you will set up the necessary request headers and make the POST request to PayerURL.

```python
# Set up the request headers
url = "https://test.payerurl.com/api/payment"
headers = {
        "Content-Type": "application/x-www-form-urlencoded;charset=UTF-8",
        "Authorization": f"Bearer {auth_str}",
    }


# Make the request using fetch or axios
data = args_string
response = requests.post(url, headers=headers, data=data)
if response.status_code == 200:
    re_data = response.json()
	context['redirectTO'] = re_data['redirectTO']
```

### Step 7: Get Redirect URL

After making the payment request to PayerURL, you will need to extract the "redirectTO" from the response (`re_data`) and send it to the frontend to redirect the user to this URL.


## Response Handling

### Step 1: Decode Authorization Header

In your response route, decode the Authorization header and split the public key and signature.

```python
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
```

### Step 2: Process Response
Process the PayerURL response and handle various scenarios.

```python
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
	
	"""
    # Add advanced security checks if needed
    # sorted_args_keys = {}
    # for key in sorted(GETDATA.keys()):
    #     sorted_args_keys[key] = GETDATA[key]
    #
    # if not verify_signature(auth[1], sorted_args_keys, payerurl_secret_key):
    #     response = {"status": 2030, "message": "Signature not matched."}
    #     return Response(response, status=200)
	"""
    data = {"status": 2040, "message": GETDATA}
	"""
	#
	#
	#   Your custom code here
	#
	#
	"""
```

