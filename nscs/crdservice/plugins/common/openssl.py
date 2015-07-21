import os
import stat
import subprocess
from nscs.crdservice.openstack.common import log as logging
from oslo.config import cfg


LOG = logging.getLogger(__name__)
CONF = cfg.CONF

DEFAULT_SUBJECT = '/C=US/ST=Unset/L=Unset/O=Unset/CN='
DIR_PERMS = (stat.S_IRUSR | stat.S_IWUSR | stat.S_IXUSR |
             stat.S_IRGRP | stat.S_IXGRP |
             stat.S_IROTH | stat.S_IXOTH)
CERT_PERMS = stat.S_IRUSR | stat.S_IRGRP | stat.S_IROTH
PRIV_PERMS = stat.S_IRUSR | stat.S_IWUSR | stat.S_IXUSR

CA_CERT_NAME = 'ca_cert.pem'
CA_PRIVATE_KEY = 'ca_private_key.pem'
DEFAULT_CA_CERT_DIR = "/tmp/crd-ca/"
DAYS_VALID = "1024"
SWITCH_KEY = "switch.key"
SWITCH_CSR = "switch.csr"
SWITCH_CRT = "switch.crt"
OPENSSL = "/usr/bin/openssl"

def is_file(file_path):
    return os.path.exists(file_path)

def write_to_file(file_path,data):
    with open(file_path,"w+") as f: f.write(data)




class CertificateAuthority(object):
    """
    Generate Key pair for the logical switches based on
    the DPID.
    Certify the Publick key with Cluster CA.
    """
    
    def __init__(self):
        pass
        
    def execute_command(self, cmd):
        try:
            #LOG.debug(_("Executing command => %s"), cmd)
            output = subprocess.check_output(cmd.rsplit(' '))
            return output    
        except subprocess.CalledProcessError, e:
            #LOG.debug(_("Error while processing the command => %s [Error] %s"),cmd,e)
            pass

    def create_ca_directory(self,dirname,cert,private_key):
        """
        Create the directory to store Cluster certificates and keys
        to certify the switches
        CA directory format example:
         Cluster CA Certificate: /etc/crd/ca/7250fad1-6359-4871-830b-4873326ffbdd/ca.pem
         Cluster CA Private Key: /etc/crd/ca/7250fad1-6359-4871-830b-4873326ffbdd/pvtk.pem
        """
        if not is_file(DEFAULT_CA_CERT_DIR): os.makedirs(DEFAULT_CA_CERT_DIR,DIR_PERMS)
        dirs = DEFAULT_CA_CERT_DIR+dirname+"/"
        if not is_file(dirs):
            os.makedirs(dirs,DIR_PERMS)
            #LOG.debug(_("writing Cluster Certificate at %s "), dirname+CA_CERT_NAME)
            write_to_file(dirs+CA_CERT_NAME,cert)
            #LOG.debug(_("writing Cluster private Key at %s "), dirname+CA_PRIVATE_KEY)
            write_to_file(dirs+CA_PRIVATE_KEY,private_key)
        return  dirs+CA_CERT_NAME,dirs+CA_PRIVATE_KEY
    

    def  generate_keypair_csr(self,dirname,common_name):
        """
        Generate the Keypair and CSR
        
        @input  dirname: Directory path, where to create the files.
        @input  common_name: the CN attribute value for CSR subject.
        
        @return complete private key and CSR file paths created.
        
        """
        """ Create new directory for this switch """
        #LOG.debug(_("Generating Asymmetric key-pair for Logical switch..."))    
        switch_dir = DEFAULT_CA_CERT_DIR+dirname+"/"+common_name
        switch_key = switch_dir +"/"+ SWITCH_KEY
        switch_csr = switch_dir +"/"+ SWITCH_CSR
        
        if not is_file(switch_dir):
            os.makedirs(switch_dir, DIR_PERMS)
        
        if is_file(switch_dir):
            cmd = OPENSSL +" req -new -nodes -keyout "+switch_key+ \
                  " -out "+switch_csr+ \
                  " -days "+DAYS_VALID+" -subj "+DEFAULT_SUBJECT+common_name
            #LOG.debug(_("Asymmetric keypair generation..  %s"),cmd)
            ret = self.execute_command(cmd)
        return  switch_key, switch_csr
        
    def certify_csr(self,dirname,common_name,ca_path,ca_private_key_path):
        """
        Certifies a CSR by generating a valid Certificate.
        
        @input dirname : the path to the directory where the crt need to be preserved.
                         here, its the CLUSTER ID
        @input common_name: The CN attribute, here is the switch DPID
        @input ca_path: complete path to CA PEM file
        @input ca_private_key_path: complete path to CA Private key file.
        
        @return complete path to the generated Certificate
        """
        dir_path = DEFAULT_CA_CERT_DIR+dirname+"/"+common_name+"/"
        csr_path = dir_path+SWITCH_CSR
        ls_certificate = dir_path+SWITCH_CRT
        
        if is_file(csr_path) and is_file(ca_path) and is_file(ca_private_key_path):
            cmd = OPENSSL +" x509 -req -in "+ csr_path +\
                  " -CA "+ca_path +" -CAkey "+ca_private_key_path+ \
                  " -CAcreateserial -out "+ ls_certificate +" -days "+ DAYS_VALID
            #LOG.debug(_("Generating Certificate to Logical Switch {%s} => %s "),common_name,cmd)
            self.execute_command(cmd)
        return  ls_certificate   
            
