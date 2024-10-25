from app.rekognition import parse_labels, convert_coordinates, send_request
from app.img_processer import analyze_snippet
from app.s3_image import S3Image


class ImageAnalyzer:
    def __init__(self, image_path: str, filename: str, bucket: str):
        self.image = S3Image(image_path, filename, bucket)

    def analyze(self, max_labels: int, min_confidence: int):
        try:
            self.image.upload()

            data = send_request(
                max_labels,
                min_confidence,
                self.image.filename(),
                self.image.bucket
            )

            labels = parse_labels(data)

            cords = convert_coordinates(
                labels,
                self.image.height(),
                self.image.width(),
            )

            items = []
            for cord in cords:
                color = analyze_snippet(
                    self.image.image,
                    cord['coordinates']['left'],
                    cord['coordinates']['top'],
                    cord['coordinates']['right'],
                    cord['coordinates']['bottom'],
                    1
                )

                obj = {
                    'item': cord['identifier'],
                    'color': color
                }
                items.append(obj)
                
            return items
        
        finally:
            # Clean up S3
            self.image.delete()

    def __enter__(self):
            return self
        
    def __exit__(self, exc_type, exc_val, exc_tb):
            self.image.delete()
            return False