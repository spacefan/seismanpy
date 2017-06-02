# -*- coding: utf-8 -*-
"""Source related functions
"""
import warnings
import numpy as np
from obspy.core.event.source import farfield


def radiation_pattern(mt, takeoff_angle, azimuth, wavetype='P', system='RTP',
                      normalize=False):
    """Wrapper of obspy.core.event.source.farfield.

    Parameters
    ----------
    mt: list(float)
        Six component moment tensor ([Mxx, Myy, Mzz, Mxy, Mxz, Myz])
    takeoff_angle: float or list(float)
        Takeoff angle of seismic ray (in degree)
    azimuth: float or list(float)
        Azimuth of seismic ray (in degree)
    wavetype: str
        Specify wave type, 'P' or 'S'
    system: str
        Coordinate system of mt, NED|USE|RTP
    normalize: bool
        Return normalized radiation pattern

    Returns
    -------
    float
        Magnitude of radiation pattern

    Examples
    --------
    (1) Explosion source:

        >>> mt = [1, 1, 1, 0, 0, 0]
        >>> mag = radiation_pattern(mt, 35, 44, wavetype='P', system='RTP')
        >>> print(mag)
        1.0

    (2) Event 2001/6/23 20:34:23

        >>> mt = [2.245, -0.547, -1.698, 1.339, -3.728, 1.444]
        >>> mag_P = radiation_pattern(mt, 80, 30, wavetype='P', system='RTP')
        >>> print(mag_P)
        0.92058159502
        >>> mag_S = radiation_pattern(mt, 80, 30, wavetype='S', system='RTP')
        >>> print(mag_S)
        3.66100655525
    """
    from obspy import __version__ as obspy_version

    if obspy_version == '1.0.2':
        msg = ("farfield in ObsPy version {} has known issues."
               "(see issue #1499 and PR #1553).").format(obspy_version)
        warnings.warn(msg)

    if system in ('RTP', 'USE'):
        ned_mt = mt_converter(mt, system_in='RTP', system_out='NED')
    elif system == 'NED':
        ned_mt = mt
    else:
        raise ValueError("Wrong coordinate system of moment tensor")

    ray = np.array([[takeoff_angle], [azimuth]]) / 180.0 * np.pi
    # farfield return three component displacement
    disp = farfield(ned_mt, ray, wavetype)
    mag = np.sqrt(np.sum(disp * disp, axis=0))[0]

    if normalize:
        mag /= get_scalar_moment(ned_mt)

    return mag


def phase_radiation_pattern(mt, system='RTP', phase_list=None,
                            source_depth_in_km=None, distance_in_degree=None,
                            azimuth=None, model='ak135'):

    '''Calcuate radiated amplitude of seismic phases

    >>> mt = [0.422, -0.689, 0.267, -0.432, -0.284, 0.377]
    >>> phase_radiation_pattern(mt, phase_list=['PcP', 'PKiKP'],
    ...                         source_depth_in_km=300, distance_in_degree=30,
    ...                         azimuth=50)
    [0.35494640676390243, 0.41287695358633075]
    '''

    from obspy.taup import TauPyModel

    model = TauPyModel(model=model)
    arrivals = model.get_travel_times(source_depth_in_km, distance_in_degree,
                                      phase_list=phase_list)

    mag_dict = {}
    for arrival in arrivals:
        mag = radiation_pattern(mt, arrival.takeoff_angle, azimuth,
                                wavetype=arrival.name[0], system=system)
        mag_dict[arrival.name] = mag

    mag_list = [mag_dict[phasename] for phasename in phase_list]

    return mag_list


def get_scalar_moment(mt):

    mt2 = fullmt(mt)
    moment = np.sqrt(np.sum(mt2*mt2)/2.0)

    return moment


def mt_converter(mt, system_in='RTP', system_out='RTP'):
    '''Moment tensor conversion between different coordinate systems

    Parameters
    ----------
    mt: list(float)
        Six component moment tensor ([Mxx, Myy, Mzz, Mxy, Mxz, Myz])
    system_in: str
        Coordinate system of input moment tensor
    system_out: str
        Coordinate system of output moment tensor

    Returns
    -------
    list(float)
        Six component moment tensor ([Mxx, Myy, Mzz, Mxy, Mxz, Myz])

    Examples
    --------
    (1) Convert from RTP to NED

        >>> mt_converter([1, 2, 3, 4, 5, 6], system_in='RTP', system_out='NED')
        [2, 3, 1, -6, 4, -5]

    (2) Convert from NED to RTP

        >>> mt_converter([1, 2, 3, 4, 5, 6], system_in='NED', system_out='RTP')
        [3, 1, 2, 5, -6, -4]
    '''

    coordinate_systems = ('NED', 'USE', 'RTP')
    if system_in not in coordinate_systems:
        msg = "Input moment tensor not in NED|USE|RTP coordinates."
        raise ValueError(msg)
    if system_out not in coordinate_systems:
        msg = "Output moment tensor not in NED|USE|RTP coordinates."
        raise ValueError(msg)

    if system_in in ('RTP', 'USE') and system_out == 'NED':
        signs = [1, 1, 1, -1, 1, -1]
        indices = [1, 2, 0, 5, 3, 4]
        ned_mt = [sign * mt[ind] for sign, ind in zip(signs, indices)]
        return ned_mt
    elif system_in == 'NED' and system_out in ('RTP', 'USE'):
        signs = [1, 1, 1, 1, -1, -1]
        indices = [2, 0, 1, 4, 5, 3]
        rtp_mt = [sign * mt[ind] for sign, ind in zip(signs, indices)]
        return rtp_mt
    else:
        return mt


def fullmt(mt):
    '''Takes 6 comp moment tensor and returns full 3x3 moment tensor

    >>> fullmt([1, 2, 3, 4, 5, 6])
    array([[1, 4, 5],
           [4, 2, 6],
           [5, 6, 3]])
    '''

    mt_full = np.array(([[mt[0], mt[3], mt[4]],
                         [mt[3], mt[1], mt[5]],
                         [mt[4], mt[5], mt[2]]]))
    return mt_full


if __name__ == "__main__":
    import doctest
    doctest.testmod()
