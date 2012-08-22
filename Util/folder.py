# -*- coding: utf-8 -*-
'''
'''

from os.path import dirname, exists
from os import makedirs

def create_dir_ifnexists(folder_name):
    '''Create the directory indicated by <folder_name> if it does not exists.
    
    NOTE: folder_name has to be terminated by / '''
    dirpath = dirname(folder_name)
    if not exists(dirpath):
        makedirs(dirpath)
