#!/usr/bin/env bash

set -e

# echo 'example,tag1=a,tag2=b i=42i,j=43i,k=44i'

if [[ -d "/hostfs" ]]; then
  source /hostfs/etc/lsb-release
  KERNEL_VERSION=$(cat /hostfs/proc/version_signature)
else
  source /etc/lsb-release
  KERNEL_VERSION=$(cat /proc/version_signature )
fi

DIST_DESC=$(echo "${DISTRIB_DESCRIPTION}" | tr ' ' '_' | tr '[:upper:]' '[:lower:]')
KERNEL=$(echo "${KERNEL_VERSION}" | tr ' ' '_' | tr '[:upper:]' '[:lower:]')

echo -n "lsb_dist_counter,dist_desc=${DIST_DESC},kernel=${KERNEL} host_counter=1"
