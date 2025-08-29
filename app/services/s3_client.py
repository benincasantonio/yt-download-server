import os

import logging
from typing import Optional

import boto3
from botocore.exceptions import ClientError, NoCredentialsError
from botocore.config import Config

logger = logging.getLogger(__name__)

class S3Client:
    def __init__(self):
        """Initialize S3 client with environment variables"""
        self.endpoint_url = os.getenv('S3_ENDPOINT_URL')
        self.access_key = os.getenv('S3_ACCESS_KEY_ID')
        self.secret_key = os.getenv('S3_SECRET_ACCESS_KEY')
        self.bucket_name = os.getenv('S3_BUCKET_NAME')
        self.region = os.getenv('S3_REGION', 'us-east-1')
        self.use_ssl = os.getenv('S3_USE_SSL', 'true').lower() == 'true'
        self.verify_ssl = os.getenv('S3_VERIFY_SSL', 'true').lower() == 'true'

        if not all([self.access_key, self.secret_key, self.bucket_name]):
            raise ValueError("Missing required S3 configuration: S3_ACCESS_KEY_ID, S3_SECRET_ACCESS_KEY, or S3_BUCKET_NAME")

        # Configure boto3 client
        config = Config(
            region_name=self.region,
            retries={'max_attempts': 3, 'mode': 'adaptive'},
            s3={'addressing_style': 'path'}
        )

        self.client = boto3.client(
            's3',
            endpoint_url=self.endpoint_url,
            aws_access_key_id=self.access_key,
            aws_secret_access_key=self.secret_key,
            config=config,
            use_ssl=self.use_ssl,
            verify=self.verify_ssl
        )

        # Create bucket if it doesn't exist
        self._ensure_bucket_exists()

    def _ensure_bucket_exists(self):
        """Create bucket if it doesn't exist"""
        try:
            self.client.head_bucket(Bucket=self.bucket_name)
            logger.info(f"Bucket '{self.bucket_name}' already exists")
        except ClientError as e:
            error_code = e.response['Error']['Code']
            if error_code in ("NoSuchBucket", "404"):
                try:
                    self.client.create_bucket(Bucket=self.bucket_name)
                    logger.info(f"Created bucket '{self.bucket_name}'")
                except ClientError as create_error:
                    logger.error(f"Failed to create bucket: {create_error}")
                    raise
            else:
                logger.error(f"Error checking bucket: {e}")
                raise

    def upload_file(self, file_path: str, object_key: str) -> bool:
        """Upload a file to S3-compatible storage"""
        try:
            self.client.upload_file(file_path, self.bucket_name, object_key)
            logger.info(f"Successfully uploaded {file_path} as {object_key}")
            return True
        except FileNotFoundError:
            logger.error(f"File not found: {file_path}")
            return False
        except NoCredentialsError:
            logger.error("S3 credentials not available")
            return False
        except ClientError as e:
            logger.error(f"Failed to upload file: {e}")
            return False

    def download_file(self, object_key: str, file_path: str) -> bool:
        """Download a file from S3-compatible storage"""
        try:
            self.client.download_file(self.bucket_name, object_key, file_path)
            logger.info(f"Successfully downloaded {object_key} to {file_path}")
            return True
        except ClientError as e:
            logger.error(f"Failed to download file: {e}")
            return False

    def delete_file(self, object_key: str) -> bool:
        """Delete a file from S3-compatible storage"""
        try:
            self.client.delete_object(Bucket=self.bucket_name, Key=object_key)
            logger.info(f"Successfully deleted {object_key}")
            return True
        except ClientError as e:
            logger.error(f"Failed to delete file: {e}")
            return False

    def get_file_url(self, object_key: str, expiration: int = 3600) -> Optional[str]:
        """Generate a presigned URL for file access"""
        try:
            url = self.client.generate_presigned_url(
                'get_object',
                Params={'Bucket': self.bucket_name, 'Key': object_key},
                ExpiresIn=expiration
            )
            return url
        except ClientError as e:
            logger.error(f"Failed to generate presigned URL: {e}")
            return None

    def list_files(self, prefix: str = "") -> list:
        """List files in the bucket with optional prefix"""
        try:
            response = self.client.list_objects_v2(
                Bucket=self.bucket_name,
                Prefix=prefix
            )
            if 'Contents' in response:
                return [obj['Key'] for obj in response['Contents']]
            return []
        except ClientError as e:
            logger.error(f"Failed to list files: {e}")
            return []

    def file_exists(self, object_key: str) -> bool:
        """Check if a file exists in the bucket"""
        try:
            self.client.head_object(Bucket=self.bucket_name, Key=object_key)
            return True
        except ClientError:
            return False

# Global S3 client instance
s3_client = None

def get_s3_client() -> S3Client:
    """Get or create S3 client instance"""
    global s3_client
    if s3_client is None:
        s3_client = S3Client()
    return s3_client
