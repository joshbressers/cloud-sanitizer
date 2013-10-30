#!/usr/bin/env python

"""
library and utility for uploading images (using location rather than data) to
OpenStack Glance.
"""

# http://docs.openstack.org/trunk/openstack-compute/admin/content/starting-images.html

# OpenStack components
from novaclient.v1_1 import client
import glanceclient
import keystoneclient.v2_0.client
from cloud import _get_identity_client, _get_image_client

# other imports
from fabric.api import env, hide, run, get, execute, sudo

# standard imports
import time
import optparse
import logging
from os import environ
import sys

# local imports
import config


def upload_image(name, url, disk_format="qcow2", container_format="bare"):
    if config.DEBUG:
        LOG = logging.getLogger('glanceclient')
        LOG.addHandler(logging.StreamHandler())
        LOG.setLevel(logging.DEBUG)

    # glance client object
    gcobj = _get_image_client()

    # sometimes the server sends "publicURL" value which contains
    # trailing "/v1" and glance doesn't like that.
    # the follwing fix sucks but works!
    gcobj.endpoint_path = ""

    # images = set(gcobj.images.list())
    # for image in images:
    #    print image

    # print(dir(gcobj))
    # print(dir(gcobj.images))

    ret = gcobj.images.create(location=url,
            name=name,
            is_public=False,
            container_format=container_format,
            disk_format=disk_format)

    # poll the server
    while True:
        uret = gcobj.images.get(ret.id)
        status  = uret.status
        print "[*]", "image status is", status, "and ID is", uret.id
        if status.upper() == "ACTIVE":
            print "[+]", "image", name, "uploaded with ID", uret.id
            # print ret
            break
        time.sleep(7)

    return

def main():
    """
    utility module purely intended for testing purposes
    """
    parser = optparse.OptionParser()
    parser.add_option('-n', action="store",
            dest="name", default="dummy",
            help="user specified image identifier")
    parser.add_option('-l', action="store",
            dest="location", help="URL of the image")
    parser.add_option('-d', action="store",
            dest="disk_format", default="qcow2",
            help="qcow2 / vdi / vmdk / /vhd / iso / ami / raw")
    parser.add_option('-c', action="store",
            dest="container_format", default="bare",
            help="bare / ovf")
    parser.add_option('-t', action="store_true",
            dest="test", default=False,
            help="test stuff")

    options, remainder = parser.parse_args()

    if len(sys.argv) < 2:
        parser.print_help()
        return

    if options.test:
        url = "https://launchpad.net/cirros/trunk/0.3.0/+download/cirros-0.3.0-x86_64-disk.img"
        if options.location:
            url = options.location
        upload_image(options.name, url)
    else:
        upload_image(options.name, options.location, options.disk_format, options.container_format)

if __name__ == "__main__":
    main()


