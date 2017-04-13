#!/usr/bin/env python
# -*- coding: utf-8 -*-
import os

import pytest

from obspy import read
from seismanpy.sac import read_sac, cut_sac

pwd = os.path.dirname(__file__)
path = os.path.join(pwd, 'data')


class TestSACClass:
    def test_read_sac(self):
        st = read_sac(os.path.join(path, "ca*.z"), 'a-1', 'a+2')
        assert st[0].stats.npts == 296
        assert st[1].stats.npts == 296

    def test_read_sac_undefined_tmark(self):
        with pytest.raises(KeyError):
            st = read_sac(os.path.join(path, "ca*.z"), 't0-1', 'a+2')
        with pytest.raises(KeyError):
            st = read_sac(os.path.join(path, "ca*.z"), 'a-1', 't1+2')

    def test_cut_sac(self):
        st = read(os.path.join(path, "ca*.z"))
        st2 = cut_sac(st, 'a-1', 'a+2')
        assert st[0].stats.npts == 3933
        assert st[1].stats.npts == 3933
        assert st2[0].stats.npts == 296
        assert st2[1].stats.npts == 296

