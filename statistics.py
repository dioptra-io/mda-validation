import numpy as np
import scipy as sp
import scipy.stats

def mean_confidence_interval(data, confidence=0.95):
    a = 1.0*np.array(data)
    n = len(a)
    m, se = np.mean(a), scipy.stats.sem(a)
    percentile = sp.stats.norm.ppf((1+confidence)/2.)
    h = se * percentile
    return m, h