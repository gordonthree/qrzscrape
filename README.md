## Python script that generates a mailing list by reading the QRZ.com database.

### How to use
1. Add your qrz credentials to qrz_creds.txt like this: ``username,password`` Note, you must have at least the xml data subscription.
2. Add the callsigns you want to generate a mailing list for to ``callsigns.txt``, one callsign per line.
3. Run the script, it will read each callsign and output data to hams.csv. There is a 100msec delay per request to avoid hammering the QRZ servers.

Thanks to K8VSY for their telegram bot script https://gitlab.com/vyano/pytelehambot

