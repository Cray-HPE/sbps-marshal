#
#  MIT License
#
#  (C) Copyright 2023-2024 Hewlett Packard Enterprise Development LP
#
#  Permission is hereby granted, free of charge, to any person obtaining a
#  copy of this software and associated documentation files (the 'Software'),
#  to deal in the Software without restriction, including without limitation
#  the rights to use, copy, modify, merge, publish, distribute, sublicense,
#  and/or sell copies of the Software, and to permit persons to whom the
#  Software is furnished to do so, subject to the following conditions:
#
#  The above copyright notice and this permission notice shall be included
#  in all copies or substantial portions of the Software.
#
#  THE SOFTWARE IS PROVIDED 'AS IS', WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
#  IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
#  FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL
#  THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR
#  OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE,
#  ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR
#  OTHER DEALINGS IN THE SOFTWARE.
#

"""Simple configuration module that allows environment overrides"""

import os


KV = dict()
_env_prefix = 'SBPS_MARSHAL_'

# How often the agent should sleep between scans for projection changes (seconds)

if os.environ.get(_env_prefix + 'SCAN_FREQUENCY') is not None:
    KV['SCAN_FREQUENCY'] = int(os.environ.get(_env_prefix + 'SCAN_FREQUENCY')) 
else:
    KV['SCAN_FREQUENCY'] = 180 

# API gateway to use for IMS requests

if os.environ.get(_env_prefix + 'API_GATEWAY') is not None:
    KV['API_GATEWAY'] = os.environ.get(_env_prefix + 'API_GATEWAY')
else:
    KV['API_GATEWAY'] = 'https://api-gw-service-nmn.local'

# IMS application endpoint to use for IMS requests

if os.environ.get(_env_prefix + 'IMS_URI') is not None:
    KV['IMS_URI'] = os.environ.get(_env_prefix + 'IMS_URI')
else:
    KV['IMS_URI'] = 'apis/ims/v3/images'

# Toggle to use IMS image tagging or not

if os.environ.get(_env_prefix + 'IMS_TAGGING') is not None:
    if KV['IMS_TAGGING'] == "true":
        KV['IMS_TAGGING'] = True
    else:
        KV['IMS_TAGGING'] = False
else:
    KV['IMS_TAGGING'] = False

# IMS request timeout to use (seconds)

if os.environ.get(_env_prefix + 'IMS_TIMEOUT') is not None:
    KV['IMS_TIMEOUT'] = int(os.environ.get(_env_prefix + 'IMS_TIMEOUT'))
else:
    KV['IMS_TIMEOUT'] = 10

# S3 host to use for S3 requests

if os.environ.get(_env_prefix + 'S3_HOST') is not None:
    KV['S3_HOST'] = os.environ.get(_env_prefix + 'S3_HOST')
else:
    KV['S3_HOST'] = 'rgw-vip.nmn'

# The S3 protocol to use for S3 requests

if os.environ.get(_env_prefix + 'S3_PROTO') is not None:
    KV['S3_PROTO'] = os.environ.get(_env_prefix + 'S3_PROTO')
else:
    KV['S3_PROTO'] = 'https'

# File that contains S3 credentials

if os.environ.get(_env_prefix + 'S3_CREDENTIAL_FILE') is not None:
    KV['S3_CREDENTIAL_FILE'] = os.environ.get(_env_prefix + 'S3_CREDENTIAL_FILE')
else:
    KV['S3_CREDENTIAL_FILE'] = '/root/.iscsi-sbps.s3fs'

# S3 bucket to use to verify Squashfs images
    
if os.environ.get(_env_prefix + 'S3_BUCKET') is not None:
    KV['S3_BUCKET'] = os.environ.get(_env_prefix + 'S3_BUCKET')
else:
    KV['S3_BUCKET'] = 'boot-images'

# Location of the Squashfs S3FS mount path
    
if os.environ.get(_env_prefix + 'SQUASHFS_S3FS_MOUNT') is not None:
    KV['SQUASHFS_S3FS_MOUNT'] = os.environ.get(_env_prefix + 'SQUASHFS_S3FS_MOUNT')
else:
    KV['SQUASHFS_S3FS_MOUNT'] = '/var/lib/cps-local/boot-images'

# Location of the Spire Agent executable path to use

if os.environ.get(_env_prefix + 'SPIRE_AGENT_PATH') is not None:
    KV['SPIRE_AGENT_PATH'] = os.environ.get(_env_prefix + 'SPIRE_AGENT_PATH')
else:
    KV['SPIRE_AGENT_PATH'] = '/usr/bin/sbps-marshal-spire-agent'

# The Spire JWT Audience to use

if os.environ.get(_env_prefix + 'SPIRE_JWT_AUDIENCE') is not None:
    KV['SPIRE_JWT_AUDIENCE'] = os.environ.get(_env_prefix + 'SPIRE_JWT_AUDIENCE')
else:
    KV['SPIRE_JWT_AUDIENCE'] = 'system-compute'

# The Spire agent socket path to use

if os.environ.get(_env_prefix + 'SPIRE_AGENT_SOCK_PATH') is not None:
    KV['SPIRE_AGENT_SOCK_PATH'] = os.environ.get(_env_prefix + 'SPIRE_AGENT_SOCK_PATH')
else:
    KV['SPIRE_AGENT_SOCK_PATH'] = '/var/lib/spire/agent.sock' 

# The LIO saveconfig file to update

if os.environ.get(_env_prefix + 'LIO_SAVE_FILE') is not None:
    KV['LIO_SAVE_FILE'] = os.environ.get(_env_prefix + 'LIO_SAVE_FILE')
else:
    KV['LIO_SAVE_FILE'] = '/etc/target/saveconfig.json'

# Path to the LIO targetcli executable

if os.environ.get(_env_prefix + 'TARGETCLI_BIN') is not None:
    KV['TARGETCLI_BIN'] = os.environ.get(_env_prefix + 'TARGETCLI_BIN')
else:
    KV['TARGETCLI_BIN'] = '/usr/bin/targetcli'
