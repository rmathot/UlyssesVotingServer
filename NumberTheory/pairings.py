# -*- coding: utf-8 -*-
'''
Pairings implementations
'''

from NumberTheory.bn_curve import n_u_, p_u_, number_of_bits, bigexpo
from NumberTheory.finite_fields import PF12, PF2
import time

def pairing(P, Q):
    '''Wrapper function that allows the developper to select a pairing without 
    modifiying the whole code'''
    return tate_pairing(P, Q)
    #return optimal_ate_pairing(P, Q)

def tate_pairing(P2, Q2):
    ''' The Tate Pairing

        P2 belongs to G_1
        Q2 belongs to G_2

        G_1    x G_2      -> G_T
        E(F_p) x E2(F_p²) -> F_p¹² 
        
        Algorithm from:
        Augusto Jun Devegili, Michael Scott and Ricardo Dahab, "Implementing 
        Cryptographic Pairings over Barreto-Naehrig Curves", 2007.
        
        @note: This implementation does not claim any efficiency goal (if you 
        are looking for an efficient pairing, Tate pairing is probably NOT a 
        good choice!).
    '''

    F12 = PF12(p_u_)
    one = F12(None, one = True)

    P = P2.affine()
    Q = Q2.affine()

    t0 = time.time()

    if((P.is_infinite() == False) & (Q.is_infinite() == False)):

        cord_len = number_of_bits
        cord_bits = bin(n_u_)[2:]
        V = P
        r = one

        i = cord_len - 2

        while(i >= 0): # Miller loop

            r = (r ** 2) * gl(V, V, Q)
            V = V * 2

            if(cord_bits[-(i + 1)] == '1'):

                r = r * gl(V, P, Q)
                V = V + P

            i = i - 1

        pairing_output = r ** bigexpo # Final exponentiation

        t1 = time.time()
        print("DEBUG - Time for pairing:" + (t1 - t0).__str__())

        return pairing_output

    else:
        raise Exception("You cannot compute a pairing on point at infinity")


def gl(A, B, C):
    '''Auxiliary function for tate_pairing
       
       V, P and Q have to be expressed in projective coordinates'''

    F12 = PF12(p_u_)
    F2 = PF2(p_u_)
    one = F12(None, one = True)
    w = [None, None, None, None, None, None]

    V = A.jacobian()
    P = B.jacobian()
    Q = C.jacobian()

    if (V.is_infinite() | P.is_infinite() | Q.is_infinite()):
        return one

    Vz3 = V.coordinates[2] ** 3

    if V == P:
        n = (V.coordinates[0] ** 2).scalmul(3)
        d = (V.coordinates[1] * V.coordinates[2]).scalmul(2)
    else:
        assert P.coordinates[2].value == 1
        n = P.coordinates[1] * Vz3 - V.coordinates[1]
        d = P.coordinates[0] * Vz3 - (V.coordinates[0] * V.coordinates[2])

    w[1] = w[4] = w[5] = F2([0, 0])
    w[0] = F2([0, ((d * V.coordinates[1]) - (n * V.coordinates[0] * V.coordinates[2])).value])
    w[2] = Q.coordinates[0].scalmul((n * Vz3).value)
    w[3] = Q.coordinates[1].scalmul((Vz3.scalmul((p_u_ - d.value))).value)

    return F12(w)


#def optimal_ate_pairing(P, Q):
#    pass                        #Not Yet Implemented
