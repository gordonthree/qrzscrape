#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# Copyright 2023, K8VSY, https://k8vsy.radio/
# Licensed under the Eiffel Forum License 2.


import requests
import xmltodict
import time
import csv
import re  # Import the regular expression module

session = requests.session()

def get_qrz_creds():
    '''
    Grab credentials for QRZ.com
    '''

    try:
        fh = open('qrz_creds.txt', 'r')
    except:
        print('Please create a `qrz_creds.txt` file in the same directory ' +
              'as this file in the format of: username,password')
        return None, None

    lines = list()

    if fh:
        lines = fh.readlines()

    fh.close()

    if len(lines) > 0:
        txt = lines[0]
        parts = txt.split(',')
        if len(parts) == 2:
            qrz_username = parts[0].strip()
            qrz_password = parts[1].strip()
        else:
            print('Not able to understand format of qrz_creds.txt file')
            return None, None
    else:
        return None, None

    return qrz_username, qrz_password

def qrz_sessionkey(session):
    qrz_username, qrz_password = get_qrz_creds()
    if not qrz_username or not qrz_password:  # Simplified condition
        print('Cannot log into QRZ')
        return None  # Return None on failure

    url = f"https://xmldata.qrz.com/xml/current/?username={qrz_username}&password={qrz_password}" # f-string formatting
    try:
        r = session.get(url)
        r.raise_for_status()  # Raise HTTPError for bad responses (4xx or 5xx)
        raw_session = xmltodict.parse(r.content)
        session_key = raw_session.get('QRZDatabase', {}).get('Session', {}).get('Key') # Safer access
        if session_key: # Check if session_key is actually obtained
            print('Got session key')
            return session_key
        else:
            print("Could not obtain session key")
            return None
    except requests.exceptions.RequestException as e:
        print(f"Error getting session key: {e}")
        return None
    except (xmltodict.expat.ExpatError, KeyError) as e: # Catch potential parsing errors
        print(f"Error parsing XML: {e}")
        return None


def qrz_lookup(session, session_key, callsign):
    url = f"https://xmldata.qrz.com/xml/current/?s={session_key}&callsign={callsign}" # f-string formatting
    try:
        r = session.get(url)
        r.raise_for_status()
        raw = xmltodict.parse(r.content).get('QRZDatabase', {}) # Safer access
        ham = raw.get('Callsign')
        return ham
    except requests.exceptions.RequestException as e:
        print(f"Error looking up callsign: {e}")
        return None
    except (xmltodict.expat.ExpatError, KeyError) as e:
        print(f"Error parsing XML: {e}")
        return None

def cleanup_value(value):
    """Removes commas, newlines, and other problematic characters from a string."""
    if value is None:  # Handle None values gracefully
        return "none"
    value = str(value)  # Ensure it's a string
    value = re.sub(r'[,\n\r"]', ' ', value).strip() # Replace commas, newlines, carriage returns and quotes with spaces, then strip whitespace
    return value

def lookup_call(session, session_key, callsign):
    '''
    look up a given callsign via QRZ; and pretty-print the output
    '''

    # print(f'Input: {callsign[:15]}')  # f-string formatting

    if not (3 <= len(callsign) < 15 and any(c.isdigit() for c in callsign[:3])): # Simplified validation
        print('Not a valid call sign.')
        return None  # Return None for invalid call signs

    outs = qrz_lookup(session, session_key, callsign)
    if outs is None:  # Check for None, which could indicate error or no result
        print('No results found on QRZ.com or error occurred.')
        return None

    message = ""
    #fields = ['call', 'fname', 'name', 'email', 'class', 'addr1', 'addr2', 'state', 'efdate', 'expdate']
    for field in fields:
        value = outs.get(field)
        cleaned_value = cleanup_value(value)  # Clean the value
        message += cleaned_value + "," if field != 'expdate' else cleaned_value # Add cleaned value
    return message


# open a session the QRZ api
session_key = qrz_sessionkey(session)

if session_key is None:
    print("Failed to obtain session key. Exiting.")
    exit(1)  # Exit with an error code if the session can't be established

fields = ['call', 'fname', 'name', 'email', 'class', 'addr1', 'addr2', 'state', 'zip', 'efdate', 'expdate']  # Define fields *once*

with open("callsigns.txt", "r") as f, open("hams.csv", "w", newline="") as out:
    writer = csv.writer(out, quoting=csv.QUOTE_MINIMAL)
    writer.writerow(fields)  # Write header row

    for callsign in f:  # Iterate over lines in the file directly
        callsign = callsign.rstrip("\n")  # Remove newline from each line
        result = lookup_call(session, session_key, callsign)
        if result:
            writer.writerow(result.split(","))
            print(result)
        time.sleep(0.1)

print("Done")

    