import hashlib
import hmac

import boto3
from django.conf import settings


def get_at(index, t):
    try:
        value = t[index]
    except IndexError:
        value = None
    return value


def get_s3direct_destinations():
    """Returns s3direct destinations.

    NOTE: Don't use constant as it will break ability to change at runtime (e.g. tests)
    """
    return getattr(settings, 'AWS_DESTINATIONS', None)


# AWS Signature v4 Key derivation functions. See:
# http://docs.aws.amazon.com/general/latest/gr/signature-v4-examples.html#signature-v4-examples-python

def sign(key, message):
    return hmac.new(key, message.encode("utf-8"), hashlib.sha256).digest()


def get_aws_v4_signing_key(key, signing_date, region, service):
    datestamp = signing_date.strftime('%Y%m%d')
    date_key = sign(('AWS4' + key).encode('utf-8'), datestamp)
    k_region = sign(date_key, region)
    k_service = sign(k_region, service)
    k_signing = sign(k_service, 'aws4_request')
    return k_signing


def get_aws_v4_signature(key, message):
    return hmac.new(key, message.encode('utf-8'), hashlib.sha256).hexdigest()


def get_s3_url(file):
    if settings.TESTING:
        return 'http://localhost/'
    
    if file.s3_bucket is None or file.s3_key is None:
        return None
    if len(file.s3_bucket) == 0 or len(file.s3_key) == 0:
        return None

    s3 = boto3.client(
        's3',
        aws_access_key_id=settings.AWS_ACCESS_KEY,
        aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
        region_name=settings.AWS_REGION,
    )

    # Generate the URL to get 'key-name' from 'bucket-name'
    url = s3.generate_presigned_url(
        ClientMethod='get_object',
        Params={
            'Bucket': file.s3_bucket,
            'Key': file.s3_key,
            'ResponseContentDisposition': 'attachment; filename={}'.format(file.name)
        }
    )

    return url


def delete_s3_object(file):
    if file.s3_bucket is None or file.s3_key is None:
        return None
    if len(file.s3_bucket) == 0 or len(file.s3_key) == 0:
        return None

    s3 = boto3.client(
        's3',
        aws_access_key_id=settings.AWS_ACCESS_KEY,
        aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
        region_name=settings.AWS_REGION,
    )
    s3.delete_object(Bucket=file.s3_bucket, Key=file.s3_key)
