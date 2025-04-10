#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Jun  3 16:10:27 2022

@author: lekshmi
"""

import numpy as np
import matplotlib.pyplot as plt
from numpy import atleast_2d



#Gaussian_function
def gaussian(x,b=1):
    return np.exp(-x**2/(2*b**2))/(b*np.sqrt(2*np.pi))




def kde_plotfunc(data,name):
    N=100 #Number of bins
    lenDataset = len(data)
    #normalized histogram of loaded datase
    hist, bins = np.histogram(data, bins=N, range=(np.min(data), np.max(data)), density=True)
    center = (bins[:-1] + bins[1:]) / 2
    
    #Silverman's Rule(bandwidth)
    sumPdfSilverman=np.zeros(len(center))
    h=1.06*np.std(data)*lenDataset**(-1/5.0)
    
    for i in range(0, lenDataset):
        sumPdfSilverman+=((gaussian(center-data[i],h))/lenDataset)
    
    plt.hist(data,N, density=True )
    plt.plot(center, sumPdfSilverman,color='red', )
    plt.legend(['KDE, Silvermans bandwidth h=%.2f' % h,'histogram of data'])
    plt.title(name)
    plt.xlabel('x-values')
    plt.ylabel('pdf')
    plt.show()
    
def kde_func(data,name,bins):
    N=bins #Number of bins
    lenDataset = len(data)
    #normalized histogram of loaded datase
    hist, bins = np.histogram(data, bins=N, range=(np.min(data), np.max(data)), density=True)
    center = (bins[:-1] + bins[1:]) / 2
    
    #Silverman's Rule(bandwidth)
    sumPdfSilverman=np.zeros(len(center))
    h=1.06*np.std(data)*lenDataset**(-1/5.0)
    
    for i in range(0, lenDataset):
        sumPdfSilverman+=((gaussian(center-data[i],h))/lenDataset)
    return (center,sumPdfSilverman,h)
    
 
    

def bandwidth(data):
    N=100#Number of bins
    lenDataset = len(data)
    #normalized histogram of loaded datase
    hist, bins = np.histogram(data, bins=N, range=(np.min(data), np.max(data)), density=True)
    center = (bins[:-1] + bins[1:]) / 2
    
    #Silverman's Rule(bandwidth)
    sumPdfSilverman=np.zeros(len(center))
    h=1.06*np.std(data)*lenDataset**(-1/5.0)
    
    return h

def resample(k1, size,name):
    h=bandwidth(k1)
    k1=atleast_2d(k1)
    n, d = k1.shape
    indices = np.random.randint(0, d, size)
    
    #cov1=(np.cov(k1))*(h*h)
    cov1=h**2
    cov_list=[cov1 for i in range(n)]
    
    cov = np.diag(cov_list)
    
    means = k1[:,indices]
    #print("m",means)
    norm = np.random.multivariate_normal(np.zeros(n), cov, size)
    
    
    y=np.transpose(norm)+means
    plt.show()
    return y[0]

#h=kde_func(data,"kde",100)
#resample(k1,h,"kde")




def resample2(data,N):
    lenDataset = len(data)
    h=1.06*np.std(data)*lenDataset**(-1/5.0)
    i=0
    lenDataset=len(data)
    generatedDataPdfSilverman=np.zeros(N)
    while i<N:
        randNo=np.random.rand(1)*(np.max(data)-np.min(data))-np.absolute(np.min(data))
        if np.random.rand(1)<=np.sum((gaussian(randNo-data,h))/lenDataset):
            generatedDataPdfSilverman[i]=randNo
            i+=1



    plt.hist(generatedDataPdfSilverman,100,density=True)
    plt.legend(['histogram of generated data(method2)'])
    plt.show()
    return generatedDataPdfSilverman
    


    
    
    