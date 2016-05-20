#!/usr/bin/python
import argparse
import subprocess
import time
import xml.etree.ElementTree as etree

def set_cepa_config(audit_endpoint):
    cepa_config_file='/opt/CEEPack/emc_cee_config.xml'
    tree = etree.parse(cepa_config_file)

    audit_node = tree.find('CEPP/Audit/Configuration')
    audit_node.find('Enabled').text = "1"
    audit_node.find('EndPoint').text = audit_endpoint

    tree.write(cepa_config_file)

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--audit_endpoint',default='Splunk@http://127.0.0.1:12229',help='audit processor endpoint')
    parser.add_argument('--bash',action='store_true',help='drop into container bash')
    args = parser.parse_args()

    #Start webservice
    subprocess.Popen(["python", "/cepa.py"])

    #set CEPA config & Start
    set_cepa_config(args.audit_endpoint)
    subprocess.call(['/opt/CEEPack/emc_cee.exe','-daemon'],cwd='/opt/CEEPack')

    #start bash, otherwise tail the audit.log to console indefinitely
    if args.bash:
        subprocess.call('/bin/bash')
    else:
        call(['tail','-f','/audit.log'])

if __name__ == '__main__':
    main()
