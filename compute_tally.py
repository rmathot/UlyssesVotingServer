#!/usr/bin/python -OO
# -*- coding: utf-8 -*-

'''
This tool is part of UlyssesVoting and can be used to compute the final outcome
of an election.

@author: Richard Mathot
'''

import logging
import sys

def main():
    exit(0)

if __name__ == '__main__':
    logging.basicConfig(level = logging.ERROR)
    if(sys.argv.__len__() != 4):
        logging.critical("Incorrect argument number! \n    \
        USAGE: ./compute_tally.py <settings> <privkey> <ballots_folder>")
        exit(1)
    main()
