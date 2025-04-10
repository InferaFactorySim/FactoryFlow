# -*- coding: utf-8 -*-
"""
Created on Mon Feb  6 11:53:55 2023

@author: User
"""

import scipy,random
import pandas as pd
from scipy import stats
import matplotlib.pyplot as plt

import numpy as np
from statsmodels.tsa.arima_process import ArmaProcess

def genrvs_old(N):
    distributionlist=[i+1 for i in range(5)]
    d1=random.choice(distributionlist)
    if N%2==0:
        N1=N//2
        N2=N//2
    else:
        N1=N//2
        N2=(N//2)+1
        
    #print(d1)
    if d1==1:
        k1=scipy.stats.expon.rvs(random.random(), size=N1)
        k2=scipy.stats.norm.rvs(random.randint(5,10),random.randint(1,2)+random.random(),size=N2)
    elif d1==2:
        k1=scipy.stats.expon.rvs(random.randint(1,2)+random.random(), size=N1)
        k2=scipy.stats.norm.rvs(random.randint(7,9),random.randint(0,2)+random.random(),size=N2)
    elif d1==3:
        k1=scipy.stats.norm.rvs(random.randint(5,10),random.randint(2,3)+random.random(),size=N1)
        k2=scipy.stats.norm.rvs(random.randint(13,15),random.randint(0,2)+random.random(),size=N2)
    elif d1==4:
        k1=scipy.stats.norm.rvs(random.randint(38,42),random.randint(0,2)+random.random(),size=N1)
        k2=scipy.stats.uniform.rvs(random.randint(40,43),random.randint(55,65), size=N2)
    else:
        k1=scipy.stats.uniform.rvs(random.randint(45,49),random.randint(60,65), size=N1)
        k2=scipy.stats.expon.rvs(random.randint(44,46)+random.random(), size=N2)
   
    
    #plt.hist(k1,bins=40)    
    #plt.hist(k2,bins=40)  
    #plt.show()
   
    return np.concatenate((k1,k2))


def genrvs(d1,d2,param1,param2,size1,size2):
    k=getattr(scipy.stats, d1)
    args=param1[:-2]
    k1=k.rvs(loc=param1[-2],scale=param1[-1],*args,size=size1)
    k=getattr(scipy.stats, d2)
    args=param2[:-2]
    k2=k.rvs(loc=param2[-2],scale=param1[-1],*args,size=size2)
    return np.concatenate((k1,k2))

def mixeddistribution(N):
    if N%2==0:
        N1=N//2
        N2=N//2
    else:
        N1=N//2
        N2=(N//2)+1
    data1= genrvs("norm","expon",[2,0.5],[1,0.5],N1,N2)
    data2= genrvs("norm","triang",[2,1],[0.5,0.5,1],N1,N2)
    data3= genrvs("norm","uniform",[2.5,0.06],[4,3],N1,N2)
    data4= genrvs("uniform","uniform",[6,6],[6,7],N1,N2)
    return random.choice([data1,data2,data3,data4])



def normal(N):
    return scipy.stats.norm.rvs(random.randint(5,30),random.randint(0,2)+random.random(),size=N)
def expon(N):
    return scipy.stats.expon.rvs(random.random(), size=N)
def uniform(N):
    return scipy.stats.uniform.rvs(random.randint(5,30),random.randint(5,30), size=N)
def poisson(N):
    return np.random.poisson(random.random(),N)
def geometric(N):
    return np.random.geometric(random.random(), size=N)




def MVGaussian(N):
    np.random.seed(0)
    n_sample = N
    d_sample = 5
    cov_sample = np.eye(d_sample) + np.random.rand(d_sample, d_sample)+5
    sim_cov = cov_sample.transpose().dot(cov_sample)
    data = np.random.exponential(size=(n_sample, d_sample)) + np.random.multivariate_normal(
        np.zeros(d_sample), sim_cov, size=n_sample)
    return data

def MVGaussian_positive(N):
    
    mean=[2,3]
    cov=[[2.0, 0.3], [0.3, 0.5]]
    data  = np.random.multivariate_normal(mean, cov, N)
    return data

def multivariate_Gaussian_sample(N):
    data=MVGaussian(N)
    processdataMV={"temp":data[:,0],"pressure":data[:,1],"items_processed":geometric(N),"usedrawmaterial_amount":data[:,3],"flow":data[:,4],"powerconsumption":mixeddistribution(N)}
    processdfMV=pd.DataFrame(processdataMV)
    #processdf.to_csv("sampledatamultivariate.csv")
    return processdfMV

def multivariate_Gaussian_sample4uni(N):
    data=MVGaussian(N)
    processdataMV={"temp":data[:,0],"pressure":data[:,1],"jobarrival_Machine":data[:,2],"usedrawmaterial_amount":data[:,3],"flow":data[:,4]}
    processdfMV=pd.DataFrame(processdataMV)
    #processdf.to_csv("sampledatamultivariate.csv")
    return data

def multivariate_Gaussian_sample(N):
    data=MVGaussian(N)
    processdataMV={"temp":data[:,0],"pressure":data[:,1],"items_processed":geometric(N),"usedrawmaterial_amount":data[:,3],"flow":data[:,4],"powerconsumption":mixeddistribution(N)}
    processdfMV=pd.DataFrame(processdataMV)
    #processdf.to_csv("sampledatamultivariate.csv")
    return processdfMV


def univariate_sample(N):
    MVG=multivariate_Gaussian_sample4uni(N)
    #processdata={"temp":MVG[:,0],"items_processed":geometric(N),"usedrawmaterial_amount":expon(N),"pressure":MVG[:,1],"timetaken_transport":uniform(N),"powerconsumption":mixeddistribution(N)}
    #processdata={"arrival_M31_rate":MVG[:,0],"arrival_converyoybelt11_rate":geometric(N),"arrival_store1_rate":expon(N),"arrival_split21_rate":MVG[:,1],"conveyor_power_column":uniform(N),"machine31_power_column":mixeddistribution(N),"store1_power_column":uniform(N),"split21_power_column":mixeddistribution(N)}
    processdata={"delay_Machine1":MVG[:,0],"delay_Machine2":geometric(N),"arrival_conveyor1_rate":expon(N),"Machine1_power_column":uniform(N),"Machine3_delay":mixeddistribution(N),"conveyor2_delay":uniform(N)}
    #print(processdata)
    processdf=pd.DataFrame(processdata)
    processdf.to_csv("sampledatajun13.csv")
    return processdf


def TimeSeriesGen(N):
    n=N
    ar3 = np.array([3])
    
    # specify the weights : [1, 0.9, 0.3, -0.2]
    ma3 = np.array([1, 0.9, 0.3, -0.2])
    
    # simulate the process and generate 1000 data points
    ARMA03 = ArmaProcess(ar3, ma3).generate_sample(nsample=n)
    
    
    
    ar1 = np.array([1, 0.6])
    ma1 = np.array([1, -0.2])
    ARMA11 = ArmaProcess(ar1, ma1).generate_sample(nsample=n)
    ar3 = np.array([1, 0.9, 0.3, -0.2])
    ma = np.array([3])
    ARMA30 = ArmaProcess(ar3, ma).generate_sample(nsample=n)
    ar2 = np.array([1, 0.6, 0.4])
    ma2 = np.array([1, -0.2, -0.5])
    
    ARMA22 = ArmaProcess(ar2, ma2).generate_sample(nsample=n)
    
    processdataTS={"Stockprice":ARMA22,"GasPrice":ARMA30,"dailytemp":ARMA11,"dailytraffic":ARMA03}
    processdfTS=pd.DataFrame(processdataTS)
    return processdfTS

def arbitrary_MV_samples(N):
    data=MVGaussian_positive(N)
    
    
    #teardrop
    xt=scipy.stats.norm.rvs(0,5,N)
    yt=[float(scipy.stats.norm.rvs(i,np.abs(i),1)) for i in xt]
    
    processdata={"temp":data[:,0],"pressure":data[:,1],"powerconsumption":xt,"flow":yt}
    
    arb_df=pd.DataFrame(processdata)
    return arb_df
    
                        