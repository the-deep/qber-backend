from storages.backends.s3boto3 import S3Boto3Storage
from storages.utils import setting


class S3StaticStorage(S3Boto3Storage):
    location = 'static'
    default_acl = 'public-read'
    querystring_auth = False

    def get_default_settings(self):
        return {
            **super().get_default_settings(),
            'bucket_name': setting('AWS_S3_BUCKET_STATIC'),
        }


class S3MediaStorage(S3Boto3Storage):
    location = 'media'

    def get_default_settings(self):
        return {
            **super().get_default_settings(),
            'bucket_name': setting('AWS_S3_BUCKET_MEDIA'),
        }
