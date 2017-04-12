# -*- coding: utf-8 -*-
'''Classic seismic ray theory for layered models

'''

import cmath
import numpy as np

def sin2cos(x):
    return cmath.sqrt(1.-x**2)

class Material(object):

    def __init__(self, vp, vs, rho, qp=None, qs=None):
        self.vp = vp
        self.vs = vs
        self.rho = rho

class Discontinuity(object):

    def __init__(self, material1=None, material2=None):
        self.above = material1
        self.below = material2

    def psv_solid_solid(self, p):
        '''

        :param p:
        :return:

        Scatter matrix:
        [[P1P1, S1P1, P2P1, S2P1],
         [P1S1, S1S1, P2S1, S2S1],
         [P1P2, S1P2, P2P2, S2P2],
         [P1S2, S1S2, P2S2, S2S2]]
        '''

        m1, m2 = self.above, self.below

        vp1, vs1, rho1 = m1.vp, m1.vs, m1.rho
        vp2, vs2, rho2 = m2.vp, m2.vs, m2.rho

        # angles for P wave
        sini1 = p * vp1
        cosi1 = sin2cos(sini1)
        sini2 = p * vp2
        cosi2 = sin2cos(sini2)

        # angles for S wave
        sinj1 = p * vs1
        cosj1 = sin2cos(sinj1)
        sinj2 = p * vs2
        cosj2 = sin2cos(sinj2)

        # Aki & Richards (1980) P149, Eq. 5.35
        M = np.array([
            [-sini1, -cosj1, sini2,  cosj2],
            [ cosi1, -sinj1, cosi2, -sinj2],
             ]
        ])





if __name__ == '__main__':
    m1 = Material(10, 20, 30)
    m2 = Material(40, 50, 60)
    dis = Discontinuity(m1, m2)