# -*- coding: utf-8 -*-

import numpy as np
import scipy.signal
from obspy import read, Trace


def stack(stream, method="linear", nroot=2, pws_power=1):
    '''
    Returns stack for stream

    Parameters
    ----------
    stream: ObsPy Stream object
        Stream of seismograms to be stacked
    method: String
        Stack method, choose from linear|nroot|pws
    nroot: Float
        Nth root for nroot method
    pws_power: Float
        Power for phase weighted stack
    '''

    # check npts and delta
    assert len(set([tr.stats.npts for tr in stream])) == 1, "npts not equal for all traces"
    assert len(set([tr.stats.delta for tr in stream])) == 1, "delta not equal for all traces"

    method = method.lower()

    if method == 'linear':
        stack = linear_stack(stream)
    elif method == 'nroot':
        stack = Nth_root_stack(stream, n=nroot)
    elif method == 'pws':
        stack = phase_weighted_stack(stream, pws_power=pws_power)
    else:
        print("Incorrect stack method")

    return stack


def linear_stack(stream):
    '''
    Returns the linear stack for stream.

    Parameters
    ----------
    stream: ObsPy Stream object
        Stream of seismograms to be stacked
    normalize: bool
        Normlize the stacked trace or not

    Returns
    -------
    stack: NumPy array
        The stacked trace
    '''

    stack = np.mean([tr.data for tr in stream], axis=0)
    return Trace(stack)


def Nth_root_stack(stream, n):
    '''
    Returns the nth root stack for stream.

    Parameters
    ----------
    stream: ObsPy Stream object
        Stream of seismograms to be stacked
    n: int
        Order of the nth root process

    Returns
    -------
    stack: NumPy array
        The stacked trace
    '''

    stack = np.zeros(stream[0].data.shape)
    for tr in st:
        stack += pow(abs(tr.data), 1.0/n) * np.sign(tr.data)

    stack /= len(stream)

    stack = pow(abs(stack), n) * np.sign(stack)

    return Trace(stack)


def phase_weighted_stack(stream, pws_power):
    '''
    Returns the phase weighted stack for stream.

    Parameters
    ----------
    stream: ObsPy Stream object
        Stream of seismograms to be stacked
    n: float

    Returns
    -------
    stack: NumPy array
        The stacked trace
    '''

    npts = stream[0].data.shape
    stack = np.zeros(npts)

    phase = np.zeros(npts, dtype="c8")
    for tr in stream:
        angle = np.angle(scipy.signal.hilbert(tr.data))
        phase.real += np.cos(angle)
        phase.imag += np.sin(angle)

    weight = np.abs(phase) / len(stream)

    for tr in stream:
        stack += tr.data * np.power(weight, pws_power)

    return Trace(stack)


if __name__ == "__main__":
    import doctest
    doctest.testmod()
