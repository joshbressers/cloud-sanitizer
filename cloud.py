#!/usr/bin/env python

"""
utility and library class for spawning VMs and testing stuff
"""

# OpenStack components
from novaclient.v1_1 import client
import glanceclient
import keystoneclient.v2_0.client

# other imports
from fabric.api import env, hide, get, execute, sudo

# standard imports
import time
import optparse
import logging
from os import environ
import sys
import traceback

# local imports
import config


def _get_identity_client():
    """
    used by glance stuff.
    """
    try:
        username = environ["OS_USERNAME"]
        password = environ["OS_PASSWORD"]
        tenant_name = environ["OS_TENANT_NAME"]
        auth_url = environ["OS_AUTH_URL"]
    except KeyError:
        traceback.print_exc()
        print "\n[?] did you 'source openrc.sh' ?"
        # this is fatal, so we exit
        sys.exit(-1)

    return keystoneclient.v2_0.client.Client(username=username,
            password=password,
            tenant_name=tenant_name,
            auth_url=auth_url, insecure=True)

def _get_image_client():
    keystone = _get_identity_client()
    token = keystone.auth_token
    endpoint = keystone.service_catalog.url_for(service_type='image',
            endpoint_type='publicURL')
    return glanceclient.Client('1', endpoint=endpoint, token=token)

def _sanitize(commands=None):
    if _sanitize.succeeded:
        return

    # XXX not the greatest idea
    if not commands:
        commands = config.commands
    else:
        print "Using Fedora commands"
        commands = config.fedora_commands

    print "[+]", "connecting to", env.host
    try:
        for command in commands:
            print "[#]", "running command", "'%s ...'" % \
                    command[0:16], "on", env.host
            with hide('output', 'running', 'stderr'):
                o = sudo(command, combine_stderr=False)
                print "[+]", "command '%s ...'" % command[0:16], \
                        "executed with return status", \
                        o.return_code
        # get output files
        get("*-ssg-results*", ".")
        _sanitize.succeeded = True
    except Exception, exc:
        print "[-]", exc

    print ""

_sanitize.succeeded = False

def test_image(name, image_id, key_name,
        output_path=".", username=None,
        commands=None, flavor=0, password=None):

    try:
        nt = client.Client(environ["OS_USERNAME"],
                environ["OS_PASSWORD"],
                environ["OS_TENANT_NAME"],
                environ["OS_AUTH_URL"])
    except KeyError:
        print "did you 'source openrc.sh' ?"
        return

    # logging configuration
    logging.basicConfig()
    logging.getLogger('ssh.transport').setLevel(logging.INFO)

    if config.DEBUG:
        LOG = logging.getLogger('glanceclient')
        LOG.addHandler(logging.StreamHandler())
        LOG.setLevel(logging.DEBUG)


    # glance client object
    gcnt = _get_image_client()

    # this sucks but works!
    gcnt.endpoint_path = ""

    # for i in gcnt.images.list():
    #    print i
    # return

    flavors = nt.flavors.list()
    # print flavors
    # [<Flavor: m1.tiny>, <Flavor: m1.small>, <Flavor: m1.medium>]

    # print nt.servers.list()
    print "[*] keypairs =>", nt.keypairs.list()

    # all_images = nt.images.list(detailed=True)

    # desired_image = filter(lambda x: x.id == config.our_image_id, all_images)
    # desired_image = desired_image[0]
    # print desired_image
    # print dir(desired_image)
    sm = nt.servers

    # flavors[1] ==> m1.small, a safe choice in case of Fedora 19 images
    print "[+] machine types =>", flavors

    print "[^]", "creating and lauching VM ..."
    server = sm.create(name, image_id, flavors[flavor], key_name=key_name)
    sid = server.id

    # only for testing
    # sid = config.HOST_ID

    # poll the server
    while True:
        ns = sm.get(sid)
        print "[*]", "server status is", ns.status, "and ID is", ns.id
        if ns.status.upper() == "ACTIVE":
            break
        time.sleep(7)

    print "[*]", "server addresses", ns.networks
    env.warn_only = True
    env.disable_known_hosts = True  # XXX dangerous?

    if username:
        env.user = username
    else:
        env.user = config.VM_USERNAME

    if password:
        env.password = password

    print "Using VM user", env.user

    # FIXME select a single public IP
    env.hosts = ns.networks["default"]

    while not _sanitize.succeeded:
        execute(_sanitize, commands)

    # reset state of _sanitize function
    _sanitize.succeeded = False


def main():
    """
    utility module purely intended for testing purposes
    """
    parser = optparse.OptionParser()
    parser.add_option('-n', action="store",
            dest="name", default="dummy",
            help="user specified VM identifier")
    parser.add_option('-i', action="store",
            dest="image_id", default=config.IMAGE_ID,
            help="image ID")
    parser.add_option('-k', action="store",
            dest="key_name", default="test",
            help="key name")
    parser.add_option('-f', action="store",
            dest="flavor", default=0,
            help="0 / 1 / 2 ==> tiny / small / medium")
    parser.add_option('-u', action="store",
            dest="username", default=None,
            help="username for the Guest OS, use 'fedora' for Fedora images")
    parser.add_option('-p', action="store",
            dest="password", default=None,
            help="password for the Guest OS")
    parser.add_option('-c', action="store",
            dest="commands", default=None,
            help="which command set to user, say 'fedora' for Fedora, \
                      RHEL is default")

    options, _ = parser.parse_args()

    if len(sys.argv) < 2:
        parser.print_help()
        return

    assert(options.image_id)
    assert(options.key_name)

    test_image(options.name, options.image_id,
            options.key_name,
            username=options.username,
            commands=options.commands,
            flavor=options.flavor)

if __name__ == "__main__":
    main()
