# PnP_AP_p
AP Cisco DNA Center PnP Workflow Automation

This repo includes all the files needed for PnP AP Provisioning.
This application has been tested using Cisco DNA Center version 1.2.10, C9800-CL controller version 16.10, and one Access Point Cisco 3800.

For the application the following are needed:
- Cisco DNA Center
- Catalyst 9800 controller
- Cisco Access Point 3800
- ServiceNow developer account


## Installation

The requirements.txt file includes all the Python libraries needed for this application.


## Configuration

Change the config.py file with the devices, applications, user name and passwords that you have in your environment.
This file is the only file you need to change.


## Usage

Files included:
 - requirements.txt - python libraries required
 - config.py - file with the info on how to configure access to devices and applications, and the AP assignment
 - dnac_apis.py, service_now_apis.py - Python modules for DNA Center and ServiceNow
 - utils.py - Python module with various Python useful tools
 - dnac_pnp_ap.py - AP PnP provisioning
 - dnac_pnp_ap_reset.py - reset AP PnP demo
   

The application "dnac_pnp_ap.py" will:
   - identify any PnP unclaimed APs
   - map to local database to identify the floor to provision the AP to
   - claim the AP
   - verify PnP process workflow
   - re-sync the WLC controller
   - verify the AP on-boarded using the Cisco DNA Center Inventory:
     - reachability, IP address, access switch info, WLC info
   - create, and update a ServiceNow incident with the information collected
   - close ServiceNow incident if PnP completes successfully

The application "dnac_pnp_ap_reset.py" will:
   - clear the AP CAPWAP config from C9800-CL
   - delete the AP from the PnP database
   - re-sync the WLC controller
   - delete the AP from the DNAC inventory
   
For demo and testing purpose this application will run on demand and PnP one AP at one time. It could be changed to constantly run and identify unclaimed APs.
If large deployments of APs are needed, we could import the AP MAC addresses and location assignments from a CSV file.