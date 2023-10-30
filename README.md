# sbps-marshal
Agent to manage iSCSI projection via LIO based on Squashfs image inventories for scalable boot

## Local build
Requirements:
* GNU `make`
* Docker CLI installed and authenticated against `artifactory.algol60.net`:

Invoke default `make` target to build RPM package:

    make clean rpm

Resulting RPM file will be under `dist/rpmbuild/RPMS/`.

## Build and Release
Development versions are built automatically on push of regular commit to a branch, and published under [csm-rpms/unstable](https://artifactory.algol60.net/artifactory/csm-rpms/hpe/unstable/noos/sbps-marshal/). A tag, named as `vX.Y.Z` is considered a release, and signed RPM is published to [csm-rpms/stable](https://artifactory.algol60.net/artifactory/csm-rpms/hpe/stable/noos/sbps-marshal/).