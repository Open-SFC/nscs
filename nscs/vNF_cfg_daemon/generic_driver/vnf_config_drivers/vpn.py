# VPN vNF Configuration Manager/Driver

# (note) The File must be named " 'v'pn.py " and the Class must be
# named as " 'V'pn() ". Look into the [0] character of the file and
# class names.

import os

class Vpn():
    """
    VPN vNF configuration Manager/driver. 
    
    Requires, get_vnf_name and handle_vnf_config functions
    to handle and process the configuration.
    """

    def __init__(self):
       self.client_api = 'generate_vpn_config'
       print "Loading VPN vNF ..... done"

    def get_vnf_name(self):
        """
        Define the 'slug' parameter name for use in loading the vnf drivers.
        """
        return "vpn"

    def handle_vnf_config(self,request_dict):
        """
        Handles update of VPN Configuration
        and Requests from Compute node.
        """
        json_data = ''
        print "[LOG] Received request type: ", request_dict['header']
        if request_dict['header'] == 'request':
            print "[LOG] Processing 'Request' header"
            request_dict['response'] = "SUCCESS"
            json_data = self._prepare_vpn_response(request_dict)
        elif request_dict['header'] == 'data':
            print "[LOG] Processing 'Data' Header"
            self._handle_vpn_request_data(request_dict)
        print "Data framed %s.....\n" % str(json_data)
        return json_data

    def _handle_vpn_request_data(self,request_dict):
        """
        Handles 'data' header and prepares the 
        response json.
        """
        response = request_dict['response']

        print "Data From CRD Server %s.....\n" % str(response)
        json_data = ''
        ipsec_conf = '/etc/ipsec.conf'
        strongswan_conf = '/etc/strongswan.conf'
        ipsec_secrets = '/etc/ipsec.secrets'
        os.system("ipsec stop")
        self._write_file(ipsec_conf,response['ipsec.conf'])
        #self._write_file(strongswan_conf,response['strongswan.conf'])
        self._write_file(ipsec_secrets,response['ipsec.secrets'])
        os.system("ipsec start")

    def _prepare_vpn_response(self,request):
        """
        Prepare the JSON formatted Response data.
        """
        data = {"header":"response",
                "config_handle_id":request['config_handle_id'],
                "slug":request['slug'],
                "version":"0.0",
                "response":request['response'],
               }
        return {"method":request['client_api'],'kwargs':{'body':{'config':data}}}

    def _write_file(self,path,data):
        """
        writes the file in the specified location
        """
        with open(path,"w") as fd:
            fd.write(data)
            fd.close()
