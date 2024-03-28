#
#  MIT License
#
#  (C) Copyright 2020-2023 Hewlett Packard Enterprise Development LP
#
#  Permission is hereby granted, free of charge, to any person obtaining a
#  copy of this software and associated documentation files (the "Software"),
#  to deal in the Software without restriction, including without limitation
#  the rights to use, copy, modify, merge, publish, distribute, sublicense,
#  and/or sell copies of the Software, and to permit persons to whom the
#  Software is furnished to do so, subject to the following conditions:
#
#  The above copyright notice and this permission notice shall be included
#  in all copies or substantial portions of the Software.
#
#  THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
#  IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
#  FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL
#  THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR
#  OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE,
#  ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR
#  OTHER DEALINGS IN THE SOFTWARE.
#

"""Module containing a few s3 helper functions, built upon boto3"""

import boto3
import datetime
import json


def get_s3_client(s3_url: str, s3_key_id: str, s3_access_key: str) -> boto3.client:

    """Create and return boto3 session"""
    
    session = boto3.Session()
    return session.client(
        's3',
        aws_access_key_id=s3_key_id,
        aws_secret_access_key=s3_access_key,
        endpoint_url=s3_url,
        verify=False
    )

def list_bucket_objects(s3_client: boto3.client, bucket: str) -> list:

    """List objects in a target S3 bucket"""

    def datetime_handler(x):
        if isinstance(x, datetime.datetime):
            return x.isoformat()
        raise TypeError(f"Unknown type: {type(x)}")

    files = []
    paginator = s3_client.get_paginator('list_objects')
    pages = paginator.paginate(Bucket=bucket)

    for page in pages:
        if 'Contents' in page:
            for obj in page['Contents']:
                files.append(obj)

    return json.loads(json.dumps(files, default=datetime_handler))


def get_s3_object(s3_client: boto3.client, bucket: str, key: str) -> bytes:

    """Download an S3 object provided by key, from bucket"""

    response = s3_client.get_object(Bucket=bucket, Key=key)
    return response['Body']