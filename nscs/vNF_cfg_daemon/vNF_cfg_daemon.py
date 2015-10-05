#!/usr/bin/python
# SLB VM Configuration Daemon
import sys
import os
import subprocess
import threading
import fcntl
import ast
import time
import re

class VMConfigurationDaemon(object):
    """
    VMConfigurationDaemon class implements the SLB VM configuration routines 
    required for the updates to the configuration of the SLB.
    Here, HA-Proxy
    """
    def __init__(self):
        """
        Initializing the data required
        """
        self.response = ''
        self.tmp_path ="/tmp/haproxy.cfg"
        self.haproxy_cfg_path ="/etc/haproxy/haproxy.cfg"
	self.vbts_cfg_path ="/etc/lte_l2.conf"
	self.dpdk_cfg_path ="/etc/dpdk-iface.conf"
	self.setup_enb_path ="/home/root/start_l2.sh"
	self.cmd_str = 'curl http://169.254.169.254/openstack/latest/user_data'
	self.command = Command(self.cmd_str)
        
    def _handle_loadbalancer_config(self,request_dict):
        """
        Handles update of HA-Proxy Configuration
        and Resuests from Compute node.
        """
	json_data = ''
        self.client_api = 'generate_slb_config'
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

    
    
    #### For Firewall
    def _handle_firewall_config(self,request_dict):
        """
        Handles update of Firewall Configuration
        and Resuests from Compute node.
        """
	json_data = ''
        self.client_api = 'generate_firewall_config'
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
    
    
    
    #### For VPN
        
    def _handle_vpn_config(self,request_dict):
        """
        Handles update of VPN Configuration
        and Resuests from Compute node.
        """
	json_data = ''
        self.client_api = 'generate_vpn_config'
        request_dict['client_api'] = self.client_api
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
	
    #### VPN End
    
    
    
    
    #### For vBTS
    def _advertise_l2vm(self, request):
	"""
        Advertises L2VM Details
        """
	json_data = ''
	if request['header'] == 'request':
	    request_dict = {}
	    self.client_api = 'advertise_l2vm'
	    request_dict['client_api'] = self.client_api
	    print "[LOG] Processing 'Request' header"
	    request_dict['instance_id'] = request['instance_id']
	    output = None
	    ret_code = None
	#    p = subprocess.Popen(['curl http://169.254.169.254/openstack/latest/user_data'],
	#	stdout=subprocess.PIPE,
	#	shell=True)
	#    (output,error) = p.communicate()
	
	    #i=1
	    #while(i<=5):
	    (ret_code, output, err) = self.command.run(timeout=5)
		#if ret_code == 0:
		#    break
		#i=i+1
	    if ret_code == 0:
		location = output
	    else:
		location = 'default'
	    print "[LOG] Location:", location
	    
	    print "[LOG] Assigning IP Addresses in VM..."
	    interfaces = request['interfaces']
	    ports = {}
	    for dev, port in interfaces.iteritems():
		ipaddr = port['ipaddr']
		port_id = port['port_id']
		net_id = port['net_id']
		if dev == 'b9131':
		    ports.update({'b9131':{'port_id': port_id, 'net_id': net_id, 'ipaddr': ipaddr}})
		    cmd = ""
		    #cmd = "ifconfig eth0 " +str(ipaddr)+ "/24 up"
		elif dev == 'epc':
		    ports.update({'epc':{'port_id': port_id, 'net_id': net_id, 'ipaddr': ipaddr}})
		    cmd = "ifconfig eth0 " +str(ipaddr)+ "/24 up"
		print "ifconfig command: %s"% str(cmd)
		os.system(cmd)
	    
	    sample_config = {'tenant_id': request['tenant_id'],
			     'instance_id': request['instance_id'],
			     'ports': ports,
			     'header': 'response',
			     #"config_handle_id":request['config_handle_id'],
			     'slug': 'vbts',
			     'version': '0.0',
			     'response': 'SUCCESS',
			     'location': location}
	    request_dict.update(sample_config)
	    json_data = self._prepare_vbts_advertisement(request_dict)
	    print "Data framed %s.....\n" % str(json_data)
	elif request['header'] == 'data':
	    print "[LOG] Processing 'Data' header"
	    self._handle_vbts_data(request)
	elif request['header'] == 'dpdk':
	    print "[LOG] Processing 'DPDK' header"
	    self._handle_dpdk_data(request)
	elif request['header'] == 'sooktha':
	    print "[LOG] Starting Sooktha Stack in L2VM ..."
	    os.system("rm -f /tmp/setup_enb.log")
	    print "[LOG] Starting Sooktha Stack"
	    start_enb_cmd = 'nohup sh ' + str(self.setup_enb_path) + '> /tmp/enb.log 2>&1 &'
	    os.system(start_enb_cmd)
	    time.sleep(2)
	    i=1
	    state = False
	    while i<=100:
		with open('/tmp/setup_enb.log', 'r') as content_file:
		    content = content_file.read()
		
		print "[LOG] Content: %s" % str(content)
		if re.search('DPDK Initialization', content):
		    state = True
	    	    print "[LOG] Sooktha Stack Started."
		    break
		else:
		    time.sleep(1)
		i = i+1
	    if state:
		request_dict = {}
		request_dict['client_api'] = 'start_sooktha_epc'
		print "[LOG] Processing 'Request' to start Sooktha Stack in EPC Machine ..."
		request_dict['instance_id'] = request['instance_id']
		output = None
		ret_code = None
		(ret_code, output, err) = self.command.run(timeout=5)
		if ret_code == 0:
		    location = output
		else:
		    location = 'default'
		print "[LOG] Location:", location
		sample_config = {'tenant_id': request['tenant_id'],
			     'instance_id': request['instance_id'],
			     'header': 'response',
			     'slug': 'vbts',
			     'version': '0.0',
			     'response': 'SUCCESS',
			     'location': location}
		request_dict.update(sample_config)
		json_data = self._prepare_vbts_advertisement(request_dict)
		print "Data framed %s.....\n" % str(json_data)
	return json_data
    
    def _prepare_vbts_advertisement(self,request):
        """
        Prepare the JSON formatted L2 VM Advertisement data.
        """
        return {"method":request['client_api'],'kwargs':{'body':{'config':request}}}
    
    def _handle_vbts_data(self,request):
        """
        Applies JSON data to vbts configuration
        """
	response = request['response']
	print "vBTS eNodeb Configuration is: %s.....\n" % str(response)
	self._update_lte_enb_conf(payload=response['device_config'])
    
    def _handle_dpdk_data(self,request):
        """
        Applies JSON data to dpdk iface configuration
        """
	response = request['response']
	print "vBTS DPDK Configuration is: %s.....\n" % str(response)
	self._update_dpdk_conf(payload=response)

    def _update_lte_enb_conf(self, payload=None):
	print "Updating configuration file: %s...\n" % str(self.vbts_cfg_path)
	if payload:
	    f2 = open(self.vbts_cfg_path, 'w')
	    freq_band = payload['lte_rf_band']
	    nw_mode = payload['nw_mode']
	    cell_bandwidth = payload['cell_bandwidth']
	    cell_bandwidth = int(cell_bandwidth) * 5
	    f2.write("freq_band_indicator=" + str(freq_band) + "\n")
	    f2.write("dup_mode=LTE_" + str(nw_mode) + "\n")
	    f2.write("dl_bw_prb=" + str(cell_bandwidth) + "\n")
	    f2.close()

    def _update_dpdk_conf(self, payload=None):
	print "Updating DPDK configuration file: %s...\n" % str(self.dpdk_cfg_path)
	if payload:
	    f2 = open(self.dpdk_cfg_path, 'w')
	    src_mac_addr = payload['src_mac_addr']
	    dst_mac_addr = payload['dst_mac_addr']
	    src_ip_addr = payload['src_ip_addr']
	    dst_ip_addr = payload['dst_ip_addr']
	    
	    f2.write("src_mac_addr=" + str(src_mac_addr) + "\n")
	    f2.write("src_ip_addr=" + str(src_ip_addr) + "\n")
	    f2.write("dst_mac_addr=" + str(dst_mac_addr) + "\n")
	    f2.write("dst_ip_addr=" + str(dst_ip_addr) + "\n")
	    
	    f2.close()
    
    def _write_file(self,path,data):
        """
        writes the file in the specified location
        """
        with open(path,"w") as fd:
            fd.write(data)
            fd.close()

    def daemon_loop(self):
        """
        Loop to find the incoming config change requests
        and update and restart the SLB.
        """
	print "[LOG] Daemon starting up.. \r\n"
        while True:
            try:
                fd=open("/dev/virtio-ports/ns_port",'r+',False)
                fl = fcntl.fcntl(fd, fcntl.F_GETFL)
        	fcntl.fcntl(fd, fcntl.F_SETFL, fl | os.O_NONBLOCK)
	        print "[LOG] sending Hello Message \r\n"
                fd.write("{'method':'hello','msg':'Config Daemon is UP'}")
        	time.sleep(1)
		while True:
	                try:
    	                     self.recv = ast.literal_eval(fd.read())
          	             print "[LOG] Received Request: ", self.recv	
    	                     self.request_dict = self.recv['config']	
              	             print "[LOG] Received Request: ", self.request_dict
			     if self.request_dict:
				if self.request_dict['slug'] == 'loadbalancer':
				    print "Loadbalancer"
				    self.response = self._handle_loadbalancer_config(self.request_dict)
				if self.request_dict['slug'] == 'firewall':
				    print "Firewall"
				    self.response = self._handle_firewall_config(self.request_dict)
				if self.request_dict['slug'] == 'vpn':
				    print "VPN"
				    self.response = self._handle_vpn_config(self.request_dict)
				if self.request_dict['slug'] == 'vlanpair':
				    print "vlanpair"
				    self.vlanin = self.request_dict['vlanin']
				    self.vlanout = self.request_dict['vlanout']
				    os.system("modprobe 8021q")
				    cmd = "vconfig add eth0 "+str(self.vlanin)+" INGRESS"
				    os.system(cmd)
				    
				    cmd = "vconfig add eth0 "+str(self.vlanout)+" EGRESS"
				    os.system(cmd)
				    
				    cmd = "ifconfig eth0."+str(self.vlanin)+" promisc up"
				    os.system(cmd)
				    
				    cmd = "ifconfig eth0."+str(self.vlanout)+" promisc up"
				    os.system(cmd)
    
				    cmd = "brctl addbr br0"
				    os.system(cmd)
		    
				    cmd = "brctl addif br0 eth0."+str(self.vlanin)
				    os.system(cmd)
		    
				    cmd = "brctl addif br0 eth0."+str(self.vlanout)
				    os.system(cmd)
		    
				    cmd = "ifconfig br0 up"
				    os.system(cmd)
				if self.request_dict['slug'] == 'vbts':
				    print "[LOG] VBTS...received request:", self.request_dict
				    self.response = self._advertise_l2vm(self.request_dict)
				if self.response:
				    print "[LOG] Sending the respone. ", self.response
				    fd.write(str(self.response))
                        except (IOError,SyntaxError):
            	          continue
            except IOError:
                continue
	    print "[LOG] Closing device \r\n"
   	    fd.close()

class Command(object):
    def __init__(self, cmd):
        self.cmd = cmd
        self.process = None
        self.output = None

    def run(self, timeout):
        def target():
            print 'Thread started'
            self.process = subprocess.Popen(self.cmd, stdout=subprocess.PIPE, shell=True)
            (self.output, self.error) = self.process.communicate()
            print 'Thread finished'

        thread = threading.Thread(target=target)
        thread.start()

        thread.join(timeout)
        if thread.is_alive():
            print 'Terminating process'
            self.process.terminate()
            thread.join()
        
        return (self.process.returncode, self.output, self.error)
            
def main():
    """
    Start the Daemon Loop with required data
    """
    VmConf = VMConfigurationDaemon()
    VmConf.daemon_loop()
    sys.exit(0)
    pass


if __name__ == "__main__":
    main()



    


