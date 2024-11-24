import jwt
import requests
import uuid
import datetime

# Use your full private key here
private_key = """-----BEGIN RSA PRIVATE KEY-----
MIIEpAIBAAKCAQEA3ak6iZ5W1NdBW+sn+2uHeIGeboUxYuQy2ANKcnK3mu3U94rn
6J3QXzSveKGNSaSjPzVzhkZVNc/42yhaNlYgBK+nKW50Di/LWhdK71SO71d9lGqp
Ww1d2kAtAArm7Bosus033Liio7oJcrRZUJPw3T4OXrTsaCCKMlxDS5d/ukCVYr2Y
pAJHq9dfh0KpA05zNRabwSwtMuVnytzZwn0Jaiv4fuH6jWe3ek8IXg8EX9vKs8h/
IP+UggZgTsbQ3/SVywyqEFAYVLbWlAHLXQsKPX4BrNgbbnYiAEGTG8BWILpuMtuD
I4HehAX/9vSlHtLZnZjSbXv/8IiV8L2jx5hCcwIDAQABAoIBAQDFVE1HjE1Sx5po
4QzD93MvpXzMeQiBOBPHWA6jmlq3svi/sspHvI5u4zE/G9ry731g3Q3OQLjE4jNx
rxe4fa2dXl5bNPheVNAckNXmAAoLKoEial4AMAMYM7+b5Ri0oYymc+FCPqCTTx/w
HHvSjxGDdCZIy5oWDLnaoWZLWkCcJg+zUVK5Co5J3JV3wm/tUgAke7jaV2T6vpSd
+S6XJ3TGERsWuSKrItapTijEfbLf+kbwXjZvoRsUu5X38s+HBU2w8XvNcCSAj81Z
kZoJBHKJKEzOoKqWGHcfxW2Sjk+Ie7ZJyLTi9/ZzhFuQlrXnoOB9Uj3SxNF9IXmp
sIg2VYbZAoGBAOBoJks5YjKyw/lrj6dhOnRjJ9kLiEhw+RwF7DEDgvdIXW/+8jrK
Sx4ppWJYB9R2y6tpehOFlamyYkW8h1il3mwk8dVStqS0FhqQoBak/UhGT6VtDkXB
BQRXC0oY3foB5orzEREY0cRAJF7QUxUzRlxm++d0ic9N24T+W+JiG6M/AoGBAPze
HkJYKPjyKl0HOvlQmJ2vKNqquN/2A1f+7AOsf9olL5m0iplIsWncI89oJsGOutGK
CgKkStgCiF+5yspWXfHX2VoyfwhgbZBTgiAEPx02ZuFdD+Gb7gPPp+prDnmPMwWE
HSvDWLrhTg2CSr38kfgRVcORzpTc4YYWnsXznDfNAoGAK9Jq1/nGwVvDhWuJzAfi
oGPUnj/wRyU4oE5Px2qGIsAQ7xP8PZrPfH5pe4DxVn40W67nVfSaO19IbZHZZGhP
vRKh3ySd4iAAyQNBH+rsQzbnysg3J0wALM7Kt5ePkYjZenzo8kvEeuyDrbhE4Tj4
HodF3fcWClOL8LazPswl1YUCgYAmpkiXuWPh0RnaiD1iWAhLqbcj3Q5O5QpTy9oF
IbuU+zQQWUEJ9stvM7+hdvjdgtRZLLElADmUVKbFgt9VF+haC7TkDW3POPXmJm1w
OVXwQB1vesrvn+a8XGP894oJ2HJi+HOA+eW5ArDsbarA6TbiZLvoHYQmyrAJz7FK
7lZFTQKBgQCZ+e/EGzY52A6/NmpYKK9R7C/vKyy3H3ADC+1ypuHI2dQk+0NGKk41
kiTEr7dmkR8yG4ahStvJzYBbNwW7xZhnZFZAwG0FaCCtA7FA99ckzb4gvBlOBtnx
MJVaeFKKvh4StNSjIHefGhmPHh0x7M0YbtbkzIHc6v8OAtN1YCxMcA==
-----END RSA PRIVATE KEY-----"""

key_id = "09a9fd18-64b6-4d7e-94c2-f2889773163d"
application_id = "IxxCXXa2a-6umdciziHx3QfBu6rVrwAR"
redirect_uri = "http://localhost:8000/callback"
scopes = "estimate surge_multiplier low_estimate high_estimate"

# Step 1: Create the JWT Assertion
def create_jwt_assertion():
    header = {
        "alg": "RS256",
        "typ": "JWT",
        "kid": key_id,
    }
    payload = {
        "iss": application_id,
        "sub": application_id,
        "aud": "auth.uber.com",
        "jti": str(uuid.uuid4()),  # unique identifier
        "exp": int((datetime.datetime.utcnow() + datetime.timedelta(minutes=5)).timestamp()),  # expires in 5 minutes
    }
    jwt_assertion = jwt.encode(payload, private_key, algorithm="RS256", headers=header)
    return jwt_assertion

# Step 2: Get the authorization URL
def get_authorization_url():
    auth_url = (
        f"https://auth.uber.com/oauth/v2/authorize?client_id={application_id}"
        f"&redirect_uri={redirect_uri}&scope={scopes}&response_type=code"
    )
    return auth_url

# Step 3: Exchange the authorization code for an access token
def get_access_token(auth_code, jwt_assertion):
    token_url = "https://auth.uber.com/oauth/v2/token"
    data = {
        "grant_type": "authorization_code",
        "code": auth_code,
        "redirect_uri": redirect_uri,
        "client_assertion": jwt_assertion,
        "client_assertion_type": "urn:ietf:params:oauth:client-assertion-type:jwt-bearer",
    }
    response = requests.post(token_url, data=data)
    response_data = response.json()
    access_token = response_data.get("access_token")
    return access_token

# Step 4: Make a request to Uber's API for a price estimate
def get_price_estimate(access_token, start_latitude, start_longitude, end_latitude, end_longitude):
    estimate_url = "https://api.uber.com/v1.2/estimates/price"
    headers = {
        "Authorization": f"Bearer {access_token}"
    }
    params = {
        "start_latitude": start_latitude,
        "start_longitude": start_longitude,
        "end_latitude": end_latitude,
        "end_longitude": end_longitude
    }
    estimate_response = requests.get(estimate_url, headers=headers, params=params)
    return estimate_response.json()

# Main flow
if __name__ == "__main__":
    # Generate JWT assertion
    jwt_assertion = create_jwt_assertion()

    # Step 1: Print the authorization URL
    auth_url = get_authorization_url()
    print("Visit this URL to authorize the app:", auth_url)

    # Step 2: Get the authorization code from the redirect URL
    auth_code = input("Enter the authorization code from the redirect URL: ")

    # Step 3: Get the access token
    access_token = get_access_token(auth_code, jwt_assertion)
    print("Access Token:", access_token)

    # Step 4: Make the price estimate request if the access token is valid
    if access_token:
        start_latitude = 37.7759792
        start_longitude = -122.41823
        end_latitude = 37.7758
        end_longitude = -122.418
        estimate = get_price_estimate(access_token, start_latitude, start_longitude, end_latitude, end_longitude)
        print("Price Estimate Response:", estimate)
    else:
        print("Failed to obtain access token.")