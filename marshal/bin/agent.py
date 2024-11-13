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

import argparse
import logging
import hashlib
import json
import os
import time
import urllib3
urllib3.disable_warnings()
import urllib.parse

import lib.config as config
import lib.auth as auth
import lib.s3 as s3
import lib.ims as ims
import lib.lio as lio
import subprocess


def main():

    parser = argparse.ArgumentParser()
    parser.add_argument('-d', '--debug', action='store_true')
    parser.add_argument('-q', '--quiet', action='store_true')
    args = parser.parse_args()

    log_format = "%(filename)s:%(funcName)s:%(lineno)s %(levelname)s %(asctime)s %(message)s"

    if args.debug:
            logging.basicConfig(
                format=log_format,
                datefmt="%Y-%m-%dT%H:%M:%S%z",
                level=logging.DEBUG)
    elif not args.quiet:
            logging.basicConfig(
                format=log_format,
                datefmt="%Y-%m-%dT%H:%M:%S%z",
                level=logging.INFO)

    for k,v in config.KV.items():
        logging.info(f"config K:{k}, V: {str(v)}")


    ## --------------------------------------------------------------
    ## Main Agent Loop
    ## --------------------------------------------------------------

    while True:

        logging.info("START SCAN")
        ## ----------------------------------------------------------
        ## Pre-flight for all types of image projection
        ## ----------------------------------------------------------        

        # Attempt to load S3 credentials from file, and then create a client

        try:
            s3_key_id, s3_access_key = auth.get_s3fs_creds(config.KV['S3_CREDENTIAL_FILE'])
        except Exception as err:
            logging.error(f"Unable to retrieve S3 credentials, received -> {str(err)}")
            time.sleep(config.KV['SCAN_FREQUENCY'])
            continue
        
        try:
            s3_host = config.KV['S3_PROTO'] + '://' + config.KV['S3_HOST']
            s3_client = s3.get_s3_client(s3_host, 
                                         s3_key_id, 
                                         s3_access_key)
        except Exception as err:
            logging.error(f"Unable to create S3 client, received -> {str(err)}")
            time.sleep(config.KV['SCAN_FREQUENCY'])
            continue

        # Attempt to query S3 objects from the configured bucket

        try:
            s3_objects = s3.list_bucket_objects(s3_client, config.KV['S3_BUCKET'])
        except Exception as err:
            logging.error(f"Unable to list S3 objects, received -> {str(err)}")
            time.sleep(config.KV['SCAN_FREQUENCY'])
            continue

        logging.info(f"Counted {len(s3_objects)} S3 objects in {config.KV['S3_BUCKET']} bucket.")

        # Load and process LIO targets and LUNs from the target
        # save configuration file (JSON)

        lio_save = None
        if os.path.isfile(config.KV['LIO_SAVE_FILE']):
            with open(config.KV['LIO_SAVE_FILE'], 'r') as f:
                lio_save = json.load(f)
        else:
            logging.error(f"LIO Save file does not exist at {config.KV['LIO_SAVE_FILE']}, aborting")
            time.sleep(config.KV['SCAN_FREQUENCY'])
            continue

        target_iqn = lio.get_lio_target_iqn(lio_save)
        if target_iqn is None:
            logging.error(f"Unable to get server target IQN from {config.KV['LIO_SAVE_FILE']}, aborting")
            time.sleep(config.KV['SCAN_FREQUENCY'])
            continue

        logging.info(f"Detected {target_iqn} as LIO server IQN")

        fileio_backstores = list(lio.extract_fileio_backstores(lio_save))
        logging.info(f"Counted {len(fileio_backstores)} LIO target fileio backstores")

        # Walk through fileio backstores, remove any that do not exist in S3FS
        # If we don't, attempting to add backstores may fail

        for fileio_backstore in fileio_backstores:

            if not os.path.exists(fileio_backstore["dev"]):

                try:
                    lio.delete_fileio_backstore(fileio_backstore["name"])
                except Exception as err:
                    logging.error(
                        f"Unable to remove LIO fileio backstore for {fileio_backstore['dev']}, received -> {str(err)}")            

                try:
                    lio.save_config()
                except Exception as err:
                    logging.error(f"Unable save LIO configuration, received -> {str(err)}")

        # Reload the fileio backstores and load LUN state after stale S3FS purge
                    
        fileio_backstores = list(lio.extract_fileio_backstores(lio_save))
        logging.info(f"Counted {len(fileio_backstores)} LIO target fileio backstores after stale S3FS purge")

        target_luns = list(lio.extract_fileio_target_luns(lio_save))
        logging.info(f"Counted {len(target_luns)} LIO target LUNs after stale S3FS purge")

        # Track the WWN products for all valid (new or existing) backstores projected
        # so we can attempt to clean them up after all projection modifications are 
        # complete
        valid_backstores = set()

        ## ----------------------------------------------------------
        ## Programming Environment Image Synchronization Logic
        ## ----------------------------------------------------------        

        pe_images = [ x for x in s3_objects if x['Key'].startswith("PE/") ]
        logging.info(f"Counted {len(pe_images)} S3, PE images in boot-images bucket. Starting PE image reconciliation.")

        for s3_object in pe_images:

            # Create an s3 normalized path to generate LIO device attributes (wwn, product)
            # e.g., s3://boot-images/PE/CPE-nvidia.x86_64-23.05.squashfs
            pe_s3_path = "s3://" + config.KV['S3_BUCKET'] + '/' + s3_object['Key']

            # Where does the object exist in s3fs (as locally mounted)
            pe_s3fs_path = os.path.join(config.KV['SQUASHFS_S3FS_MOUNT'], s3_object['Key'])        

            pe_product = lio.generate_lun_product(pe_s3_path)
            pe_wwn = lio.generate_lun_wwn(pe_s3_path)

            valid_backstores.add(pe_product)

            # Check LIO saveconfig data to see if the device exists

            # dev == the s3fs path for a fileio backstore
            # name == product
            # wwn == wwn

            found_backstore = False
            for fileio_backstore in fileio_backstores:
                if fileio_backstore["dev"] == pe_s3fs_path:
                    if fileio_backstore["name"] == pe_product:
                        if fileio_backstore["wwn"] == pe_wwn:
                            found_backstore = True

            if found_backstore:
                continue # backstore already exists, assume LUN does as well

            logging.info(f"ADD PE LIO fileio backstore: s3_path: {pe_s3fs_path}, s3fs_path: {pe_s3fs_path}, lun_wwn: {pe_wwn}, lun_product: [{pe_product}")

            try:
                lio.create_fileio_backstore(pe_product, pe_s3fs_path, pe_wwn)
            except Exception as err:
                logging.error(f"Unable to create PE LIO fileio backstore for {pe_s3fs_path}, received -> {str(err)}")

            try:
                lio.create_lun(pe_product, target_iqn)
            except Exception as err:
                logging.error(f"Unable to create PE LIO LUN for {pe_s3fs_path}, received -> {str(err)}")

            try:
                lio.save_config()
            except Exception as err:
                logging.error(f"Unable save to LIO configuration for PE, received -> {str(err)}")

        ## ----------------------------------------------------------
        ## Rootfs Image Synchronization Logic
        ## ----------------------------------------------------------

        # Attempt to query IMS API for its image inventory

        try:
            spire_jwt = auth.get_spire_svid_jwt() # use Spire Auth
        except Exception as err:
            logging.error(f"Unable to retrieve a spire token, received -> {str(err)}")
            time.sleep(config.KV['SCAN_FREQUENCY'])
            continue

        ims_url = urllib.parse.urljoin(config.KV['API_GATEWAY'], 
                                       config.KV['IMS_URI'])
        
        logging.info(f"Using IMS URL: {ims_url}")

        try:
            ims_images = list(ims.images(ims_url, 
                                         spire_jwt, 
                                         config.KV['IMS_TIMEOUT']))
            
        except Exception as err:
            logging.error(f"Unable to list IMS images, received -> {str(err)}")
            time.sleep(config.KV['SCAN_FREQUENCY'])
            continue     
        
        logging.info(f"Counted {len(ims_images)} IMS images. Starting rootfs image reconciliation.")
        for ims_image in ims_images:

            # Retrieve the IMS manifest for the image and verify required attributes

            try:
                # "s3://boot-images/1fb58f4e-ad23-489b-89b7-95868fca7ee6/manifest.json"
                m = ims_image["link"]["path"].replace("s3://" + config.KV['S3_BUCKET'] + "/", "")
                ims_image_id = m.split("/")[0]
                manifest = s3.get_s3_object(s3_client, config.KV['S3_BUCKET'], m)
                manifest = json.load(manifest)
            except Exception as err:
                logging.error(f"Unable to obtain manifest for IMS image {m}, received -> {str(err)}")
                continue

            # Attempt to retrieve the path and etag for the rootfs artifact cited
            # in the manifest. If unable to retrieve either, will be unable to project.

            rootfs_s3_path = None
            rootfs_s3_etag = None

            for artifact in manifest["artifacts"]:
                if artifact["type"] == "application/vnd.cray.image.rootfs.squashfs" and \
                    'link' in artifact and artifact['link'] is not None and \
                    'path' in artifact['link'] and 'etag' in artifact['link']:
                    # Expects a normalized s3 path for link->path, e.g., 
                    # s3://boot-images/00d18ed1-20a3-4df2-affb-a88fda00b6f6/rootfs
                    rootfs_s3_path = artifact["link"]["path"]
                    rootfs_s3_etag = artifact["link"]["etag"]

            if rootfs_s3_path is None or rootfs_s3_etag is None:
                logging.error(f"path or etag missing in IMS manifest -> {m}")
                continue
            
            if config.KV['IMS_TAGGING']:

                # Check to see if image is marked for projection
                # If the metadata key does not exist, we assume that the 
                # version of IMS in use doesn't support image tagging

                if 'metadata' in ims_image.keys():
                    if 'sbps-project' not in ims_image['metadata'].keys():
                        logging.info(f"No sbps-project key value, so image is not marked for projection")
                        continue
                    else:
                        try:
                            if ims_image['metadata']['sbps-project'] != "true":
                                logging.info(f"Image is not marked for projection in IMS {m}")
                                continue
                        except KeyError:
                            pass

            # Calculate WWN (input) and product name

            digest_data = rootfs_s3_path + "|" + rootfs_s3_etag
            rootfs_wwn = lio.generate_lun_wwn(digest_data)
            rootfs_product = lio.generate_lun_product(digest_data)

            # Verify that the image exists in s3

            ims_in_s3 = False
            for s3_object in s3_objects:
                k = rootfs_s3_path.replace("s3://" + config.KV['S3_BUCKET'] + "/", "")
                if s3_object['Key'] == k:
                    if s3_object["ETag"].replace('"','') == rootfs_s3_etag:
                        ims_in_s3 = True
                        break
            else:
                logging.info(f"Matching S3 object not found for {rootfs_s3_path} with etag {rootfs_s3_etag}")
                continue

            # Verify that the image exists in s3fs
            
            s3fs_path = os.path.join(config.KV['SQUASHFS_S3FS_MOUNT'], 
                                rootfs_s3_path.replace("s3://" + config.KV['S3_BUCKET'] + "/", ""))
            
            if not os.path.isfile(s3fs_path):
                logging.info(f"S3 object for rootfs not found in s3fs, path: {s3fs_path}")
                continue

            valid_backstores.add(rootfs_product)

            # Check LIO saveconfig data to see if the device exists
            # dev == s3fspath, name == product, wwn == wwn

            found_backstore = False
            for fileio_backstore in fileio_backstores:
                if fileio_backstore["dev"] == s3fs_path:
                    if fileio_backstore["name"] == rootfs_product:
                        if fileio_backstore["wwn"] ==rootfs_wwn:
                            found_backstore = True

            ## TODO: should we guard against other S3FS corner cases here, like transient cache state? 

            # If a backstore was not found for the rootfs image, add it and create a lun

            if not found_backstore:
                
                logging.info(f"ADD rootfs LIO fileio backstore: s3_path: {rootfs_s3_path}, s3_etag: {rootfs_s3_etag}, s3fs_path: {s3fs_path}, lun_wwn: {rootfs_wwn}, lun_product: {rootfs_product}")

                try:
                    lio.create_fileio_backstore(rootfs_product, s3fs_path, rootfs_wwn)
                except Exception as err:
                    logging.error(f"Unable to create LIO fileio backstore for {rootfs_s3_path}, received -> {str(err)}")

                try:
                    lio.create_lun(rootfs_product, target_iqn)
                except Exception as err:
                    logging.error(f"Unable to create LIO LUN for {rootfs_s3_path}, received -> {str(err)}")

                try:
                    lio.save_config()
                except Exception as err:
                    logging.error(f"Unable save LIO configuration, received -> {str(err)}")

        # If fileio backstores exist that we didn't scan as valid at this point, 
        # attempt to remove them
        for fileio_backstore in fileio_backstores:
            if fileio_backstore["name"] not in valid_backstores:

                logging.info(f"Attempting to remove fileio backstore {fileio_backstore} as it wasn't validated in this scan period")

                try:
                    lio.delete_fileio_backstore(fileio_backstore["name"])
                except Exception as err:
                    logging.error(f"Unable to remove LIO fileio backstore for {fileio_backstore['name']}, received -> {str(err)}")            

                try:
                    lio.save_config()
                except Exception as err:
                    logging.error(f"Unable to save LIO configuration, received -> {str(err)}")

        logging.info("END SCAN")
        time.sleep(config.KV['SCAN_FREQUENCY'])

if __name__ == "__main__":
    main()
