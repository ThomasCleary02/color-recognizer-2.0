from fastapi import FastAPI, HTTPException, UploadFile, File
from app.image_analyzer import ImageAnalyzer
from dotenv import load_dotenv, find_dotenv
import tempfile
import os

load_dotenv(find_dotenv())

bucket = os.getenv('S3_BUCKET')

app = FastAPI()

@app.post("/analyze-image")
async def analyze_image(
    file: UploadFile = File(...),
):
    try:
        with tempfile.NamedTemporaryFile(delete=False) as temp_file:
            content = await file.read()
            temp_file.write(content)
            temp_path = temp_file.name

        with ImageAnalyzer(
            image_path=temp_path,
            filename=file.filename,
            s3_bucket=bucket
        ) as analyzer:
            results = analyzer.analyze(
                max_labels= 5,
                min_confidence=80
            )
        if results:
            return {
                "status": "success",
                "results": results,
                "confidence": "high"
            }
        else:
            results = analyzer.analyze(
                max_labels=5,
                min_confidence=60,
            )
            if results:
                return {
                    "status": "success",
                    "results": results,
                    "confidence": "low"
                }
            else:
                return {
                    "status": "Failed",
                    "results": "None"
                }
    
            
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error processing image: {str(e)}"
        )
    
    finally:
        # Clean up temporary file
        if os.path.exists(temp_path):
            os.unlink(temp_path)