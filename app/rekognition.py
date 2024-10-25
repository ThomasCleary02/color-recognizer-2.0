import boto3

rekognition = boto3.client('rekognition')

def send_request(max_labels: int, min_confidence: int, filepath: str, bucket: str):
    try:
        rekognition = boto3.client('rekognition')
        
        import time
        time.sleep(2)  # Add a small delay after upload
        
        response = rekognition.detect_labels(
            Image={
                'S3Object': {
                    'Bucket': bucket,
                    'Name': filepath,
                }
            },
            MaxLabels=max_labels,
            MinConfidence=min_confidence
        )
        return response
    except rekognition.exceptions.InvalidS3ObjectException:
        print("Error: Image not found in S3. Please verify the image was uploaded successfully and the correct path is being used.")
        return None
    except Exception as e:
        print(f"Something went wrong with Rekognition: {e}")
        return None

def parse_labels(rekognition_response: dict):
    if not rekognition_response:
        return []
        
    labels = []
    for label in rekognition_response["Labels"]:
        name = label["Name"]
        if label["Instances"]:
            for instance in label["Instances"]:
                labels.append({
                    "name": name,
                    "bounding_box": instance["BoundingBox"]
                })
        else:
            labels.append({
                "name": name,
                "bounding_box": None
            })
    return labels

def convert_coordinates(labels: list, img_height: int, img_width: int):
    if img_height <= 0 or img_width <= 0:
        raise ValueError("Height and width must be positive")
        
    try:
        new_list = []
        for item in labels:
            if item['bounding_box'] is not None:
                bb = item['bounding_box']
                left = int(bb['Left'] * img_width)
                top = int(bb['Top'] * img_height)
                width = int(bb['Width'] * img_width)
                height = int(bb['Height'] * img_height)

                right = left + width
                bottom = top + height

                new_list.append({
                    "identifier": item["name"],
                    "coordinates": {
                        "left": left,
                        "top": top,
                        "right": right,
                        "bottom": bottom,
                    },
                })
        return new_list
        
    except KeyError as e:
        print(f"Missing expected key in response: {e}")
        return []
    except TypeError as e:
        print(f"Invalid type in coordinates calculation: {e}")
        return []
    except Exception as e:
        print(f"Unexpected error converting coordinates: {e}")
        return []

    