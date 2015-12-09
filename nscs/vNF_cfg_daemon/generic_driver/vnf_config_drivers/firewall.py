# Firewall vNF Configuration Manager/Driver

# (note) The File must be named " 'f'irewall.py " and the Class must be
# named as " 'F'irewall() ". Look into the [0] character of the file and
# class names.

class Firewall():
    """
    Firewall vNF configuration Manager/driver. 
    
    Requires, get_vnf_name and handle_vnf_config functions
    to handle and process the configuration.
    """ 

    def __init__(self):
       self.client_api = 'generate_firewall_config'
       print "Loading Firewall vNF..... done"

    def get_vnf_name(self):
        """
        Define the 'slug' parameter name for use in loading the vnf drivers.
        """
        return "firewall"

    def handle_vnf_config(self, request_dict):
        """
        Process Firewall vNF configuration.
        """
        json_data = ''
        request_dict['client_api'] = self.client_api
        print "[LOG] Received request type: ", request_dict['header']
        if request_dict['header'] == 'request':
            print "[LOG] Processing 'Request' header"
            request_dict['response'] = "SUCCESS"
            json_data = self._prepare_firewall_response(request_dict)
        elif request_dict['header'] == 'data':
            print "[LOG] Processing 'Data' Header"
            self._handle_firewall_request_data(request_dict)
        print "Data framed %s.....\n" % str(json_data)
        return json_data

    def _handle_firewall_request_data(self,request_dict):
        """
        Handles 'data' header and prepares the 
        response json.
        """
        json_data = ''
        os.system("iptables -F")

        response = request_dict['response']
        ##TODO Add firewall rules ---Veera
        print "Data From CRD Server %s.....\n" % str(response)
        for firewall in response:
            firewall_rule_list = firewall['firewall_rule_list']
            firewall_rule_list = sorted(firewall_rule_list, key=lambda k: k['position'])
            for rule in firewall_rule_list:
                protocol = rule['protocol']
                enabled = rule['enabled']
                source_port = rule['source_port']
                destination_port = rule['destination_port']
                source_ip_address = rule['source_ip_address']
                destination_ip_address = rule['destination_ip_address']
                action = rule['action']
                if enabled:
                    if protocol:
                        pass
                    else:
                        protocol = 'all'
                    rule = "iptables -A FORWARD -p "+protocol

                    if source_ip_address:
                        rule +=" -s "+source_ip_address
                    if destination_ip_address:
                        rule +=" -d "+destination_ip_address
                    if source_port:
                        rule +=" --sport "+source_port
                    if destination_port:
                        rule +=" --dport "+destination_port
                    if action == 'allow':
                        rule += " -j ACCEPT"
                    if action == 'deny':
                        rule += " -j REJECT"
                    print rule
                    os.system(rule)

    def _prepare_firewall_response(self,request):
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

        
