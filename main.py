from fastapi import FastAPI, HTTPException, UploadFile, File
from app.image_analyzer import ImageAnalyzer
from dotenv import load_dotenv, find_dotenv
from mangum import Mangum
import tempfile
import logging
import os
import imghdr  # Add this to verify image files

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)
load_dotenv(find_dotenv())

bucket = os.getenv('S3_BUCKET')

stage = os.environ.get('STAGE', None)
root_path = f"/{stage}" if stage else ""
app = FastAPI(root_path=root_path)

@app.get("/health")
async def health_check():
    return {    
                "status": "healthy",
                "message": "The Lambda function is working properly"
            }

@app.post("/analyze-image")
async def analyze_image(
    file: UploadFile = File(...),
):
    logger.debug(f"Received file: {file.filename}")
    logger.debug(f"Content type: {file.content_type}")
    
    temp_path = None
    try:
        # Create temp file with a specific suffix to help with format detection
        suffix = os.path.splitext(file.filename)[1]
        with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as temp_file:
            content = await file.read()
            logger.debug(f"Read content length: {len(content)}")
            temp_file.write(content)
            temp_path = temp_file.name
            
        # Verify the image file
        logger.debug(f"Temp file path: {temp_path}")
        logger.debug(f"File exists: {os.path.exists(temp_path)}")
        logger.debug(f"File size: {os.path.getsize(temp_path)}")
        logger.debug(f"Image type: {imghdr.what(temp_path)}")
        
        with ImageAnalyzer(
            image_path=temp_path,
            filename=file.filename,
            s3_bucket=bucket
        ) as analyzer:
            results = analyzer.analyze(
                max_labels=5,
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
        logger.exception("Error processing image")
        raise HTTPException(
            status_code=500,
            detail=f"Error processing image: {str(e)}"
        )
    
    finally:
        # Clean up temporary file
        if temp_path and os.path.exists(temp_path):
            try:
                os.unlink(temp_path)
            except Exception as e:
                logger.error(f"Error deleting temp file: {e}")

handler = Mangum(app, lifespan="off")
logger.info("Mangum handler initialized")