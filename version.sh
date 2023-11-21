#!/usr/bin/env bash
(git describe --tags || echo "v0.0.1") | sed -e "s/^v//" | tr "-" "~"
