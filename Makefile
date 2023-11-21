#
# MIT License
#
# (C) Copyright 2023 Hewlett Packard Enterprise Development LP
#
# Permission is hereby granted, free of charge, to any person obtaining a
# copy of this software and associated documentation files (the "Software"),
# to deal in the Software without restriction, including without limitation
# the rights to use, copy, modify, merge, publish, distribute, sublicense,
# and/or sell copies of the Software, and to permit persons to whom the
# Software is furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included
# in all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL
# THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR
# OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE,
# ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR
# OTHER DEALINGS IN THE SOFTWARE.
#
NAME ?= sbps-marshal
VERSION ?= $(shell ./version.sh)
RELEASE ?= 1
ARCH ?= noarch
NAME_VERSION_RELEASE ?= $(NAME)-$(VERSION)-$(RELEASE)
BUILD_DIR ?= dist/rpmbuild
PYTHON_VERSION ?= 3.10

.PHONY: all
all: rpm

.PHONY: rpm-local
rpm-local:
	mkdir -p $(BUILD_DIR)/SPECS $(BUILD_DIR)/SOURCES
	cat $(NAME).spec | \
		sed -e "s/@NAME@/$(NAME)/g" | \
		sed -e "s/@VERSION@/$(VERSION)/g" | \
		sed -e "s/@RELEASE@/$(RELEASE)/g" | \
		sed -e "s/@ARCH@/$(ARCH)/g" \
		> $(BUILD_DIR)/SPECS/$(NAME).spec
	zypper install -y python3-pip python3-wheel
	pip3 download --python-version $(PYTHON_VERSION) --platform linux/amd64 --only-binary=:all: -d $(BUILD_DIR)/wheels -r ./requirements.txt
	pip3 wheel . -w $(BUILD_DIR)/wheels
	tar -cvjf $(BUILD_DIR)/SOURCES/$(NAME_VERSION_RELEASE).tar.bz2 \
		--transform 'flags=r;s,^$(BUILD_DIR)/,$(NAME_VERSION_RELEASE)/,' \
		--transform 'flags=r;s,^\./,$(NAME_VERSION_RELEASE)/,' \
		./etc \
		$(BUILD_DIR)/wheels \
		./LICENSE
	rpmbuild -bb $(BUILD_DIR)/SPECS/$(NAME).spec --define "_topdir $(abspath $(BUILD_DIR))"
	chown -R $${HOST_UID}:$${HOST_GID} $(BUILD_DIR)

.PHONY: rpm
rpm: $(BUILD_DIR)/RPMS/$(ARCH)/$(NAME_VERSION_RELEASE).$(ARCH).rpm

$(BUILD_DIR)/RPMS/$(ARCH)/$(NAME_VERSION_RELEASE).$(ARCH).rpm:
	docker run --rm \
	-e HOST_UID=$(shell id -u) \
	-e HOST_GID=$(shell id -g) \
	-v $(PWD):/work \
	--workdir /work \
	artifactory.algol60.net/csm-docker/stable/csm-docker-sle:15.5 \
	bash -c "git config --global --add safe.directory /work; make rpm-local"

.PHONY: clean
clean:
	rm -rf $(BUILD_DIR)
