# -*- coding: utf-8 -*-
''' SAC related functions. '''

from obspy import read, Stream
from obspy.io.sac.util import get_sac_reftime


def read_sac(pathname, starttime='b+0', endtime='e+0', **kwargs):
    '''Read SAC files with cut option.

    >>> st = read_sac("test.sac", 't0-10', 't0+10')  # doctest: +SKIP
    '''

    st = read(pathname, **kwargs)
    return cut_sac(st, starttime=starttime, endtime=endtime)


def cut_sac(st, starttime='b+0', endtime='e+0'):
    '''Cut stream with specified time window.

    >>> st = read("test.sac")  # doctest: +SKIP
    >>> st2 = cut_sac(st, 't0-10', 't0+10')  # doctest: +SKIP

    '''

    tmark0, offset0 = _parse_time(starttime)
    tmark1, offset1 = _parse_time(endtime)

    st2 = Stream()
    for tr in st:
        reftime = get_sac_reftime(tr.stats.sac)
        try:
            start = reftime + tr.stats.sac[tmark0] + offset0
        except KeyError:
            msg = "{}: time marker {} undefined".format(tr.id, tmark0)
            raise KeyError(msg)
        try:
            end = reftime + tr.stats.sac[tmark1] + offset1
        except KeyError:
            msg = "{}: time marker {} undefined".format(tr.id, tmark1)
            raise KeyError(msg)
        st2 += tr.slice(start, end)

    return st2


def _check_tmark(tmark):
    '''Check validity of SAC time markers.

    >>> _check_tmark('b')
    True

    >>> _check_tmark('T0')
    True

    >>> _check_tmark('T11')
    False
    '''
    tmark = tmark.upper()
    if len(tmark) == 1:
        return tmark in ('B', 'E', 'A', 'O', 'E')
    elif len(tmark) == 2 and tmark[0] == 'T':
        return tmark[1].isdigit()
    else:
        return False


def _parse_time(value):
    '''Parse time in ``Tn+-xx`` format.

    >>> _parse_time('T0+20')
    ('T0', 20.0)

    >>> _parse_time('T3-5.5')
    ('T3', -5.5)

    >>> _parse_time('T11-5')
    Traceback (most recent call last):
    ...
    ValueError: Unknown relative time format T11-5.

    >>> _parse_time('C+5')
    Traceback (most recent call last):
    ...
    ValueError: Unknown relative time format C+5.
    '''

    # tmark + positive offset
    try:
        tmark, offset = value.split('+')
        if _check_tmark(tmark):
            return tmark, float(offset)
    except ValueError:
        pass

    # tmark - negative offset
    try:
        tmark, offset = value.split('-')
        if _check_tmark(tmark):
            return tmark, -float(offset)
    except ValueError:
        pass

    raise ValueError("Unknown relative time format {}.".format(value))


if __name__ == "__main__":
    import doctest
    doctest.testmod()
