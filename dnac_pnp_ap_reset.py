#!/usr/bin/env python3


# developed by Gabi Zapodeanu, TME, Enterprise Networks, Cisco Systems


import time
import urllib3
import logging

import dnac_apis

from requests.auth import HTTPBasicAuth  # for Basic Auth
from urllib3.exceptions import InsecureRequestWarning  # for insecure https warnings
from netmiko import ConnectHandler

from config import DNAC_PASS, DNAC_USER
from config import PnP_WLC_NAME, PnP_WLC_IP, PnP_WLC_USER, PnP_WLC_PASS

urllib3.disable_warnings(InsecureRequestWarning)  # disable insecure https warnings

DNAC_AUTH = HTTPBasicAuth(DNAC_USER, DNAC_PASS)


DEVICE_INFO = {
    'device_type': 'cisco_ios',
    'host': PnP_WLC_IP,
    'username': PnP_WLC_USER,
    'password': PnP_WLC_PASS,
    'secret': PnP_WLC_PASS
    }


def main():
    """
    This application will:
    - clear the capwap ap config from C9800-CL
    - delete the AP from the PnP database
    - re-sync the WLC controller
    - delete the AP from the DNAC inventory
    """

    # run the application on demand to reset the AP PnP demo

    print('\n\nApplication "dnac_pnp_ap_reset.py" started')

    # device info and site

    pnp_device_assign = {'device_hostname': 'APB026.80DF.6E18', 'site_name': 'PDX', 'floor_name': 'Floor 3'}

    site_name = pnp_device_assign['site_name']
    floor_name = pnp_device_assign['floor_name']
    pnp_device_name = pnp_device_assign['device_hostname']

    print('\nThis application will reset the DNA Center PnP AP demo')

    # logging, debug level, to file {application_run.log}
    logging.basicConfig(
        filename='application_run.log',
        level=logging.DEBUG,
        format='%(asctime)s.%(msecs)03d %(levelname)s %(module)s - %(funcName)s: %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S')

    dnac_token = dnac_apis.get_dnac_jwt_token(DNAC_AUTH)

    # find if the AP is in provisioned state and delete from the PnP database

    pnp_devices_info = dnac_apis.pnp_get_device_list(dnac_token)
    device_state = pnp_devices_info[0]['deviceInfo']['state']
    pnp_device_id = pnp_devices_info[0]['id']
    pnp_device_ip = pnp_devices_info[0]['deviceInfo']['httpHeaders'][0]['value']

    print('\nPnP device state: ' + device_state)
    if device_state != 'Unclaimed':
        # if AP is unclaimed, go through the process to delete all configs

        # connect to C9800-CL using ssh/netmiko
        net_connect = ConnectHandler(**DEVICE_INFO)
        command_output = net_connect.find_prompt()
        print('\nPrompt of the connected device: ', command_output)

        # send the command to clear the PnP AP capwap config
        command = 'clear ap config ' + pnp_device_name
        command_output = net_connect.send_command(command)
        print(command_output)

        # disconnect from the C9800-CL
        net_connect.disconnect()

        # check if error during CLI command and delete config manually

        if '% Error' in command_output:
            print('\n\nClear AP Config All from C9800-CL>Configuration>Wireless>AP>Advanced')
            input('\nPress any key to continue')

        print('\nDemo reset started')

        # wait for the AP to delete the config and reboot
        time.sleep(30)

        print('\n\n\nPnP database device id: ' + pnp_device_id)
        print('PnP device IP Address: ', pnp_device_ip)

        # delete the device from the PnP database
        delete_result = dnac_apis.pnp_delete_provisioned_device(pnp_device_id, dnac_token)
        print('PnP database delete result: ', delete_result['deviceInfo']['state'])

        # get the Provisioned AP device id
        ap_device_id = dnac_apis.get_device_id_name(pnp_device_name, dnac_token)

        # sync the PnP WLC, wait 60 seconds to complete, delete the PnP device from the DNAC inventory
        dnac_apis.sync_device(PnP_WLC_NAME, dnac_token)
        print('\nDNA Center Device Re-sync started: ', PnP_WLC_NAME)
        time.sleep(60)

        delete_task_id = dnac_apis.delete_device(ap_device_id, dnac_token)['taskId']
        print('Device deleted from DNA Center inventory started')

        time.sleep(30)

        delete_status = dnac_apis.check_task_id_status(delete_task_id, dnac_token)
        print('\nDelete task status: ', delete_status)

    print('\nYou may start the demo again when the AP is available in the Cisco DNA Center PnP tab')
    print('\n\nEnd of Application "dnac_pnp_ap_reset.py" Run')


if __name__ == '__main__':
    main()
