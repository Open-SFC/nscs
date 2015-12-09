# vnf_config_manager.py
#
# Generalized implementation to load the vNF configuration drivers 
# from /opt/vnf_config_drivers directory/
#
# version: 1.0

import fcntl
import imp
import os

import eventlet

class VnfConfigManager(object):

    """
    This class process the loading of several vNF Config Drivers 
    existing in /opt/vnf_config_drivers directory.
    """

    _instance = None
 
    def __init__(self):

      self.vnf_config_drivers = {} 
      self.response = ""
      self.config_driver_path = "/opt/vnf_config_drivers"
      self._load_vnf_config_drivers(self.config_driver_path)

    def _load_vnf_config_drivers(self, driver_path):
       """ 
       Traverse into the directory and instantiate the classes.
       """
       for f in sorted(os.listdir(driver_path)):
           try:
               # get the file extension and file name and verify the same.
               mod_name, file_ext = os.path.splitext(os.path.split(f)[-1])
               drvr_path = os.path.join(driver_path, f)
               if file_ext.lower() == '.py' and not mod_name.startswith('_'):
                  mod = imp.load_source(mod_name, drvr_path)
                  drvr_name = mod_name[0].upper() + mod_name[1:]
                  print "[Info] Loading vNF driver: %s" % drvr_name
                  new_drvr_class = getattr(mod, drvr_name, None)
                  if not new_drvr_class:
                     # note: (trinaths) printing the warning for now, might be
                     # need to take care this in future.
                     print "[Warning] Unable to find the class %s" % new_drvr_class
                  # instantiate the class here.
                  new_drvr = new_drvr_class()
                  self.vnf_config_drivers[new_drvr.get_vnf_name()] = new_drvr
           except Exception as exception:
              print "[Error] vNF driver file %s was not loaded due to %s. " % (f,
                                                              exception)
                
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
                          rq = self.recv['config']
                          print "[LOG] Received Request: ", rq

                          if (hasattr(rq, 'slug') and 
                             rq['slug'] is not None and 
                             hasattr(self.vnf_config_drivers, rq['slug'])):

                             print "[Info] Processing vNF config driver '%s'..." % rq['slug']
                             resp = self.vnf_config_drivers[rq['slug']
                                                       ].handle_vnf_config(rq)
                          if resp:
                             print "[Info] Sending the respone ... ", resp
                             fd.write(str(resp))
                      except (IOError,SyntaxError):
                         continue
            except IOError:
                continue
            print "[Info] Closing device \r\n"
            fd.close()


def main():
  eventlet.monkey_patch()
  vnf_conf =  VnfConfigManager()
  vnf_conf.daemon_loop()
  sys.exit(0)
  pass

if __name__ == "__main__":
   main()
