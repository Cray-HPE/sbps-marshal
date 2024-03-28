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

import hashlib
import subprocess

import lib.config as config

VENDOR_LENGTH_BYTES=16
WWN_LENGTH_BYTES=32


def sha224_hexdigest(message: str) -> str:

    return hashlib.sha224(bytes(message.encode('utf-8'))).hexdigest()

# See https://github.com/open-iscsi/rtslib-fb/blob/c1378f28f7abce6f8993a43c34d5e287b092bb1e/rtslib/utils.py#L320
# We will generate based on the SHA224 hash digest

def generate_lun_wwn(message: str) -> str:

    return sha224_hexdigest(message)[0:WWN_LENGTH_BYTES-1]

def generate_lun_product(message: str) -> str:

    return sha224_hexdigest(message)[0:VENDOR_LENGTH_BYTES-1]

## TODO: replace generator typehint with generic iterable class

def extract_fileio_backstores(target_config: dict) -> list:

    for stor_obj in target_config["storage_objects"]:
        if stor_obj["plugin"] == "fileio":
            yield {
                "dev" : stor_obj["dev"],
                "name" : stor_obj["name"],
                "size" : stor_obj["size"],
                "wwn" : stor_obj["wwn"]
            }

## TODO: replace generator typehint with generic iterable class

def extract_fileio_target_luns(target_config: dict) -> list:
    
    ## TODO: add defensive code to guard against cases with multiple TPGS

    for stor_obj in target_config["targets"]:
        if stor_obj["fabric"] == "iscsi":
            tpg = stor_obj["tpgs"][0]
            for lun in tpg["luns"]:
                yield {
                    "index" : lun["index"],
                    "storage_object" : lun["storage_object"]
                }

def get_lio_target_iqm(target_config: dict) -> str:

    try:
        return target_config["targets"][0]["wwn"]
    except IndexError as err:
        return None

# targetcli: create name file_or_dev [size] [write_back] [sparse] [wwn]

def create_fileio_backstore(vendor: str, file_path: str, wwn: str):
    
    ctx = f"/backstores/fileio create {vendor} {file_path} 0 false true {wwn}"
    subprocess.run([config.KV['TARGETCLI_BIN'], ctx], check=True)

def create_lun(vendor: str, iqm: str):
    
    ctx = f"/iscsi/{iqm}/tpg1/luns create /backstores/fileio/{vendor}"
    subprocess.run([config.KV['TARGETCLI_BIN'], ctx], check=True)

# targetcli: delete name [save] 

def delete_fileio_backstore(vendor: str):
    
    ctx = f"/backstores/fileio delete {vendor}"
    subprocess.run([config.KV['TARGETCLI_BIN'], ctx], check=True)

def save_config():

    ctx = f"saveconfig"
    subprocess.run([config.KV['TARGETCLI_BIN'], ctx], check=True)