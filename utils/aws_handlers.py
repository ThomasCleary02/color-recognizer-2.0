import boto3
import json

s3_client = boto3.client('s3')
rekognition = boto3.client('rekognition')

bucket = "color-analyzer-images"

def upload_image(image, filename):
    try:
        s3_client.upload_file(image, bucket, filename)
    except Exception as e:
        print(f"Error uploading the selected file {e}")

def delete_image(file_path):
    try:
        s3_client.delete_object(Bucket=bucket, Key=file_path)
    except Exception as e:
        print(f"Error deleteting the specified file {e}")

def rekognition_request(image, max_labels, min_confidence):
    temp_key = "test_img"
    try:
        upload_image(image, temp_key)
        response = rekognition.detect_labels(
            Image = {
                'S3Object': {
                    'Bucket': bucket,
                    'Name': temp_key,
                }
            },
            MaxLabels = max_labels,
            MinConfidence = min_confidence)
        formatted_response = json.dumps(response)
        delete_image(temp_key)
        return formatted_response
    except Exception as e:
        print(f"Error sending rekognition request {e}")

if __name__ == "__main__":
    print(rekognition_request("test-image-2.jpg", 5, 80))