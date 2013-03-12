# -*- coding: UTF-8 -*-
#-------------------------------------------------------------------------------
# Name:        test_ipol
# Purpose:     unit tests for the wrdalib.ipol module
#
# Author:      Thomas Pfaff
#
# Created:     31.05.2012
# Copyright:   (c) Thomas Pfaff 2012
# Licence:     The MIT License
#-------------------------------------------------------------------------------
#!/usr/bin/env python
import numpy as np

import wradlib.ipol as ipol

def test__parse_covariogram():
    cov_model = '1.0 Exp(10.5) + 2.3 Sph(20.4) + 5.0 Nug(0.)'
    h = 5.0
    c = ipol.parse_covariogram(cov_model)
    ci = sum([ipol.cov_exp(h, 1., 10.5),
              ipol.cov_sph(h, 2.3, 20.4),
              ipol.cov_nug(h, 5.0, 0.)])
    assert c(h) == ci


def test__cov_lin():
    assert np.allclose(ipol.cov_lin([0.,5.,10.]), np.array([1., 0., 0.]))
    assert np.allclose(ipol.cov_lin([0.,5.,10.], sill=2., rng=10.), np.array([2., 1., 0.]))


def test__cov_sph():
    assert np.allclose(ipol.cov_sph([0.,5.,10.]), np.array([1., 0., 0.]))
    assert np.allclose(ipol.cov_sph([0.,5.,10.], sill=2., rng=10.), np.array([2., 0.625, 0.]))


def test__cov_exp():
    assert np.allclose(ipol.cov_exp([0.,5.,10.]), np.array([1.,6.73794700e-03, 4.53999298e-05]))
    assert np.allclose(ipol.cov_exp([0.,5.,10.], sill=2., rng=10.), np.array([2.,1.21306132, 0.73575888]))


def test__cov_pow():
    assert np.allclose(ipol.cov_pow([0.,5.,10.]), np.array([ 1., -4., -9.]))
    assert np.allclose(ipol.cov_pow([0.,5.,10.], sill=2., rng=10.), np.array([2.00000000e+00, -9.76562300e+06, -1.00000000e+10]))


def test__cov_mat():
    assert np.allclose(ipol.cov_mat([0.,5.,10.]), np.array([1.00000000e+00, 8.49325705e-04, 7.21354153e-07]))
    assert np.allclose(ipol.cov_mat([0.,5.,10.], sill=2., rng=10.), np.array([2., 0.98613738, 0.48623347]))
    assert np.allclose(ipol.cov_mat([0.,5.,10.], sill=2., rng=10., shp=0.25), np.array([2., 0.74916629, 0.39961004]))


def test__cov_gau():
    assert np.allclose(ipol.cov_gau([0.,5.,10.]), np.array([1.00000000e+00, 1.38879439e-11, 3.72007598e-44]))
    assert np.allclose(ipol.cov_gau([0.,5.,10.], sill=2., rng=10.), np.array([2., 1.55760157, 0.73575888]))


def test__cov_cau():
    assert np.allclose(ipol.cov_cau([0.,5.,10.]), np.array([1., 0.16666667, 0.09090909]))
    assert np.allclose(ipol.cov_cau([0.,5.,10.], sill=2., rng=10., ), np.array([2., 1.33333333, 1.]))
    assert np.allclose(ipol.cov_cau([0.,5.,10.], sill=2., rng=10., alpha=0.5), np.array([2., 0.6862915, 0.5]))
    assert np.allclose(ipol.cov_cau([0.,5.,10.], sill=2., rng=10., alpha=0.5, beta=1.5), np.array([2., 0.40202025, 0.25]))


def test__OrdinaryKriging_1():
    """testing the basic behaviour of the OrdinaryKriging class"""
    src = np.array([[0.,0.], [4.,0]])
    trg = np.array([[0.,0.], [2.,0.], [1.,0], [4.,0]])

    ip = ipol.OrdinaryKriging(src, trg, '1.0 Lin(2.0)')

    vals = np.array([[1., 2., 3.],
                     [3., 2., 1.]])
    res = ip(vals)
    assert np.all(res == np.array([[ 1.,   2.,   3. ],
                                   [ 2.,   2.,   2. ],
                                   [ 1.5,  2.,   2.5],
                                   [ 3.,   2.,   1. ]]))


def test__ExternalDriftKriging_1():
    """testing the basic behaviour of the ExternalDriftKriging class
    with drift terms constant over multiple fields"""
    src = np.array([[0.,0.], [4.,0]])
    trg = np.array([[0.,0.], [2.,0.], [1.,0], [4.,0]])
    src_d = np.array([0., 1.])
    trg_d = np.array([0.,1.,2.,3.])

    ip = ipol.ExternalDriftKriging(src, trg, '1.0 Lin(2.0)',
                                      src_drift=src_d,
                                      trg_drift=trg_d)

    vals = np.array([[1., 2., 3.],
                     [3., 2., 1.]])
    res = ip(vals)
    assert np.all(res == np.array([[ 1.,  2.,  3.],
                                   [ 3.,  2.,  1.],
                                   [ 5.,  2., -1.],
                                   [ 7.,  2., -3.]]))


def test__ExternalDriftKriging_2():
    """testing the basic behaviour of the ExternalDriftKriging class
    with drift terms varying over multiple fields"""
    src = np.array([[0.,0.], [4.,0]])
    trg = np.array([[0.,0.], [2.,0.], [1.,0], [4.,0]])
    src_d = np.array([[0.,0.,0.],
                      [1.,1.,1.]])
    trg_d = np.array([[0.,0.,0.],
                      [1.,1.,1.],
                      [2.,2.,2.],
                      [3.,3.,3.]])

    ip = ipol.ExternalDriftKriging(src, trg, '1.0 Lin(2.0)',
                                      src_drift=src_d,
                                      trg_drift=trg_d)

    vals = np.array([[1., 2., 3.],
                     [3., 2., 1.]])
    res = ip(vals)
    assert np.all(res == np.array([[ 1.,  2.,  3.],
                                   [ 3.,  2.,  1.],
                                   [ 5.,  2., -1.],
                                   [ 7.,  2., -3.]]))


if __name__ == '__main__':
    pass