# -*- coding: utf-8 -*-
''' euclide.py

This module contains extended euclidean algorithm. It calculates the GCD of two 
integers. GCD algorithm can be used in order to compute multiplicative modular 
inverses.
 
Source: 
http://en.wikibooks.org/w/index.php?title=Algorithm_Implementation/Mathematics/
Extended_Euclidean_algorithm&oldid=1971523
Wikibooks is published under GNU Free Documentation License and Creative 
Commons Attribution-ShareAlike 3.0 License
'''


def modinv(a, m):
    '''Inverts integer a wrt modulus m, such as a^(-1) = x % m.
    This algorithm returns x, also known as modular inverse of a.'''
    g, x, _ = egcd_iter(a, m)
    if g != 1:
        return None  # modular inverse does not exist
    else:
        return x % m


def egcd_iter(a, b):
    '''Computes GCD between a and b, in an iterative way.'''
    x, y, u, v = 0, 1, 1, 0
    while a != 0:
        q, r = b / a, b % a
        m, n = x - u * q, y - v * q
        b, a, x, y, u, v = a, r, u, v, m, n
    return b, x, y


def egcd_rec(a, b):
    '''Computes GCD between a and b, in a recursive way.'''
    if a == 0:
        return (b, 0, 1)
    else:
        g, y, x = egcd_rec(b % a, a)
        return (g, x - (b // a) * y, y)
