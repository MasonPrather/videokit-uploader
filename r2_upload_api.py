import os
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import boto3
from botocore.client import Config
from fastapi.middleware.cors import CORSMiddleware

# --- Env ---
R2_ACCOUNT_ID = os.environ["R2_ACCOUNT_ID"]
R2_ACCESS_KEY = os.environ["R2_ACCESS_KEY"]
R2_SECRET_KEY = os.environ["R2_SECRET_KEY"]
R2_BUCKET     = os.environ["R2_BUCKET"]

# S3 client for R2
s3 = boto3.client(
    "s3",
    aws_access_key_id=R2_ACCESS_KEY,
    aws_secret_access_key=R2_SECRET_KEY,
    endpoint_url=f"https://{R2_ACCOUNT_ID}.r2.cloudflarestorage.com",
    config=Config(signature_version="s3v4"),
    region_name="auto",
)

app = FastAPI(title="VideoKit_Uploader", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["POST", "OPTIONS"],
    allow_headers=["*"],
)

class PresignPutReq(BaseModel):
    key: str
    content_type: str = "video/mp4"

class PresignGetReq(BaseModel):
    key: str

@app.post("/presign-put")
def presign_put(req: PresignPutReq):
    try:
        expires = 60 * 10  # 10 minutes
        put_url = s3.generate_presigned_url(
            "put_object",
            Params={
                "Bucket": R2_BUCKET,
                "Key": req.key,
                "ContentType": req.content_type,
            },
            ExpiresIn=expires,
        )
        get_url = s3.generate_presigned_url(
            "get_object",
            Params={"Bucket": R2_BUCKET, "Key": req.key},
            ExpiresIn=expires,
        )
        return {"key": req.key, "put_url": put_url, "get_url": get_url}
    except Exception as e:
        raise HTTPException(500, f"presign error: {e}")

@app.post("/presign-get")
def presign_get(req: PresignGetReq):
    try:
        expires = 60 * 10
        url = s3.generate_presigned_url(
            "get_object",
            Params={"Bucket": R2_BUCKET, "Key": req.key},
            ExpiresIn=expires,
        )
        return {"url": url, "expires_in": expires}
    except Exception as e:
        raise HTTPException(500, f"presign error: {e}")