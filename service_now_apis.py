#!/usr/bin/env python3


# developed by Gabi Zapodeanu, TME, Enterprise Networks, Cisco Systems


# This file contains the ServiceNow functions to be used during the demo

import requests
import json
import utils


from config import SNOW_ADMIN, SNOW_PASS, SNOW_URL


# users roles :
# SNOW_ADMIN = Application Admin
# SNOW_DEV = Device REST API Calls


def get_last_incidents_list(incident_count):
    """
    This function will return the numbers for the last {incident_count} number of incidents
    :param incident_count: number of incidents
    :return: incident list - list with all incidents numbers
    """
    url = SNOW_URL + '/table/incident?sysparm_limit=' + str(incident_count)
    headers = {'Content-Type': 'application/json', 'Accept': 'application/json'}
    response = requests.get(url, auth=(SNOW_ADMIN, SNOW_PASS), headers=headers)
    incident_json = response.json()
    incident_info = incident_json['result']
    incident_list = []
    for incident in incident_info:
        incident_list.append(incident['number'])
    return incident_list


def get_last_incidents_info(incident_count):
    """
    This function will return the info for the last {incident_count} number of incidents
    :param incident_count: number of incidents
    :return: incident info - info for all incidents
    """
    url = SNOW_URL + '/table/incident?sysparm_limit=' + str(incident_count)
    headers = {'Content-Type': 'application/json', 'Accept': 'application/json'}
    response = requests.get(url, auth=(SNOW_ADMIN, SNOW_PASS), headers=headers)
    incident_json = response.json()
    incident_info = incident_json['result']
    return incident_info


def get_incident_detail(incident):
    """
    This function will return the incident information for the incident with the number {incident}
    :param incident: incident number
    :return: incident info
    """
    incident_sys_id = get_incident_sys_id(incident)
    url = SNOW_URL + '/table/incident/' + incident_sys_id
    headers = {'Content-Type': 'application/json', 'Accept': 'application/json'}
    response = requests.get(url, auth=(SNOW_ADMIN, SNOW_PASS), headers=headers)
    incident_json = response.json()
    return incident_json['result']


def create_incident(description, comment, username, severity):
    """
    This function will create a new incident with the {description}, {comments} for the {user}
    :param description: incident short description
    :param comment: comment with incident details
    :param username: caller username
    :param severity: urgency level
    :return: incident number
    """
    caller_sys_id = get_user_sys_id(username)
    url = SNOW_URL + '/table/incident'
    payload = {'short_description': description,
               'comments': (comment + '\n\nCreated using APIs by caller: ' + username),
               'caller_id': caller_sys_id,
               'urgency': severity,
               'priority': severity
               }
    headers = {'Content-Type': 'application/json', 'Accept': 'application/json'}
    response = requests.post(url, auth=(username, SNOW_PASS), data=json.dumps(payload), headers=headers)
    incident_json = response.json()

    return incident_json['result']['number']


def update_incident(incident, comment, username):
    """
    :param incident: incident number
    :param comment: comment with incident details
    :param username: caller username
    :return:
    """
    caller_sys_id = get_user_sys_id(username)
    incident_sys_id = get_incident_sys_id(incident)
    url = SNOW_URL + '/table/incident/' + incident_sys_id
    payload = {'comments': (comment + '\n\nUpdated using APIs by caller: ' + username),
               'caller_id': caller_sys_id}
    headers = {'Content-Type': 'application/json', 'Accept': 'application/json'}
    response = requests.patch(url, auth=(username, SNOW_PASS), data=json.dumps(payload), headers=headers)


def get_incident_sys_id(incident):
    """
    This function will find the incident sys_id for the incident with the number {incident}
    :param incident: incident number
    :return: incident sys_id
    """
    url = SNOW_URL + '/table/incident?sysparm_limit=1&number=' + incident
    headers = {'Content-Type': 'application/json', 'Accept': 'application/json'}
    response = requests.get(url, auth=(SNOW_ADMIN, SNOW_PASS), headers=headers)
    incident_json = response.json()
    return incident_json['result'][0]['sys_id']


def close_incident(incident, username):
    """
    This function will close the incident with the number {incident}
    :param incident: incident number
    :param username: user that calls in to close ticket
    :return: status code
    """
    incident_id = get_incident_sys_id(incident)
    caller_id = get_user_sys_id(username)
    url = SNOW_URL + '/table/incident/' + incident_id
    payload = {'close_code': 'Closed/Resolved by Caller',
               'state': '7',
               'caller_id': caller_id,
               'close_notes': ('Closed using APIs by caller: ' + username)}
    headers = {'Content-Type': 'application/json', 'Accept': 'application/json'}
    response = requests.put(url, auth=(username, SNOW_PASS), data=json.dumps(payload), headers=headers)


def get_user_sys_id(username):
    """
    This function will retrieve the user sys_id for the user with the name {username}
    :param username: the username
    :return: user sys_id
    """
    url = SNOW_URL + '/table/sys_user?sysparm_limit=1&name=' + username
    headers = {'Content-Type': 'application/json', 'Accept': 'application/json'}
    response = requests.get(url, auth=(username, SNOW_PASS), headers=headers)
    user_json = response.json()
    return user_json['result'][0]['sys_id']


def get_incident_comments(incident):
    """
    This function will return the comments for an incident with the number {incident_number}
    :param incident: incident_number
    :return: incident comments
    """
    incident_sys_id = get_incident_sys_id(incident)
    url = SNOW_URL + '/table/sys_journal_field?sysparm_query=element_id=' + incident_sys_id
    headers = {'Content-Type': 'application/json', 'Accept': 'application/json'}
    response = requests.get(url, auth=(SNOW_ADMIN, SNOW_PASS), headers=headers)
    comments_json = response.json()['result']
    return comments_json


def delete_incident(incident):
    """
    This function will delete the incident with the number {incident}
    :param incident: incident number
    :return: status code
    """
    incident_id = get_incident_sys_id(incident)
    url = SNOW_URL + '/table/incident/' + incident_id
    headers = {'Content-Type': 'application/json', 'Accept': 'application/json'}
    response = requests.delete(url, auth=(SNOW_ADMIN, SNOW_PASS), headers=headers)
    return response.status_code


def find_comment(incident, comment):
    """
    Find if any of the existing comments from the {incident} matches exactly the {comment}
    :param incident: incident number
    :param comment: comment string to search for
    :return: {True} if comment exist, {False} if not
    """
    comments_list = get_incident_comments(incident)
    for comment_info in comments_list:
        if comment == comment_info['value']:
            return True
    return False

