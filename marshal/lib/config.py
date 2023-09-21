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

## TODO: Allow overrides from ENV

KV = dict()

KV['API_GATEWAY'] = "https://api-gw-service-nmn.local"
KV['IMS_URI'] = "apis/ims/v3/images"
KV['S3_HOST'] = "rgw-vip.nmn"
KV['S3_PROTO'] = "https"
KV['S3_CREDENTIAL_FILE'] = "/root/.ims.s3fs"
KV['S3_BUCKET'] = "boot-images"
KV['LIO_SAVE_FILE'] = "/etc/target/saveconfig.json"
KV['SQUASHFS_S3FS_MOUNT'] = "/var/lib/cps-local/boot-images"
KV['SPIRE_AGENT_PATH'] = "/usr/bin/sbps-marshal-spire-agent"
KV['SPIRE_JWT_AUDIENCES'] = "system-compute"
KV['SPIRE_AGENT_SOCK_PATH'] = "/var/lib/spire/agent.sock" 
KV['SCAN_FREQUENCY'] = 180 
KV['IMS_TIMEOUT'] = 10
KV['TARGETCLI_BIN'] = "/usr/bin/targetcli"
