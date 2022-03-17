#!/usr/bin/env python3
'''
Copyright (C) 2022 Santiago Agudelo


This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License version 3 as published by
the Free Software Foundation.


This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
GNU General Public License for more details.


You should have received a copy of the GNU General Public License
along with this program. If not, see <http://www.gnu.org/licenses/>.
'''


from datetime import datetime
from drive import Drive
from utilities import pause_and_exit
import json
import os


def main():
    '''
    Main function
    '''
    check_config()  # 1
    remove_old_backups()
    upload_folders()
    print('\n\n_________________\nBACKUP COMPLETADO\n')
    pause_and_exit()


def upload_folders():
    '''
    Upload folders to Google Drive
    '''
    backup_date = datetime.now().strftime('%d-%m-%Y')
    print(f'\n\nBACKUP {backup_date}')
    # Check if backup already exists
    root_folder_id = get_folder_id(backup_date, CONFIG['drive_folder_id'])
    if root_folder_id:
        print('El backup ya existe')
        pause_and_exit()
    root_folder_id = create_folder(backup_date, CONFIG['drive_folder_id'])

    # Upload files
    print('Carga de archivos al servidor...')
    for folder in CONFIG['local_folders']:
        parent_id = root_folder_id
        for root, _, files in os.walk(folder):
            print(f'\nSubiendo: {root}')

            parent_id = get_or_create_folder_id(os.path.basename(root), parent_id)

            for file in files:
                file_name = file[:20] + '...' if len(
                    file) > 20 else file + '...' + ' ' * (17 - len(file))
                print(f'\t{file_name}\t', end='\t')
                file_path = os.path.join(root, file)
                # Skip empty files
                if os.path.getsize(file_path) == 0:
                    print('SALTADO')
                    continue

                file_metadata = {
                    'title': file,
                    'parents': [{'id': parent_id}]
                }

                try:
                    media = DRIVE.CreateFile(file_metadata)
                    media.SetContentFile(file_path)
                    media.Upload()
                    print('OK')
                except Exception as e:
                    print('ERROR')
                    print(e)
                    continue


def get_or_create_folder_id(name, parent_id):
    '''
    Create or get folder id
    '''
    # Get folder id
    f_id = get_folder_id(name, parent_id) or create_folder(name, parent_id)
    return f_id


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


def remove_old_backups():
    '''
    delete backups older than the indicated days
    '''
    print('Buscando backups antiguos...')
    try:
        backups = DRIVE.ListFile(
            {'q': f"'{CONFIG['drive_folder_id']}' in parents and trashed=false"}
        ).GetList()

        for backup in backups:
            try:
                backup_date = datetime.strptime(backup['title'], '%d-%m-%Y')
                now = datetime.now()
                if (now - backup_date).days > CONFIG['days_to_keep']:
                    print(f'backup {backup["title"]}\t\t', end='\t')
                    backup.Delete()
                    print('ELIMINADO\n')
            except ValueError:
                pass
        print('OK\n')
    except Exception as e:
        print('ERROR\nOcurrió un error inesperado')
        print(e)
        pause_and_exit(1)


def check_config():
    '''
    Validate the necessary configurations
    '''
    print('\nValidando configuración...\t', end='\t')
    if not os.path.exists('config.json'):
        print('ERROR\nNo se encontró el archivo de configuración')
        pause_and_exit(1)
    try:
        with open('config.json', 'r') as f:
            config_file = json.load(f)
            # Check if config is valid
            configs = ['drive_folder_id', 'local_folders', 'days_to_keep']
            for config in configs:
                if config not in config_file:
                    print('ERROR\nEl archivo de configuración no es válido')
                    pause_and_exit(1)
            global CONFIG
            CONFIG = config_file
            print('OK\n')
    except Exception as e:
        print('ERROR\nNo se pudo leer el archivo de configuración')
        print(e)
        pause_and_exit(1)
    global DRIVE
    DRIVE = Drive().instance
    # Check if drive folder exists
    print('Carpeta Backup...\t\t', end='\t')
    try:
        # Get all folder in root
        folders_list = DRIVE.ListFile(
            {'q': f"'root' in parents and trashed=false and mimeType='application/vnd.google-apps.folder'"}
        ).GetList()
        for folder in folders_list:
            if folder['id'] == CONFIG['drive_folder_id']:
                print('OK\n')
                break
            else:
                print('ERROR\nNo se encontró el destino en Google Drive')
                pause_and_exit(1)
    except Exception as e:
        print('ERROR\nNo se pudo verificar la carpeta destino')
        print(e)
        pause_and_exit(1)


if __name__ == '__main__':
    main()
