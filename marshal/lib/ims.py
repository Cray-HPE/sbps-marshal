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

import json
import requests

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

# IMS Manifest Example
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

def images(ims_url: str, access_token: str, timeout: int=10) -> list:

    ## TODO: Update to use Spire token, add auth lib
    
    '''access_token = None
    with open("/root/.config/cray/tokens/api_gw_service_nmn_local.vers", "r") as f:
        access_token = json.load(f)['access_token']'''

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