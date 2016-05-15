#!/usr/bin/python
import argparse
import subprocess
import time

def set_cepa_config(audit_endpoint):
    cepa_config_file='/opt/CEEPack/emc_cee_config.xml'
    filedata = None

    with open(cepa_config_file, 'r') as file :
      filedata = file.read()

    # Replace the target string
    #this is hack way ot update xml file... probably should edit with xml tool
    #Todo: update with proper xml update
    current_config = '<EndPoint></EndPoint>'
    new_config = '<EndPoint>{0}</EndPoint>'.format(audit_endpoint)
    filedata = filedata.replace(current_config,new_config,1)
    filedata = filedata.replace('>0<','>1<',1)
    filedata = filedata.replace('<Debug>0</Debug>','<Debug>1</Debug>')
    filedata = filedata.replace('<Verbose>0</Verbose>','<Verbose>1</Verbose>')

    # Write the file out again
    with open(cepa_config_file, 'w') as file:
      file.write(filedata)


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
