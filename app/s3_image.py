from PIL import Image
import boto3
import io

class S3Image:

    def __init__(self, image, file_name, bucket):
        self.s3_client = boto3.client('s3')
        self.image = image
        self.bucket = bucket
        self.file_name = file_name

    def all_objects(self):
        try:
            objects = []
            paginator = self.s3_client.get_paginator('list_objects_v2')
            pages = paginator.paginate(Bucket=self.bucket)
            
            for page in pages:
                if 'Contents' in page:  # Check if bucket has contents
                    for content in page['Contents']:
                        objects.append(content['Key'])
            return objects
        except Exception as e:
            print(f"Error listing objects: {e}")
            return []
    
    def change_filename(self, new_name):
        self.file_name = new_name

    def upload(self):
        try:
            if self.file_name in self.all_objects():
                raise Exception("The specified file name already exists, please use the change_filename('new file name')")
            
            # Verify the file exists locally before attempting upload
            with open(self.image, 'rb') as file:
                self.s3_client.upload_fileobj(file, self.bucket, self.file_name)
            print(f"Successfully uploaded {self.file_name} to {self.bucket}")
            return True
        except FileNotFoundError:
            print(f"Error: The file {self.image} was not found locally")
            return False
        except Exception as e:
            print(f"Error uploading selected file: {e}")
            return False

    def delete(self):
        try:
            self.s3_client.delete_object(Bucket=self.bucket, Key=self.file_name)
        except Exception as e:
            print(f"Error deleting the image from {self.bucket}")

    def filename(self):
        return self.file_name

    def height(self):
        img = Image.open(self.image)
        return img.height

    def width(self):
        img = Image.open(self.image)
        img_width = img.width
        return img_width