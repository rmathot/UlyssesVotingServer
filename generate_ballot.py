#!/usr/bin/python -OO
# -*- coding: utf-8 -*-

'''
This tool is part of UlyssesVoting and can be used to generate a valid ballot.

@author: Richard Mathot
'''

import json
import sys
# pylint: disable=E0611
from hashlib import sha256
from Crypto.ccs_va import init_curves, ccsva_enc


#pylint: disable=R0914
def main(election_folder):
    '''Launch interactive ballot generation'''
    print("Welcome into the Ballot Generation Tool")

    raw_input("Press <ENTER> to start loading election settings...")
    print("Loading...")

    filedes = open(election_folder + election_folder[:-7] + ".pub.json", 'r')
    settings_raw = filedes.read()
    filedes.close()

    election_fingerprint = sha256(settings_raw).hexdigest()
    print("Election hash (sha256): " + election_fingerprint)

    settings = json.loads(settings_raw)
    print("Election name: " + settings['human']['name'])

    print("Loading successful!")

    (F, F2, C, C2) = init_curves()
    g_raw = settings['crypto']['g']
    h_raw = settings['crypto']['h']
    g1_raw = settings['crypto']['g1']
    h1_raw = settings['crypto']['h1']

    hx = [int(i) for i in h_raw['coord'][0]]
    hy = [int(i) for i in h_raw['coord'][1]]
    h1x = [int(i) for i in h1_raw['coord'][0]]
    h1y = [int(i) for i in h1_raw['coord'][1]]

    g_coord = [F(int(g_raw['coord'][0])), F(int(g_raw['coord'][1]))]
    g1_coord = [F(int(g1_raw['coord'][0])), F(int(g1_raw['coord'][1]))]
    h_coord = [F2(hx), F2(hy)]
    h1_coord = [F2(h1x), F2(h1y)]
    g = C(g_coord, representation = g_raw['repr'])
    g1 = C(g1_coord, representation = g1_raw['repr'])
    h = C2(h_coord, representation = h_raw['repr'])
    h1 = C2(h1_coord, representation = h1_raw['repr'])

    raw_input("Press <ENTER> to continue...")

    print("QUESTION: " + settings['human']['question'])
    print("ANSWER 0: " + settings['human']['answer_0'])
    print("ANSWER 1: " + settings['human']['answer_1'])

    vote = -1

    while (vote != 0) & (vote != 1) :
        try:
            v = int(raw_input("Please pick a choice (0 or 1) and press <ENTER>... "))
        except(ValueError): # Catch inputs that are not integers
            continue
        vote = v

    print("Encrypting ballot. This may take some time...")
    ((c0, c1, c2), sigmacc, sigmaor) = ccsva_enc(vote, g, g1, h, h1)

    # Encode ballot in JSON
    ballot_content = json.dumps({'ciphertext' : {'c0' : c0.json(),
                                               'c1' : c1.json(),
                                               'c2' : c2.json()},
                                'proofs' :{'sigmacc' : sigmacc,
                                           'sigmaor': sigmaor}},
                                indent = 4)

    print("Ballot encrypted!")

    # Compute ballot hash
    ballot_fingerprint = sha256(ballot_content).hexdigest()

    # Save ballot to a file
    filedes = open(election_folder + ballot_fingerprint + ".bal.json", "w")
    filedes.write(ballot_content)
    filedes.close()

    print("Ballot hash (sha256): " + ballot_fingerprint)
    print("This ballot is in " + election_folder + ballot_fingerprint \
          + ".pub.json")

    sys.exit(0)


if __name__ == '__main__':
    if(sys.argv.__len__() != 2):
        print("Incorrect argument number! \n    \
        USAGE: ./generate_ballot.py <election_folder.edata>")
        sys.exit(1)
    main(sys.argv[1])
