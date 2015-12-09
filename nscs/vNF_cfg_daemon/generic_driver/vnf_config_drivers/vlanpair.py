# Vlan Pair Configuration Manager/Driver

# (note) The File must be named " 'v'lanpair.py " and the Class must be
# named as " 'V'lanpair() ". Look into the [0] character of the file and
# class names.

import os

class Vlanpair():
    """
    Vlan Pair configuration Manager/driver. 
    
    Requires, get_vnf_name and handle_vnf_config functions
    to handle and process the configuration.
    """ 

    def __init__(self):
       print "Loading vlan pair config..... done"

    def get_vnf_name(self):
        """
        Define the 'slug' parameter name for use in loading the vnf drivers.
        """
        return "vlanpair"

    def _execute(self, cmd):
        os.system(cmd)

    def handle_vnf_config(self, request_dict):
        """
        Process Vlan pair configuration.
        """
        self.vlanin = self.request_dict['vlanin']
        self.vlanout = self.request_dict['vlanout']
        self._execute("modprobe 8021q")
        self._execute("vconfig add eth0 "+str(self.vlanin)+" INGRESS")
        self._execute("vconfig add eth0 "+str(self.vlanout)+" EGRESS")
        self._execute("ifconfig eth0."+str(self.vlanin)+" promisc up")
        self._execute("ifconfig eth0."+str(self.vlanout)+" promisc up")
        self._execute("brctl addbr br0")
        self._execute("brctl addif br0 eth0."+str(self.vlanin))
        self._execute("brctl addif br0 eth0."+str(self.vlanout))
        self._execute("ifconfig br0 up")
        
