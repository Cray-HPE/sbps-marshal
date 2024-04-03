#
#  MIT License
#
#  (C) Copyright 2023-2024 Hewlett Packard Enterprise Development LP
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

"""Module to support IMS image querying"""

import json
import requests

from _collections_abc import Iterable


# IMS Image Query Example
""" [
    {
        "arch": "x86_64",
        "created": "2023-07-13T22:12:48.199410+00:00",
        "id": "7ad92035-5bb9-413e-96f7-32af04dc08f0",
        "link": {
            "etag": "f3f802d2a1e9193d5207bd2952d365e8",
            "path": "s3://boot-images/7ad92035-5bb9-413e-96f7-32af04dc08f0/manifest.json",
            "type": "s3"
        },
        "name": "cray-shasta-csm-sles15sp5-barebones-csm-1.5"
    },
    ] """

# IMS Image Query Example with tag (annotation) support
""" [
    {
        "id": "46a2731e-a1d0-4f98-ba92-4f78c756bb12",
        "created": "2018-07-28T03:26:01.234Z",
        "name": "centos7.5_barebones",
        "link": {
        "path": "s3://boot-images/1fb58f4e-ad23-489b-89b7-95868fca7ee6/manifest.json",
        "etag": "f04af5f34635ae7c507322985e60c00c-131",
        "type": "s3"
        },
        "arch": "aarch64",
        "metadata": {
        "annotations": [
            {
            "key": "includes_additional_packages",
            "value": "foo,bar,baz"
            }
        ]
        }
    }
    ]"""

# IMS Image Manifest Example
""" {
    'artifacts': 
    [
        {'link': {
            'etag': '2a94bb6ce5be4f6f0aa5af23f969d739-56', 
            'path': 's3://boot-images/4842867f-a9bc-4c2a-ad84-fcc3c931bdad/rootfs', 
            'type': 's3'}, 
        'md5': '6bf3d465a59b543b00a6d4b7d25d1eec', 
        'type': 'application/vnd.cray.image.rootfs.squashfs'},
    ]
    } """

def images(ims_url: str, access_token: str, timeout: int=10) -> Iterable:

    """Query IMS for a list of images in JSON format"""

    headers = {"Authorization": "Bearer " + access_token}
    response = requests.get(ims_url, headers=headers, verify=False, timeout=timeout)
    response.raise_for_status()

    for i in json.loads(response.content):
        try:
            _ = i["link"]["path"]
        except (KeyError, TypeError):
            continue
        else:
            yield i