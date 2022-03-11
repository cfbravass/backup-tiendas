#!/usr/bin/env python3
'''
'''


from pydrive2.auth import GoogleAuth
from pydrive2.drive import GoogleDrive
from utilities import pause_and_exit


credentials_file = 'credentials.json'


class Drive:

    credentials_file = 'credentials.json'
    instance = None

    def __init__(self):
        print('Autenticando...\t\t\t', end='\t')
        try:
            gauth = GoogleAuth()
            gauth.LoadCredentialsFile(self.credentials_file)

            if not gauth.credentials:
                gauth.LocalWebserverAuth()
            elif gauth.access_token_expired:
                gauth.Refresh()
            else:
                gauth.Authorize()
            gauth.SaveCredentialsFile(self.credentials_file)
            print('OK\n')
            self.instance = GoogleDrive(gauth)
        except Exception as e:
            print('Error\n\n', e)
            pause_and_exit(1)
