cloud-sanitizer
===============

The goal of *cloud-sanitizer* project is to ensure that the cloud images, which
are being delivered to the users, meet certain security and quality standards.

*cloud-sanitizer* automagically deploys and tests cloud images as soon as they
are available on Koji. The cloud images are tested using the existing OpenStack
infrastructure.

Motivation
==========

The Red Hat Enterprise Linux 6.4 KVM Guest Image for cloud instances had an
empty root password by default. See http://rhn.redhat.com/errata/RHSA-2013-0849.html
for more details.

We need to detect such problems before shipping.

Installation on Fedora
======================

1) Install the various OpenStack client libraries ::

     sudo yum install python-novaclient python-cinderclient python-glanceclient \
         python-keystoneclient python-quantumclient python-swiftclient -y

2) Install ssh libraries for Python ::

     sudo yum install fabric python-paramiko -y

3) If you are planning to host cloud-sanitizer server, install the following
   packages ::

     sudo yum install python-celery python-flask python-pymongo \
        mongodb-server koji -y

Configuration
=============

1. Most of the settings used by cloud-sanitizer are already there in your
   "openrc.sh" file. To download "openrc.sh" from your OpenStack dashboard ::

    1. Select "Settings" option in the dashboard

    2. Select "OpenStack API" option

    3. Select "Download RC" File option

2. *Create / Import Keypair* and activate it for your shell session ::

    1. Select "Access & Security" option in the dashboard

    2. Select "Keypairs" option

    3. Select "Create Keypair" / "Import Keypair" option

   Download and activate this keypair on your local machine ::

    ssh-add ssh-add ~/Downloads/test.pem

   Please *ensure* that your can connect to your instances using this keypair.

3. For rest of the settings, see config.py file.

Usage (semi-automatic)
======================

To test the cloud images on *OpenStack*, use the following steps

1. Source the OpenStack settings into your shell session ::

      source openrc.sh

2. *Create Image*. This can be done using the standard *glance* command or by
   using the *images.py* utility ::

      $ python images.py -n test_image -l http://<url>/rhel-server-x86_64-kvm-6.4_20130130.0-4.qcow2

      [*] image status is active and ID is a57c71b8-45cc-4109-8840-b4d92d5b63f6
      [+] image test_image uploaded with ID a57c71b8-45cc-4109-8840-b4d92d5b63f6

   Note down the ID of the image created.

3. *Launch Instance* + run automated tests. This can be done using the standard
   *nova* command or by using the *cloud.py* utility ::

      $ python cloud.py -n my_vm_name -i 'a57c71b8-45cc-4109-8840-b4d92d5b63f6' -k my_key_name

      [^] creating and lauching VM ...
      [*] server status is BUILD and ID is 7150800c-746d-49bc-a8e2-010d151a9024
      [*] server status is BUILD and ID is 7150800c-746d-49bc-a8e2-010d151a9024
      [*] server status is ACTIVE and ID is 7150800c-746d-49bc-a8e2-010d151a9024
      [*] server addresses {u'default': [u'192.168.100.121', u'10.11.22.185']}[192.168.100.121]
      ...
      [10.11.22.185] Executing task '_sanitize'
      [+] connecting to 10.11.22.185
      [#] running command 'wget -O /etc/yum ...' on 10.11.22.185
      [+] command executed with return status 0
      [#] running command 'wget -O /etc/yum ...' on 10.11.22.185
      [+] command executed with return status 0
      [#] running command 'yum install scap ...' on 10.11.22.185
      [+] command executed with return status 0
      [#] running command 'oscap xccdf eval ...' on 10.11.22.185

      [10.11.22.185] download: my_vm_name-ssg-results.xml <- /tmp/my_vm_name-ssg-results.xml
      [10.11.22.185] download: my_vm_name-ssg-results.html <- /tmp/my_vm_name-ssg-results.html

   **my_vm_name-ssg-results* files contain the security assessment results.**

   For testing Fedora images, run something like ::

      python cloud.py -n F19 -i '836a7a84-ffb7-4b96-b970-da879d3d3c6c' -k \
                my_keypair_name -u fedora -c fedora
