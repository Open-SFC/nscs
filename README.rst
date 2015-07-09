NSCS
==========
#
#
#Loading Network Service Configuration Stack and its Applications on OpenStack Controller:
#
#


1) Run 'python setup.py install' command from the git check out directory of NSCS.

2) Download 'OpenStack/CNS' Repository and run Run 'python setup.py install' command from the git check out directory of CNS.

3) Configure rabbit host server IP by changing the below field in /usr/local/etc/crd/crd.conf:
#> rabbit_host = <OPENSTACK_CONTROLLER_IP>

4) Create 'crd' database:
#> mysql -u root -p<password>
mysql> create database crd;
mysql> grant all privileges on crd.* to 'crd'@'localhost' identified by '<password>';
mysql> grant all privileges on crd.* to 'crd'@'%' identified by '<password>';

5) Start CRD Server by running the following command:
#> crd-server --config-file /usr/local/etc/crd/crd.conf



#
#
#Loading Network Service Configuration Stack and its Applications on FSL - OpenFlow Controller:
#
#

1) Run 'python setup.py install' command from the git check out directory of NSCS.

2) Download CNS Repository and run Run 'python setup.py install' command from the git check out directory of CNS.

3) Configure rabbit host server IP by changing the below field in /usr/local/etc/nscsas/crd.conf:
#> rabbit_host = <OPENSTACK_CONTROLLER_IP>

4) Create 'nscsas' database:
#> mysql -u root -p<password>
mysql> create database nscsas;
mysql> grant all privileges on nscsas.* to 'nscsas'@'localhost' identified by '<password>';
mysql> grant all privileges on nscsas.* to 'nscsas'@'%' identified by '<password>';

5) Start NSCSAS by running the below command:
#> nscsas-api --config-file /usr/local/etc/nscsas/nscsas.conf

6) Start CRD Consumer by running the below command:
#> crd-consumer --config-file /usr/local/etc/nscsas/crd.conf --config-file /usr/local/etc/nscsas/consumer.conf


#
#
#Loading Relay Agent on OpenStack - vNF - Server Compute Nodes:
#
#
1) Run 'python setup.py install' command from the git check out directory of NSCS.
2) Configure rabbit host server IP by changing the below field in /usr/local/etc/crd/crd.conf:
#> rabbit_host = <OPENSTACK_CONTROLLER_IP>

3) Start CRD Relay Agent by running the below command:

#> crd-relay-agent --config-file /usr/local/etc/crd/crd.conf

4) Build Network Service Appliance vNF with the config daemon from the git check out directory 'vNF_cfg_daemon':

#
#
#Apply Nova patch
#
#
1) Check out the NSCS directory from git, to get the directory 'nova_patch', which have the nova patch file 'fsl_nova_icehouse_patch.patch'

2) Apply Nova patch as shown below:
   Go to the directory '/usr/lib/python2.7/dist-packages/nova':
    # cd /usr/lib/python2.7/dist-packages/nova

   Apply Patch:
    # patch -p1 < {NSCS_GIT_CHECKOUT_DIR}/fsl_nova_icehouse_patch.patch

