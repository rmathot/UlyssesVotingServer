#!/usr/bin/python -OO
# -*- coding: utf-8 -*-
'''
This tool is part of UlyssesVoting and can be used to generate the configuration
file of an election.

@author: Richard Mathot
'''

import json
import sys
# pylint: disable=E0611
from hashlib import sha256
from Crypto.ccs_va import ccsva_gen
from Util.folder import create_dir_ifnexists

def main(name):
    '''Launch interactive configuration for an election'''
    print("Welcome into the Election Configuration Tool")

    raw_input("Press <ENTER> to start generating election settings...")

    print("Generating commitment and encryption keys...")
    ((g, h, g1, h1), x1) = ccsva_gen()
    print("Key generation successful!")

    raw_input("Press <ENTER> to continue...")
    print("Please configure question and answers")

    question = raw_input("Question? --> ")
    answer_0 = raw_input("Answer 0? --> ")
    answer_1 = raw_input("Answer 1? --> ")

    election_pub = json.dumps({'human' : {'name' : name,
                                          'question' : question,
                                          'answer_0' : answer_0,
                                          'answer_1' : answer_1},
                                'crypto' : {'g' : g.json(),
                                            'h' : h.json(),
                                            'g1' : g1.json(),
                                            'h1' : h1.json(),
                                             }
                               }, indent = 4)
                    # 'indent' parameter enables/disables human-readable format
    election_fingerprint = sha256(election_pub).hexdigest()

    election_priv = json.dumps({'crypto' : {'x1' : x1}}, indent = 4)
                    # 'indent' parameter enables/disables human-readable format

    create_dir_ifnexists(name + ".edata/")
    create_dir_ifnexists(name + ".edata/pb/")
    create_dir_ifnexists(name + ".edata/sb/")
    print("All the election files should be in " + name + ".edata/")

    filedes = open(name + ".edata/" + name + ".pub.json", "w")
    filedes.write(election_pub)
    filedes.close()

    print("Election settings and public keys are in " + name + ".edata/" \
          + name + ".pub.json")
    print("Election hash (sha256): " + election_fingerprint)

    filedes = open(name + ".edata/" + name + ".priv.json", "w")
    filedes.write(election_priv)
    filedes.close()

    print("Private keys are in " + name + ".edata/" + name + ".priv.json")

    exit(0)

if __name__ == '__main__':
    if(sys.argv.__len__() != 2):
        print("Please provide a name for the election \n\
        USAGE: ./configure_election.py <name>")
        sys.exit(1)
    main(sys.argv[1])#.encode('utf-8', 'ignore'))
