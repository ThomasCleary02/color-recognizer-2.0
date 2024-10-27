import base64
import json
import os
import mimetypes

def create_test_event(image_path):
    # Verify the image exists
    if not os.path.exists(image_path):
        raise FileNotFoundError(f"Image file not found: {image_path}")
    
    # Get the file mime type
    mime_type, _ = mimetypes.guess_type(image_path)
    if not mime_type or not mime_type.startswith('image/'):
        raise ValueError(f"Not a valid image file: {image_path}")
    
    # Read and encode the image
    with open(image_path, 'rb') as image_file:
        file_content = image_file.read()
        encoded_content = base64.b64encode(file_content).decode('utf-8')

    # Create multipart form-data boundary
    boundary = "------------------------d74496d66958873e"
    filename = os.path.basename(image_path)
    
    # Create the multipart form-data body
    body = (
        f'--{boundary}\r\n'
        f'Content-Disposition: form-data; name="file"; filename="{filename}"\r\n'
        f'Content-Type: {mime_type}\r\n'
        '\r\n'
        f'{encoded_content}\r\n'
        f'--{boundary}--'
    )

    # Encode the entire body as base64
    body_bytes = body.encode('utf-8')
    base64_body = base64.b64encode(body_bytes).decode('utf-8')

    # Create the test event
    test_event = {
        "version": "2.0",
        "routeKey": "POST /analyze-image",
        "rawPath": "/analyze-image",
        "rawQueryString": "",
        "headers": {
            "content-type": f"multipart/form-data; boundary={boundary}",
            "x-forwarded-proto": "https",
            "x-forwarded-port": "443"
        },
        "requestContext": {
            "accountId": "654654360671",
            "apiId": "kkxfxeneah",
            "domainName": "kkxfxeneah.execute-api.us-east-1.amazonaws.com",
            "domainPrefix": "kkxfxeneah",
            "http": {
                "method": "POST",
                "path": "/analyze-image",
                "protocol": "HTTP/1.1",
                "sourceIp": "127.0.0.1",
                "userAgent": "Custom User Agent String"
            },
            "requestId": "c6af9ac6-7b61-11e6-9a41-93e8deadbeef",
            "routeKey": "POST /analyze-image",
            "stage": "$default",
            "time": "09/Apr/2023:12:34:56 +0000",
            "timeEpoch": 1617979216000
        },
        "body": base64_body,
        "isBase64Encoded": True
    }

    return test_event

if __name__ == "__main__":
    # Replace with your image path
    image_path = "test-image.png"
    try:
        test_event = create_test_event(image_path)
        
        # Save the test event to a file
        with open("test_event.json", "w") as f:
            json.dump(test_event, f, indent=2)
        
        print("Test event has been saved to test_event.json")
        print(f"Original image size: {os.path.getsize(image_path)} bytes")
        
    except Exception as e:
        print(f"Error creating test event: {e}")