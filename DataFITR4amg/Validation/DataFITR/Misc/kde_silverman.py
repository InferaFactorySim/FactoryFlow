# @title kde_silverman
#!/usr/bin/env python3
# -*- coding: utf-8 -*-


import numpy as np
import matplotlib.pyplot as plt
from numpy import atleast_2d
from genrvs import genrvs

#Gaussian_function
def gaussian(x,b=1):
    return np.exp(-x**2/(2*b**2))/(b*np.sqrt(2*np.pi))

k1=[np.random.normal(5,1) for i in range(50000)]
k3=[np.random.uniform(11,17) for i in range(50000)]
k2=[np.random.normal(11,1) for i in range(50000)]
#k4=[np.random.uniform(13,20) for i in range(50000)]
#k1=[np.random.exponential(0.5) for i in range(10000)]
#k2=[np.random.exponential(1/10) for i in range(10000)]
#k1.extend(k2)
k1.extend(k2)
#k1.extend(k4)

data=np.array(k1)



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
    N=100 #Number of bins
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
    norm = np.random.multivariate_normal(np.zeros(n), cov, size)


    y=np.transpose(norm)+means
    '''plt.hist(y[0],100,density=True)
    plt.legend(['histogram of generated data'])
    plt.xlabel('x-values')
    plt.title(name)
    plt.ylabel('pdf')'''
    plt.show()
    return y[0]

#h=kde_func(data)
#resample(k1,h,20000)




def resample2(data,h):

    i=0
    lenDataset=len(data)
    generatedDataPdfSilverman=np.zeros(1000)
    while i<1000:
        randNo=np.random.rand(1)*(np.max(data)-np.min(data))-np.absolute(np.min(data))
        if np.random.rand(1)<=np.sum((gaussian(randNo-data,h))/lenDataset):
            generatedDataPdfSilverman[i]=randNo
            i+=1



    plt.hist(generatedDataPdfSilverman,50,density=True)
    plt.legend(['histogram of generated data(method2)'])
    plt.show()


data=genrvs("norm","expon",[1,.05],[0.9,1],5000,5000)
data4=genrvs("uniform","norm",[30,10],[60,0.5],5000,5000)
kde_plotfunc(data4,"test")
#resample(data,10000,'test')