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

"""Module with LIO helpers"""

import hashlib
import subprocess
import logging

import lib.config as config

from _collections_abc import Iterable


# 'Constants' to support SCSI WWN manipulation
VENDOR_LENGTH_BYTES=16
WWN_LENGTH_BYTES=32

def sha224_hexdigest(message: str) -> str:

    """Return a SHA224 as a hexidecimal string"""

    return hashlib.sha224(bytes(message.encode('utf-8'))).hexdigest()

# See https://github.com/open-iscsi/rtslib-fb/blob/c1378f28f7abce6f8993a43c34d5e287b092bb1e/rtslib/utils.py#L320
# We will generate based on the SHA224 hash digest

def generate_lun_wwn(message: str) -> str:

    """Generate a LUN WWN based on a SHA224 digest"""

    return sha224_hexdigest(message)[0:WWN_LENGTH_BYTES-1]

def generate_lun_product(message: str) -> str:
    
    """Generate a LUN Product based a SHA224 digest"""

    return sha224_hexdigest(message)[0:VENDOR_LENGTH_BYTES-1]

def extract_fileio_backstores(target_config: dict) -> Iterable:


    """Return configured LIO backing stores from configuration file"""

    for stor_obj in target_config["storage_objects"]:
        if stor_obj["plugin"] == "fileio":
            yield {
                "dev" : stor_obj["dev"],
                "name" : stor_obj["name"],
                "size" : stor_obj["size"],
                "wwn" : stor_obj["wwn"]
            }

def extract_fileio_target_luns(target_config: dict) -> Iterable:

    """Return configured LIO LUNs from configuration file"""
    
    ## TODO: add defensive code to guard against cases with multiple TPGS

    for stor_obj in target_config["targets"]:
        if stor_obj["fabric"] == "iscsi":
            tpg = stor_obj["tpgs"][0]
            for lun in tpg["luns"]:
                yield {
                    "index" : lun["index"],
                    "storage_object" : lun["storage_object"]
                }

def get_lio_target_iqn(target_config: dict) -> str:

    """Return the servers configured WWN (IQN)"""

    try:
        return target_config["targets"][0]["wwn"]
    except IndexError as err:
        return None

# targetcli: create name file_or_dev [size] [write_back] [sparse] [wwn]

def create_fileio_backstore(vendor: str, file_path: str, wwn: str):
    
    """Try to create a fileio backstore using targetcli"""

    ctx = f"/backstores/fileio create {vendor} {file_path} 0 false true {wwn}"
    subprocess.run([config.KV['TARGETCLI_BIN'], ctx], check=True)

def create_lun(vendor: str, iqn: str):

    """Try to create a LUN using targetcli, backstore must already exist"""
    
    ctx = f"/iscsi/{iqn}/tpg1/luns create /backstores/fileio/{vendor}"
    subprocess.run([config.KV['TARGETCLI_BIN'], ctx], check=True)

# targetcli: delete name [save] 

def delete_fileio_backstore(product: str):
    
    """Try to delete a backstore using targetcli"""
    
    ctx = f"/backstores/fileio delete {product}"
    subprocess.run([config.KV['TARGETCLI_BIN'], ctx], check=True)

def save_config():
    
    """Try to save the targetcli configuration"""

    ctx = f"saveconfig"
    subprocess.run([config.KV['TARGETCLI_BIN'], ctx], check=True)

def fileio_size(product: str, size: int):
   
    if product["size"] == size:
        logging.info(f"Asha:lio: fileio_backstore size = {product["size"]} and s3_object size = {size}")
        found_backstore = True

    else:
        try:
            logging.info(f"Asha:lio: fileio_backstore size = {product["size"]} and s3_object size = {size}")
            #found_backstore = False
            delete_fileio_backstore(product["name"])
        except Exception as err:
            logging.error(
                f"Unable to remove LIO fileio backstore for {product["dev"]}, received -> {str(err)}")
        
        try:
            save_config()
        except Exception as err:
            logging.error(f"Unable to save LIO configuration, received -> {str(err)}")

    return found_backstore
