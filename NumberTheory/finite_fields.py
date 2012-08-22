# -*- coding: utf-8 -*-
''' finite_fields.py 

This module contains implementations of field arithmetic, for both prime and
extended fields (F_p, F_{p^2} and parts of F_{p^12}).

@author: Richard Mathot
'''

from itertools import izip
from NumberTheory.euclide import modinv
from Random.random_sources import get_256_random_bits_os

####################
# Prime Fields F_p #
####################

def PF(order):
    '''Wrapper to generate elements of the same field'''
    def __generator(value, rand = False):
        '''A function to generate elements in finite field of prime order'''
        return PrimeField(value, order, rand)
    return __generator


#pylint: disable=R0903
class PrimeField(object):
    '''A Galois finite field F_p of prime order p'''

    value = None
    order = None
    exp = 1
    inverse = None

    def __init__(self, value, order, rand = False):
        '''Creates an element value in the field F_order.
        If rand parameter is set to True, value will be ignored and a random 
        element of the field will be returned. 
        @note: Ensuring that order is prime is programmer responsibility!  
        '''
        assert order > 1
        if rand:
            self.value = get_256_random_bits_os() % order
        else:
            self.value = value % order
        self.order = order


    def __add__(self, b):
        '''Addition modulo order (redefinition of operator '+')'''
        assert self.order == b.order
        return PrimeField(self.value + b.value, self.order)

    def __sub__(self, b):
        '''Substraction modulo order (redefinition of operator '-')'''
        assert self.order == b.order
        return PrimeField(self.value - b.value, self.order)

    def __mul__(self, b):
        '''Multiplication modulo order (redefinition of operator '*')'''
        assert self.order == b.order
        return PrimeField(self.value * b.value, self.order)

    def scalmul(self, i):
        return PrimeField(self.value * i, self.order)

    def __pow__(self, m):
        '''Exponentiation modulo order (redefinition of operator '**')'''
        assert m > -2
        if m == -1:
            return self.__invert__()
        if m == 0:
            return PrimeField(1, self.order)
        if m == 1:
            return self
        else:
            return PrimeField(pow(self.value, m, self.order), self.order)

    def __invert__(self):
        '''Inversion modulo order (redefinition of operator '~')
        @note: This method caches modular inverse, so modifying value of X 
        directly with 'X.value = ...' can lead to incoherent inversion.
        '''
        if self.inverse == None: # caching inverse value (speed optimization)
            self.inverse = PrimeField(modinv(self.value, self.order),
                                      self.order)
        return self.inverse

    def __neg__(self):
        return PrimeField(-self.value, self.order)

    def __eq__(self, Q):
        assert self.order == Q.order
        return self.value == Q.value

    def __long__(self):
        return long(self.value)

    def __hex__(self):
        return hex(self.value)

    def __repr__(self):
        return "F_p: " + self.value.__repr__()

    def is_zero(self):
        return self.value == 0

    def is_one(self):
        return self.value == 1

    def json(self):
        return self.value.__str__()

##########################
# Extension Fields F_p^2 #
##########################

def PF2(order):
    '''Wrapper to generate elements of the same field'''
    def __generator(value, rand = False):
        '''A function to generate elements in finite field of prime order'''
        return PrimeField2(value, order, rand)
    return __generator


class PrimeField2(object):
    '''A Galois finite field F_p^2'''

    value = None
    order = None
    exp = 2
    orderexp = None

    def __init__(self, value, order, rand = False):
        '''Creates an element value in the field F_order^2.
        value must be an array [c,d] that describes polynomial cx + d
        If rand parameter is set to True, value will be ignored and a random 
        element of the field will be returned. 
        @note: Ensuring that order is prime is programmer responsibility!  
        '''
        assert order > 1
        if rand:
            self.value = [get_256_random_bits_os() % order,
                          get_256_random_bits_os() % order]
        else:
            self.value = [value[0] % order, value[1] % order]
        self.order = order
        self.orderexp = order ** self.exp

    def __add__(self, b):
        '''Addition (redefinition of operator '+')'''
        assert self.order == b.order
        return PrimeField2([self.value[0] + b.value[0],
                           self.value[1] + b.value[1]], self.order)

    def __sub__(self, b):
        '''Substraction (redefinition of operator '-')'''
        assert self.order == b.order
        return PrimeField2([self.value[0] - b.value[0],
                           self.value[1] - b.value[1]], self.order)

    def __mul__(self, b):
        '''Multiplication (redefinition of operator '*')
        
            We will multiply P(x)=ax+b and Q(x)=cx+d and reduce this product
            modulo I(x)=x^2+1 
            
            For fields of size p^m with m == 2, this can be reduced to compute 
            this new polynomial R(x) = [ad + bc]x + [bd-ac] 
        '''
        assert self.order == b.order
        assert self.exp == b.exp

        #pylint:disable=C0301
        return PrimeField2([self.value[0] * b.value[1] + self.value[1] * b.value[0],
                            self.value[1] * b.value[1] - self.value[0] * b.value[0]],
                          self.order)

    def scalmul(self, i):
        return PrimeField2([self.value[0] * i, self.value[1] * i], self.order)

    def __invert__(self):
        '''Inversion  (redefinition of operator '~')
        
            If [A(x) * B(x) mod P(x)=x^2+1] == 1, then computes 
            B(x) for a given A(x).
            
            Direct inversion algorithm
        '''
        delta = self.value[1] ** 2 + self.value[0] ** 2
        deltaInv = modinv(delta, self.order)
        return PrimeField2([(-self.value[0]) * deltaInv,
                            self.value[1] * deltaInv],
                           self.order)

    def __pow__(self, m):
        '''Exponentiation (redefinition of operator '**')'''
        assert m > -2
        if m == -1:
            return self.__invert__()
        if m == 0:
            return PrimeField2([0, 1], self.order)
        if m == 1:
            return self
        else:
            base = PrimeField2(self.value, self.order)
            ret = PrimeField2([0, 1], self.order)
            n = m
            while(n > 0):
                if (n % 2):
                    ret = ret * base
                base = base * base
                n = n / 2
            return ret

    def __neg__(self):
        return PrimeField2([-self.value[0], -self.value[1]], self.order)

    def __eq__(self, Q):
        assert self.order == Q.order
        return (self.value[0] == Q.value[0]) & (self.value[1] == Q.value[1])

    def __repr__(self):
        return "F_p^2: " + self.value.__repr__()

    def is_zero(self):
        return (self.value[0] == 0) & (self.value[1] == 0)

    def is_one(self):
        return (self.value[0] == 0) & (self.value[1] == 1)

    def json(self):
        return [self.value[0].__str__(), self.value[1].__str__()]

#===============================================================================
#    def divide_v(self):
#        qre = (self.value[1] + self.value[0]) % self.order
#        qim = (self.value[0] - self.value[1]) % self.order
#
#        re = qre
#        im = qim
#
#        if (bin(qre)[2:])[-1] == '1':
#            re = (qre + self.order)
#        if (bin(qim)[2:])[-1] == '1':
#            im = (qim + self.order)
#
#        return PrimeField2([im >> 1, re >> 1], self.order)
#===============================================================================


###########################
# Extension Fields F_p^12 #
###########################

def PF12(order):
    '''Wrapper to generate elements of the same field'''
    def __generator(value, one = False):
        '''A function to generate elements in finite field of prime order ^ 12
        
        value must be an array of PrimeField2 and len(value) == 6
        '''
        return PrimeField12(value, order, one)
    return __generator


class PrimeField12(object):

    value = None
    order = None
    exp = 12

    def __init__(self, value, order, one = False):
        if one:
            self.value = [PrimeField2([0, 1], order),
                          PrimeField2([0, 0], order),
                          PrimeField2([0, 0], order),
                          PrimeField2([0, 0], order),
                          PrimeField2([0, 0], order),
                          PrimeField2([0, 0], order)]
        else:
            assert len(value) == 6
            self.value = value
        self.order = order

    def __add__(self, b):
        assert self.order == b.order
        return PrimeField12([self.value[0] + b.value[0],
                           self.value[1] + b.value[1],
                           self.value[2] + b.value[2],
                           self.value[3] + b.value[3],
                           self.value[4] + b.value[4],
                           self.value[5] + b.value[5]], self.order)

    def __mul__(self, c):
        assert self.order == c.order
        assert self.exp == c.exp

        # Useful variables
        zero = PrimeField2([0, 0], self.order)
        one = PrimeField2([0, 1], self.order)

        # Trivial cases
        if (self.is_one()) | (c.is_zero()):
            return c
        if (self.is_zero()) | (c.is_one()):
            return self

        # Product scanning multiplication
        v = [zero, zero, zero, zero, zero, zero, zero, zero, zero, zero, zero]
        assert len(v) == 11

        a = self.value
        b = c.value
        assert len(a) == 6
        assert len(b) == 6

        for i in range (0, 11):
            for j in range(0, 6):
                for k in range(0, 6):
                    if i == (j + k):
                        v[i] = v[i] + (a[j] * b[k])

        # Modular réduction by x^6 - \xi
        # This part of the code is largely inspirated from
        # http://rosettacode.org/wiki/Polynomial_long_division#Python
        #
        # We want to reduce the vector v computed hereunder
        # by x^6 - \xi
        def _deg(P):
            '''Computes the degree of a polynom'''
            for i in range(1, len(P) + 1):
                if (P[-i].is_zero() != True):
                    return len(P) - i
            return -1
        def _sub(P, Q):
            assert len(P) == len(Q)
            assert len(P) > 0
            x = []
            for i in range(0, len(P)):
                x.extend([P[i] - Q[i]])
            return x
        def _mul(P, k):
            assert len(P) > 0
            R = []
            for i in range(0, len(P)):
                R.extend([P[i] * k])
            return R

        xi = PrimeField2([36185027886660917772715175388897419393242461986175376624593877975821770161926,
                          36185027886660917772715175388897419393242461986175376624593877975821770161926],
                         self.order)
        modulo = [xi, zero, zero, zero, zero, zero, one]

        degV = _deg(v)
        degmod = _deg(modulo)

        if degmod < 0:
            raise Exception("Polynomial reduction needs a non-null modulo!")
        if degV >= degmod:
            q = [zero] * degV
            while degV >= degmod:
                d = ([zero] * (degV - degmod)) + modulo
                mult = q[degV - degmod] = v[-1] * (~d[-1])
                d = _mul(d, mult)
                v = [(coeffv - coeffd) for coeffv, coeffd in izip(v, d)]
                degV = _deg(v)
            r = v
        else:
            q = 0
            r = v

        return PrimeField12(r[0:6], self.order)

    def scalmul(self, k):
        return PrimeField12([self.value[0].scalmul(k),
                            self.value[1].scalmul(k),
                            self.value[2].scalmul(k),
                            self.value[3].scalmul(k),
                            self.value[4].scalmul(k),
                            self.value[5].scalmul(k)], self.order)


    def __pow__(self, m):
        assert m > -1
        #if m == -1:
        #    return self.__invert__()
        if m == 0:
            return PrimeField12(None, self.order, one = True)
        if m == 1:
            return self
        else:
            base = PrimeField12(self.value, self.order)
            ret = PrimeField12(None, self.order, one = True)
            n = m
            while(n > 0):
                if (n % 2):
                    ret = ret * base
                base = base * base
                n = n / 2
            return ret

    #def __invert__(self):
    #    pass                  #Not neeeded yet

    def __eq__(self, b):
        assert self.order == b.order
        assert self.exp == b.exp
        return (self.value[0] == b.value[0]) & \
                (self.value[1] == b.value[1]) & \
                (self.value[2] == b.value[2]) & \
                (self.value[3] == b.value[3]) & \
                (self.value[4] == b.value[4]) & \
                (self.value[5] == b.value[5])

    def __repr__(self):
        return "F_p^12: " + self.value.__repr__()


    def is_zero(self):
        return (self.value[0].is_zero()) & \
                (self.value[1].is_zero()) & \
                (self.value[2].is_zero()) & \
                (self.value[3].is_zero()) & \
                (self.value[4].is_zero()) & \
                (self.value[5].is_zero())

    def is_one(self):
        return (self.value[0].is_one()) & \
                (self.value[1].is_zero()) & \
                (self.value[2].is_zero()) & \
                (self.value[3].is_zero()) & \
                (self.value[4].is_zero()) & \
                (self.value[5].is_zero())

