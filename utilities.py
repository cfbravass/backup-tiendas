#!/usr/bin/env python3
'''
Utilities for backup
'''
import sys

def pause_and_exit(code=0):
    '''
    Pause and exit
    '''
    input('\nPresione ENTER para salir...')
    sys.exit(code)
