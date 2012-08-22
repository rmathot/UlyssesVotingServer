#!/usr/bin/python -OO
# -*- coding: utf-8 -*-

'''
This tool is part of UlyssesVoting and can be used to check if a ballot is 
valid or not for an election.

@author: Richard Mathot
'''

import json
import sys
#pylint: disable=E0611
from hashlib import sha256
from shutil import move
from Crypto.ccs_va import init_curves, ccsva_extrip, ccsva_extract_c

#pylint: disable=R0914,R0915
def main(settings, ballot, election_folder):
    '''Launch single ballot validation'''
    print("Welcome into the Ballot Verification Tool")

    filedes = open(settings, 'r')
    settings_raw = filedes.read()
    filedes.close()

    filedes2 = open(ballot, 'r')
    ballot_raw = filedes2.read()
    filedes2.close()

    election_fingerprint = sha256(settings_raw).hexdigest()
    ballot_fingerprint = sha256(ballot_raw).hexdigest()

    print("Election hash (sha256): " + election_fingerprint)
    print("Ballot hash (sha256): " + ballot_fingerprint)

    settings = json.loads(settings_raw)
    ballot = json.loads(ballot_raw)
    print("Election name: " + settings['human']['name'])


    (F, F2, C, C2) = init_curves()
    g_raw = settings['crypto']['g']
    h_raw = settings['crypto']['h']
    g1_raw = settings['crypto']['g1']
    h1_raw = settings['crypto']['h1']
    g_coord = [F(g_raw['coord'][0]), F(g_raw['coord'][1])]
    h_coord = [F2(h_raw['coord'][0]), F2(h_raw['coord'][1])]
    g1_coord = [F(g1_raw['coord'][0]), F(g1_raw['coord'][1])]
    h1_coord = [F2(h1_raw['coord'][0]), F2(h1_raw['coord'][1])]
    g = C(g_coord, representation = g_raw['repr'])
    g1 = C(g1_coord, representation = g1_raw['repr'])
    h = C2(h_coord, representation = h_raw['repr'])
    h1 = C2(h1_coord, representation = h1_raw['repr'])

    c0_raw = ballot['ciphertext']['c0']
    c1_raw = ballot['ciphertext']['c1']
    c2_raw = ballot['ciphertext']['c2']
    c0_coord = [F(c0_raw['coord'][0]), F(c0_raw['coord'][1])]
    c1_coord = [F(c1_raw['coord'][0]), F(c1_raw['coord'][1])]
    c2_coord = [F2(c2_raw['coord'][0]), F2(c2_raw['coord'][1])]
    c0 = C(c0_coord, representation = c0_raw['repr'])
    c1 = C(c1_coord, representation = c1_raw['repr'])
    c2 = C2(c2_coord, representation = c2_raw['repr'])

    sigmacc_raw = ballot['proofs']['sigmacc']
    sigmaor_raw = ballot['proofs']['sigmaor']
    #FIXME check la conversion de sigma cc et sigma or
    sigmacc = sigmacc_raw
    sigmaor = sigmaor_raw

    if (ccsva_extrip(c0, c1, c2, sigmacc, sigmaor, g, h, g1, h1) == True):

        #moves the full ballot to SB
        move(ballot, election_folder + "sb/" + ballot_fingerprint + ".bal.json")

        #appends the public commitment on PB
        #(c2b, sigmaorb) = ccsva_extract_c(c0, c1, c2, sigmacc, sigmaor)
        public_ballot = json.dumps({'c2' : c2_raw, #c2b.json(),
                                    'sigmaor': sigmaor_raw}, #sigmaorb.json()},
                                   indent = 4)
        filedes = open(election_folder + "pb/" + ballot_fingerprint \
                       + ".bal.json", "w")
        filedes.write(public_ballot)
        filedes.close()

        print("Ballot accepted and stored!")
    else:
        print("Refused ballot!")
        exit(1)
    exit(0)

if __name__ == '__main__':
    if(sys.argv.__len__() != 4):
        print("Incorrect argument number! \n    \
        USAGE: ./accept_ballot.py <settings.pub.json> <ballot.bal.json> \
        <election_folder.edata")
        exit(1)
    main(sys.argv[1], sys.argv[2], sys.argv[3])
