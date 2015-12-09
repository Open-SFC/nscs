# Virtual Base Station vNF Configuration Manager/Driver

# (note) The File must be named " 'v'bts.py " and the Class must be
# named as " 'V'bts() ". Look into the [0] character of the file and
# class names

import os
import re
import subprocess
import threading
import time

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


class Vbts():
    """
    Virtual Base Station (vbts) vNF configuration Manager/driver. 
    
    Requires, get_vnf_name and handle_vnf_config functions
    to handle and process the configuration.
    """
    def __init__(self):
        self.client_api = 'advertise_l2vm'
        self.vbts_cfg_path ="/etc/lte_l2.conf"
        self.dpdk_cfg_path ="/etc/dpdk-iface.conf"
        self.setup_enb_path ="/home/root/start_l2.sh"
        self.cmd_str = 'curl http://169.254.169.254/openstack/latest/user_data'
        self.command = Command(self.cmd_str)
        print "Loading vBTS vNF.....done"

    def get_vnf_name(self):
        return "vbts"
   
    def handle_vnf_driver(self, request):
        self._advertise_l2vm(request)


    def _advertise_l2vm(self, request):
        """
        Advertises L2VM Details
        """
        json_data = ''
        if request['header'] == 'request':
            request_dict = {}
            request_dict['client_api'] = self.client_api
            print "[LOG] Processing 'Request' header"
            request_dict['instance_id'] = request['instance_id']
            output = None
            ret_code = None
        #    p = subprocess.Popen(['curl http://169.254.169.254/openstack/latest/user_data'],
        #       stdout=subprocess.PIPE,
        #       shell=True)
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

