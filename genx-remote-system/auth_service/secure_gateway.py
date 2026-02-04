from flask import Flask, request, Response
import requests
from device_auth import verify_device_fingerprint

app = Flask(__name__)

# The address of your LiteWriter server
LITEWRITER_SERVER = "http://10.62.78.114:8000"

# The build number of the authorized device
AUTHORIZED_BUILD_NUMBER = "15.1.1.109SP06(OP001PF001AZ)"

@app.route('/', defaults={'path': ''})
@app.route('/<path:path>', methods=['GET', 'POST', 'PUT', 'DELETE', 'PATCH'])
def proxy_request(path):
    """
    Acts as a secure gateway, verifying device identity before proxying requests.
    """
    # Get device identity headers from the incoming request
    fingerprint = request.headers.get("X-Device-Fingerprint")
    build_number = request.headers.get("X-Device-Build-Number")

    # Check if headers are present
    if not fingerprint or not build_number:
        return "Unauthorized: Missing device identity headers.", 401

    # Verify the device fingerprint
    if build_number != AUTHORIZED_BUILD_NUMBER or not verify_device_fingerprint(build_number, fingerprint):
        return "Forbidden: Invalid device fingerprint.", 403

    # If the fingerprint is valid, forward the request to the LiteWriter server
    try:
        resp = requests.request(
            method=request.method,
            url=f"{LITEWRITER_SERVER}/{path}",
            headers={key: value for (key, value) in request.headers if key != 'Host'},
            data=request.get_data(),
            cookies=request.cookies,
            allow_redirects=False
        )

        # Create a response to send back to the client
        excluded_headers = ['content-encoding', 'content-length', 'transfer-encoding', 'connection']
        headers = [(name, value) for (name, value) in resp.raw.headers.items()
                   if name.lower() not in excluded_headers]

        response = Response(resp.content, resp.status_code, headers)
        return response

    except requests.exceptions.RequestException as e:
        return f"Error proxying request: {e}", 502


if __name__ == '__main__':
    # This gateway should be run with a production-ready WSGI server like Gunicorn or uWSGI.
    # Example: gunicorn --bind 127.0.0.1:5001 secure_gateway:app
    app.run(host='127.0.0.1', port=5001)