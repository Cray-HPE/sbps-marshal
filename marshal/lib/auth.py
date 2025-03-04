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

"""Simple authN and authZ client module"""

import json
import os
import subprocess
import logging
import lib.config as config

def get_s3fs_creds(file_path: str) -> tuple:

    """Read Key ID/Access Key style S3 creds from file"""

    if not os.path.isfile(file_path):
        raise FileNotFoundError(f"{file_path} does not exist or is not a file.")

    with open(file_path, 'r') as f:
        key_id, key = f.read().strip().split(':')
        return key_id, key
    
    raise ValueError("Unable to parse credentials")

def get_spire_svid_jwt() -> str:

    """Attempt to retrieve a Spire JWT for the SPBS agent workload and parse
    out the bearer token"""

    ctx = [ config.KV['SPIRE_AGENT_PATH'],
            "api",
            "fetch",
            "jwt",
            "-audience",
            config.KV['SPIRE_JWT_AUDIENCE'],
            "-socketPath",
            config.KV['SPIRE_AGENT_SOCK_PATH'],
            "-output",
            "json" ]
    
    p = subprocess.run(ctx, check=True, capture_output=True)

    entries = json.loads(p.stdout)

    file = open("/etc/cray/xname", "r")
    xname = file.read().rstrip() 
    file.close()

    for e in entries:
        if 'svids' in e.keys():
            for svid in e['svids']:
                if svid['spiffe_id'] == "spiffe://shasta/ncn/workload/sbps-marshal":
                    return svid['svid']
                if svid['spiffe_id'] == f"spiffe://shasta/ncn/{xname}/workload/sbps-marshal":
                    return svid['svid']
 
    raise ValueError("Could not find valid SVID")
