#!/usr/bin/env python3
'''
Setup Program
'''


from pydrive2.auth import GoogleAuth
from pydrive2.drive import GoogleDrive
import json
import os
from utilities import pause_and_exit


def main():
    '''
    Main function
    '''
    global CONFIG
    CONFIG = {
        'drive_folder_id': '',
        'local_folders': [],
        'days_to_keep': 0,
    }
    settings()  # 1
    auth()  # 2
    config()  # 3
    print('\nINSTALACIÓN COMPLETA\n')
    pause_and_exit()


def get_folder_id(name, parent_id):
    '''
    Get drive folder id
    '''
    for f in DRIVE.ListFile({'q': f'"{parent_id}" in parents and trashed=false and title="{name}"'}).GetList():
        return f['id']
    return None


def create_folder(name, parent_id):
    '''
    Create drive folder and return id
    '''
    folder_id = DRIVE.CreateFile({
        'title': name,
        'parents': [{'id': parent_id}],
        'mimeType': 'application/vnd.google-apps.folder', })
    folder_id.Upload()
    return folder_id['id']


def get_or_create_folder_id(parent_id):
    '''
    Create or get folder id
    '''
    print('\nCarpeta backup destino...')
    name = input('NOMBRE TIENDA: ').strip()
    while name == '':
        name = input('NOMBRE TIENDA: ').strip()
    f_id = get_folder_id(name, parent_id) or create_folder(name, parent_id)
    print('OK\n')
    return f_id


def config():
    '''
    Configure
    '''
    print('\nConfigurando...\t', end='\t')
    get_local_folders()
    get_days_to_keep()

    # get drive folder name


    CONFIG['drive_folder_id'] = get_or_create_folder_id('root')

    # Create config file
    with open('config.json', 'w') as f:
        json.dump(CONFIG, f, indent=4)

    print('OK\n')


def get_days_to_keep():
    '''
    Get days to keep
    '''
    ok = False
    print()
    while not ok:
        print('Conservar durante (   ) días', end='\r')
        inp = input('Conservar durante (').strip()
        if inp.isdigit() and int(inp) > 0:
            CONFIG['days_to_keep'] = int(inp)
            ok = True
        else:
            print('Debe ingresar un número mayor a 0\n')


def get_local_folders():
    '''
    Get local folders
    '''
    ok = False
    idx = 1
    print('\n\nIngrese las rutas a carpetas locales:')
    print('\t- deje en blanco para finalizar\n')
    while not ok:
        inp = input(f'PATH #{idx}: ')
        if inp == '' and CONFIG['local_folders']:
            ok = True
        elif inp == '':
            print('Debe ingresar al menos una carpeta\n')
        elif os.path.isdir(inp):
            CONFIG['local_folders'].append(inp)
            idx += 1
        else:
            print('Revise el path ingresado\n')


def auth():
    '''
    Authenticate with Google Drive
    '''
    print('\nAutenticando...\t', end='\t')
    try:
        gauth = GoogleAuth()
        gauth.LocalWebserverAuth()
        global DRIVE
        DRIVE = GoogleDrive(gauth)
    except Exception as e:
        print(f'ERROR\n\n{e}')
        pause_and_exit(1)
    print('OK\n')


def settings():
    print('\nConfigurando entorno...\t', end='\t')
    # Check client secrets
    if not os.path.exists('client_secrets.json'):
        print('ERROR\n\nNo se encontró el archivo client_secrets.json')
        pause_and_exit(1)
    try:
        with open('client_secrets.json', 'r') as f:
            global SECRETS
            SECRETS = json.load(f)
            # Check if client secrets are valid
            if 'web' not in SECRETS or 'client_id' not in SECRETS['web'] or 'client_secret' not in SECRETS['web']:
                print('ERROR\n\nEl archivo client_secrets.json no es válido')
                pause_and_exit(1)
    except Exception as e:
        print('ERROR\n\nNo se pudo leer el archivo client_secrets.json')
        print(e)
        pause_and_exit(1)

    # Create empty credentials file
    with open('credentials.json', 'w') as f:
        f.write('')

    # Create settings files
    with open('settings.yaml', 'w') as f:
        f.write(f'''
client_config_backend: settings
client_config:
  client_id: {SECRETS['web']['client_id']}
  client_secret: {SECRETS['web']['client_secret']}

save_credentials: True
save_credentials_backend: file
save_credentials_file: credentials.json

get_refresh_token: True

oauth_scope:
  - https://www.googleapis.com/auth/drive
'''
                )
    print('OK\n')


if __name__ == '__main__':
    main()
