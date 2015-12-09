# Loadbalancer vNF Configuration Manager/Driver

# (note) The File must be named " 'l'oadbalancer.py " and the Class must be
# named as " 'L'oadbalancer() ". Look into the [0] character of the file and
# class names.

import os

class Loadbalancer():
    """
    Loadbalancer vNF configuration Manager/driver. 
    
    Requires, get_vnf_name and handle_vnf_config functions
    to handle and process the configuration.
    """

    def __init__(self):
        self.tmp_path ="/tmp/haproxy.cfg"
        self.haproxy_cfg_path ="/etc/haproxy/haproxy.cfg"
        self.client_api = 'generate_slb_config'
        print "Loading Loadbalancer vNF.....done"

    def get_vnf_name(self):
        """
        Define the 'slug' parameter name for use in loading the vnf drivers.
        """
        return "loadbalancer"

    def handle_vnf_config(self, request_dict):
        """
        Handles update of HA-Proxy Configuration
        and Requests from Compute node.
        """
        json_data = ''
        request_dict['client_api'] = self.client_api
        print "[LOG] Received request type: ", request_dict['header']
        if request_dict['header'] == 'request':
            print "[LOG] Processing 'Request' header"
            request_dict['response'] = "SUCCESS"
            json_data = self._prepare_slb_response(request_dict)
        elif request_dict['header'] == 'data':
            print "[LOG] Processing 'Data' Header"
            self._handle_slb_request_data(request_dict)
        print "Data framed %s.....\n" % str(json_data)
        return json_data

    def _handle_slb_request_data(self,request_dict):
        """
        Handles 'data' header and prepares the 
        response json.
        """
        json_data = ''
        self._write_file(self.tmp_path,request_dict['response'])
        print "[LOG] Checking the haproxy configuration "
        p = subprocess.Popen(['haproxy','-c','-f',self.tmp_path],
                                                     stdout=subprocess.PIPE,
                                                     stderr=subprocess.PIPE)
        output,error = p.communicate()
        print "output = %s , error = %s\n\n" % (str(output),str(error))
        if error.find('error') == -1:
           print "[LOG] Haproxy Config OK, Restarting HAPROXY service."
           self._write_file(self.haproxy_cfg_path,request_dict['response'])
           request_dict['response'] = 'SUCCESS'
           os.system("killall -9 haproxy")
           os.system("haproxy -f /etc/haproxy/haproxy.cfg")
        else:
           print "[LOG] Invalid HAProxy Config. "
           request_dict['response'] = 'FAILED'
           json_data = self._prepare_slb_response(request_dict)

    def _prepare_slb_response(self,request):
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
