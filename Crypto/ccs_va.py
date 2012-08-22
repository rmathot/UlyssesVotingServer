# -*- coding: utf-8 -*-
''' ccs_va.py

Commitment Consistent Cryptosystem (CCS) with validity augmentations
This cryptosystem is the combination of a traditional Elgamal encryption system
with a perfectly hiding commitment.

@author: Richard Mathot
'''

from base64 import b64encode
# pylint: disable=E0611
from hashlib import sha256
from NumberTheory.finite_fields import PF, PF2
from NumberTheory.pairings import pairing
from Random.random_sources import randint
from NumberTheory.bn_curve import p_u_, n_u_
from NumberTheory.elliptic_curves import EC


def init_curves():
    F = PF(p_u_)
    F2 = PF2(p_u_)
    C = EC(F, n_u_)
    C2 = EC(F2, n_u_)
    return (F, F2, C, C2)

def ccs_gen():
    ''' Key generator for CCS Cryptosystem 
        
        This algorithms selects:
        - two public generators g and h
        - the public key g1 and h1
        - the private key x1 
    '''

    # Curve initialisation
    (_, _, C, C2) = init_curves()

    # Keys generation
    g = C(None, representation = 'affine', infinite = False, random = True)
    h = C2(None, representation = 'affine', infinite = False, random = True)
    x1 = randint(n_u_ - 1)
    g1 = g * x1
    h1 = C2(None, representation = 'affine', infinite = False, random = True)

    return ((g.affine(), h.affine(), g1.affine(), h1.affine()), x1) # (pk, sk)


def ccs_enc(m, r, s, g, h, g1, h1):
    ''' Encryption for CCS Cryptosystem 
        
        Inputs:
        - m the message to encrypt and to commit on(0 or 1)
        - r, s two random numbers in [0, n_u_ - 1]
        - g, h, g1, h1, the public key
    '''

    assert m == 0 | m == 1

    c0 = g * s
    c1 = g * r + g1 * s
    c2 = h * r + h1 * m

    return (c0.affine(), c1.affine(), c2.affine())


def ccs_dec(c0, c1, c2, g, h, h1, x1):
    ''' Decryption for CCS Cryptosystem '''
    basis = pairing(g, h1)
    ct = pairing(c0 * x1 + ~c1, h) + pairing(g, c2)
    # Addition ou multiplication entre les deux pairings ?
    # TODO addition j'espère car sinon faut implémenter * dans F_12 :S
    m = __dlog(ct, basis)
    return m


def ccs_extract_c(c0, c1, c2):
    #pylint: disable=W0613
    ''' Extraction of the commitment '''
    return c2


def ccs_extract_e(c0, c1, c2):
    #pylint: disable=W0613
    ''' Extraction of the Elgamal encryption of the opening value of c2 '''
    return (c0, c1)


def ccs_open(m, a, c2, g, h, h1):
    if pairing(a, h) == pairing(g, c2 + ~(h1 * m)):
        return m
    else:
        return None


def elgamal_dec(c0, c1, x1):
    '''Classical Elgamal decryption'''
    return c1 - (c0 * x1)


def ccsva_gen():
    return ccs_gen()


def ccsva_enc(m, g, g1, h, h1):
    r = randint(n_u_)
    s = randint(n_u_)
    c = (c0, c1, c2) = ccs_enc(m, r, s, g, h, g1, h1)
    sigmacc = (ecc, zm, zr, zs) = __compute_cc_proof(m, r, s, c, g, h, g1, h1)
    sigmaor = (e0, e1, t0, t1) = __compute_or_proof(m, c2, s, h, g1, h1)
    return (c, sigmacc, sigmaor)


def ccsva_dec(c0, c1, c2, sigmacc, sigmaor, g, h, g1, h1, x1):
    (ecc, zm, zr, zs) = sigmacc
    (e0, e1, t0, t1) = sigmaor
    if __check_cc_proof(c0, c1, c2, ecc, zm, zr, zs, g, h, g1, h1) \
                        & __check_or_proof(e0, e1, t0, t1, c2, h, g1, h1):
        return ccs_dec(c0, c1, c2, g, h, h1, x1)
    else:
        return None


def ccsva_extract_e(c0, c1, c2, sigmacc, sigmaor):
    return ccs_extract_e(c0, c1, c2)


def ccsva_open(m, a, c2, g, h, h1):
    return ccs_open(m, a, c2, g, h, h1)


def ccsva_extrip(c0, c1, c2, sigmacc, sigmaor, g, h, g1, h1):
    (ecc, zm, zr, zs) = sigmacc
    (e0, e1, t0, t1) = sigmaor
    if __check_cc_proof(c0, c1, c2, ecc, zm, zr, zs, g, h, g1, h1) \
                        & __check_or_proof(e0, e1, t0, t1, c2, h, g1, h1):
        return True
    else:
        return None


def ccsva_extract_c(c0, c1, c2, sigmacc, sigmaor):
    return (ccs_extract_c(c0, c1, c2), sigmaor)


def ccsva_strip(c2, sigmaor, h, g1, h1):
    (e0, e1, t0, t1) = sigmaor
    if __check_or_proof(e0, e1, t0, t1, c2, h, g1, h1):
        return c2
    else:
        return None


def __dlog(x, y):
    '''Discrete logarithm extraction 
    If x = y ^ z, performs an exhaustive search to find z'''

    z = 1 #initialisé à 0 ou à 1 ?
    accy = y
    notfound = True
    while notfound:
        if accy == x:
            notfound = False
        else:
            accy = accy * y
            z = z + 1
    return z


def __compute_cc_proof(m, r, s, c, g, h, g1, h1):
    j = randint(n_u_ - 1)
    u = randint(n_u_ - 1)
    v = randint(n_u_ - 1)

    d = ccs_enc(j, u, v, g, h, g1, h1)

    longstring = g1.__repr__() + h1.__repr__() + c.__repr__() + d.__repr__()
    ecc = int((sha256(longstring).hexdigest()), 16)
    # TODO faut il faire modulo n_u_ ?

    (zm, zr, zs) = (j + ecc * m, u + ecc * r, v + ecc * s)

    return (ecc, zm, zr, zs)


def __compute_or_proof(m, c2, s, h, g1, h1):
    assert m == 0 | m == 1

    e0, e1, t0, t1, w0, w1 = None, None, None, None, None, None
    b = randint(n_u_ - 1)

    if m == 0:
        e1 = randint(n_u_ - 1)
        t1 = randint(n_u_ - 1)
        w0 = h * b
        w1 = h * t1 + (c2 - (h1 * 1)) * (-e1)
        longstring = g1.__repr__() + h1.__repr__() + c2.__repr__() + w0.__repr__() + w1.__repr__()
        e0 = int((sha256(longstring).hexdigest()), 16) - e1
        # TODO faut il faire modulo n_u_ ?
        t0 = b + e0 * s

    else:
        e0 = randint(n_u_ - 1)
        t0 = randint(n_u_ - 1)
        w1 = h * b
        w0 = h * t0 + (c2 - (h1 * 0)) * (-e0)
        longstring = g1.__repr__() + h1.__repr__() + c2.__repr__() + w0.__repr__() + w1.__repr__()
        e0 = int((sha256(longstring).hexdigest()), 16) - e0
        # TODO faut il faire modulo n_u_ ?
        t1 = b + e1 * s

    return (e0, e1, t0, t1)


def __check_cc_proof(c0, c1, c2, ecc, zm, zr, zs, g, h, g1, h1):
    (tmp0, tmp1, tmp2) = ccs_enc(zm, zr, zs, g, h, g1, h1)
    d = (d0, d1, d2) = (tmp0 * c0 - ecc, tmp1 * c1 - ecc, tmp2 * c2 - ecc)
    if ecc == b64encode(sha256(g1, h1, (c0, c1, c2), d).digest()):
        return True
    else:
        return None


def __check_or_proof(e0, e1, t0, t1, c2, h, g1, h1):
    w0 = h * t0 + (c2 + ~h1 * 0) * (-e0)
    w1 = h * t1 + (c2 + ~h1 * 1) * (-e1)
    w = (w0, w1)

    left = e0 + e1
    right = b64encode(sha256(g1, h1, c2, w).digest())

    if left == right:
        return True
    else:
        return None
