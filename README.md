# Scalable Boot Projection Service (SBPS) Marshal Agent

A relatively simple software agent that:

* Manages Cray Systems Management (CSM), Image Management Service (IMS) and S3 rootfs Squashfs image projections (read-only) via iSCSI (LIO)
* Manages Cray Systems Management (CSM) programming environment Squashfs image projections (read-only) via iSCSI
* Is designed to run on CSM Worker nodes
* Leverages Spire/SPIFFE for authentication and authorization
* Leverages direct calls via `targetcli` and cached LIO savefiles to update iSCSI LUN projections

You must use an external service management facility (e.g., systemd) to ensure that precisely one instance of the agent is running on a host. 

SBPS support is limited to the the projection of read-only LUNs in LIO, using filio backstores. 

## IMS and S3 API Requests

The agent is designed to only require read-only access to the IMS endpoint to list images, and read-only object and bucket (e.g., list) access to the backing S3 bucket. It also requires a local path to an s3fs mounted version of the backing s3 bucket, which it uses to create `fileio` backing store objects for `LIO` via `targetcli`.

Filtering via IMS image tagging is supported if the `IMS_TAGGING` configuration is set to `True`. Here it will look for an annotation with the key `sbps-project` and the string value `true`. If IMS image tagging is enabled, and this annotation does not exist, the image will not be projected. If it is currently projected, it will be removed from projection. 

## Using Environment Overrides

The `marhsal/lib/config.py` contains a `KV` dictionary that serves as a rudimentary configuration system for the agent. This module allows environment overrides, but does not sanity check the environment variable overrides. 

## LIO Integration

The agent uses a combination of the LIO/target configuration file, by default in `/etc/target/saveconfig.json` to passively read state and direct invocation of `targetcli` to actively set state (and then saving to the configuration file). There may be a better or more efficient method (e.g., via targetclid) to integrate. 

## Local build
Requirements:
* GNU `make`
* Docker CLI installed and authenticated against `artifactory.algol60.net`:

Invoke default `make` target to build RPM package:

    make clean rpm

Resulting RPM file will be under `dist/rpmbuild/RPMS/`.

## Build and Release
Development versions are built automatically on push of regular commit to a branch, and published under [csm-rpms/unstable](https://artifactory.algol60.net/artifactory/csm-rpms/hpe/unstable/noos/sbps-marshal/). A tag, named as `vX.Y.Z` is considered a release, and signed RPM is published to [csm-rpms/stable](https://artifactory.algol60.net/artifactory/csm-rpms/hpe/stable/noos/sbps-marshal/).