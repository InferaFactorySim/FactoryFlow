# @title genrvs
# -*- coding: utf-8 -*-

import scipy
from scipy import stats
import numpy as np

def genrvs(d1,d2,param1,param2,size1,size2):
    k=getattr(scipy.stats, d1)
    args=param1[:-2]
    k1=k.rvs(loc=param1[-2],scale=param1[-1],*args,size=size1)
    k=getattr(scipy.stats, d2)
    args=param2[:-2]
    k2=k.rvs(loc=param2[-2],scale=param1[-1],*args,size=size2)
    return np.concatenate((k1,k2))

data1= genrvs("norm","expon",[5,1],[0.5,0],5000,5000)