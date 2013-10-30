# FIXME this needs to be dynamic
IMAGE_ID = "624b5bbd-7735-42e1-95ed-0efee89cdfc4"

DEBUG = True
DEBUG = False

# for testing
# HOST_ID  = "ad6881e7-8dd8-42af-aee3-9ed9db137a7b"

VM_USERNAME = "cloud-user"

commands = [
            "wget -O /etc/yum.repos.d/epel-6-scap-security-guide.repo \
                http://repos.fedorapeople.org/repos/scap-security-guide/epel-6-scap-security-guide.repo",

            "wget -O /etc/yum.repos.d/epel-6-openscap.repo \
                http://repos.fedorapeople.org/repos/gitopenscap/openscap/epel-6-openscap.repo",

            "yum install scap-security-guide -y",

            "oscap xccdf eval --profile stig-rhel6-server \
                --results `hostname`-ssg-results.xml \
                --report `hostname`-ssg-results.html \
                --cpe /usr/share/xml/scap/ssg/content/ssg-rhel6-cpe-dictionary.xml \
                /usr/share/xml/scap/ssg/content/ssg-rhel6-xccdf.xml"
            ]


# 1GB+ RAM is required to oscap on Fedora 19
# Do not install the openscap-selinux package!
# https://bugzilla.redhat.com/show_bug.cgi?id=983042

fedora_commands = [

            "yum update -y",

            "yum install openscap-content openscap-content-sectool openscap-extra-probes openscap \
                openscap-utils openscap-python -y",

            "rpm -e openscap-selinux &> /dev/null", # hack to get oscap running"

            "oscap xccdf eval --profile F14-Default \
                --results `hostname`-ssg-results.xml \
                --report `hostname`-ssg-results.html \
                --cpe /usr/share/openscap/cpe/openscap-cpe-dict.xml \
                /usr/share/openscap/scap-xccdf.xml"
            ]
