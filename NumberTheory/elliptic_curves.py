# -*- coding: utf-8 -*-
''' elliptic_curves.py

This module contains the implementation of an elliptic curve over a field

@author: Richard Mathot
'''

def EC(field, order):
    '''Wrapper to generate elements of the same curve, over the same field'''
    def __generator(coordinates, representation = 'affine', infinite = False,
                    random = False):
        '''A function to generate elements in finite field of prime order'''
        return EllipticCurvePoint(field, order, coordinates, representation,
                                  infinite, random)
    return __generator


class EllipticCurvePoint(object):
    '''A point of an elliptic curve defined over a field'''

    field = None
    order = None
    coordinates = None
    representation = None
    infinite = False

    def __init__(self, field, order, coordinates, representation = 'affine',
                 infinite = False, random = False):
        '''Constructs an element on an elliptic curve of order, over field, with 
        coordinates and representation selected (affine is default).
        @note: Coordinates is a list of FIELD ELEMENTS (not integers!)
        If infinite = True: returns the point at infinity and coordinates will 
                            be ignored
        If random = True: returns a random point in affine on the curve and 
                          coordinates and representation will be ignored'''
        self.field = field
        assert order > 1
        self.order = order
        assert (representation == 'affine') | (representation == 'jacobian')
        self.representation = representation
        if infinite:
            self.infinite = True
            self.coordinates = None
            return
        self.infinite = False
        if random:
            self.coordinates = self._generate_random_coordinates()
            self.representation = 'affine'
            return
        self.coordinates = coordinates


    def copy(self):
        '''Return an object that is the clone of self'''
        return EllipticCurvePoint(self.field, self.order, self.coordinates,
                                  self.representation, infinite = self.infinite)

    def jacobian(self):
        '''Converts coordinates to jacobian (creates a new object)'''
        if self.representation == 'jacobian':
            return self.copy()
        else:
            if self.infinite:
                return EllipticCurvePoint(self.field, self.order, None,
                                         representation = 'jacobian',
                                         infinite = True)
            else:
                if self.coordinates[0].exp == 1: #Prime field F_p
                    one = self.field(1)
                elif self.coordinates[0].exp == 2: #Extension field F_p^2
                    one = self.field([0, 1])
                else:
                    raise Exception("not implemented")
                return EllipticCurvePoint(self.field, self.order,
                                          [self.coordinates[0],
                                           self.coordinates[1],
                                           one],
                                          representation = 'jacobian')

    def affine(self):
        ''''''
        if self.representation == 'affine':
            return self.copy()
        else:
            if self.infinite:
                return EllipticCurvePoint(self.field, self.order, None,
                                         representation = 'affine',
                                         infinite = True)
            else:
                invZ2 = ~(self.coordinates[2] ** 2)
                invZ3 = ~(self.coordinates[2] ** 3)
                x = self.coordinates[0] * invZ2
                y = self.coordinates[1] * invZ3
                return EllipticCurvePoint(self.field, self.order, [x, y],
                                          representation = 'affine')

    def __add__(self, Q):
        '''
        Jacobian addition algorithm for curves of the form y^2 = x^3 + b (a==0)
        http://hyperelliptic.org/EFD/g1p/auto-shortw-jacobian-0.html#addition-add-2007-bl
        '''
        # The algorithm above won't work for P + P (redirecting to doubling!)
        if self == Q:
            return self.__double__()

        P = self.jacobian()
        S = Q.jacobian()

        #  P + inf = P = inf + P
        if P.infinite:
            return S.copy()
        if S.infinite:
            return P.copy()

        X1 = P.coordinates[0]
        Y1 = P.coordinates[1]
        Z1 = P.coordinates[2]
        X2 = S.coordinates[0]
        Y2 = S.coordinates[1]
        Z2 = S.coordinates[2]
        if self.coordinates[0].exp == 1: #Prime field F_p
            two = self.field(2)
        elif self.coordinates[0].exp == 2: #Extension field F_p^2
            two = self.field([0, 2])
        else:
            raise Exception("not implemented")

        Z1Z1 = Z1 ** 2
        Z2Z2 = Z2 ** 2
        U1 = X1 * Z2Z2
        U2 = X2 * Z1Z1
        S1 = Y1 * Z2 * Z2Z2
        S2 = Y2 * Z1 * Z1Z1
        H = U2 - U1
        I = (H * two) ** 2
        J = H * I
        r = (S2 - S1) * two
        V = U1 * I
        X3 = (r ** 2) - J - (V * two)
        Y3 = r * (V - X3) - two * S1 * J
        Z3 = (((Z1 + Z2) ** 2) - Z1Z1 - Z2Z2) * H
        return (EllipticCurvePoint(self.field, self.order, [X3, Y3, Z3],
                                          representation = 'jacobian'))

    def __sub__(self, Q):
        R = Q.affine()
        minusR = EllipticCurvePoint(self.field, self.order,
                                     [R.coordinates[0], -R.coordinates[1]],
                                     representation = 'affine')
        return self +minusR

    def __double__(self):
        #pylint: disable=R0914
        '''
        Jacobian doubling algorithm for curves of the form y^2 = x^3 + b (a==0)
        http://hyperelliptic.org/EFD/g1p/auto-shortw-jacobian-0.html#doubling-dbl-2009-l
        '''
        P = self.jacobian()

        if P.infinite:
            return P

        X1 = P.coordinates[0]
        Y1 = P.coordinates[1]
        Z1 = P.coordinates[2]

        if self.coordinates[0].exp == 1: #Prime field F_p
            two = self.field(2)
            three = self.field(3)
            eight = self.field(8)
        elif self.coordinates[0].exp == 2: #Extension field F_p^2
            two = self.field([0, 2])
            three = self.field([0, 3])
            eight = self.field([0, 8])
        else:
            raise Exception("not implemented")

        A = X1 ** 2
        B = Y1 ** 2
        C = B ** 2
        D = two * ((X1 + B) ** 2 - A - C)
        E = three * A
        F = E ** 2
        X3 = F - two * D
        Y3 = E * (D - X3) - eight * C
        Z3 = two * Y1 * Z1
        return EllipticCurvePoint(self.field, self.order, [X3, Y3, Z3],
                                          representation = 'jacobian')

    def __mul__(self, k):
        '''Jacobian multiplication by a scalar k for curves of the form 
        y^2 = x^3 + P (a==0)
        This algorithm exploits doubling in order to perform point 
        multiplication ("double-and-add" algorithm).
        '''
        assert k > 0
        if k == 1:
            return self.jacobian()
        elif k == 2:
            return self.__double__()
        else:
            P = self.jacobian()
            R = EllipticCurvePoint(self.field, self.order, None,
                                   representation = 'jacobian', infinite = True)
            n = k
            while(n > 0):
                if n % 2:
                    R = R + P
                P = P.__double__()
                n = n / 2
            return R

    def __eq__(self, b):
        ''''''
        if self.infinite | b.infinite:
            return self.infinite & b.infinite
        P = self.affine()
        Q2 = b.affine()
        return (P.coordinates[0] == Q2.coordinates[0]) \
               & (P.coordinates[1] == Q2.coordinates[1])

    def is_infinite(self):
        return self.infinite

    def _generate_random_coordinates(self):
        ''''''
        while True:
            y = self.field(0, rand = True)

            if y.exp == 1: #Prime field F_p
                a = y ** 2 - self.field(3)
                x = a ** ((2 * y.order + 1) / 9)
                check = (y ** 2 == (x ** 3 + self.field(3)))
                if check:
                    break
            if y.exp == 2: #Extension field F_p^2
                a = y ** 2 - self.field([0, 3])
                x = a ** (((y.order ** 2) + 2) / 9)
                check = (y ** 2 == (x ** 3 + self.field([0, 3])))
                if check:
                    break
        return [x, y]

    def __repr__(self):
        ''''''
        if self.infinite:
            return "∞ (point at infinity)"
        else:
            return self.coordinates.__repr__() \

    def json(self):
        ''''''
        if self.infinite:
            return {}
        else:
            R = self.affine()
            return {'repr' : R.representation,
                    'coord' : [R.coordinates[0].json(), R.coordinates[1].json()]}
