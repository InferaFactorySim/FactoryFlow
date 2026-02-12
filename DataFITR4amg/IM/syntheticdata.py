# -*- coding: utf-8 -*-
"""
Created on Wed Oct 26 14:57:47 2022

@author: User
"""
import numpy as np
import random
import matplotlib.pyplot as plt
import pandas as pd
from statsmodels.tsa.arima_process import ArmaProcess

        
def dependency(data):
    """

    Parameters
    ----------
    data : data
        to find the dependency in the data: covariance and autocorrelation is used. Data is standardised

    Returns
    -------
     autocorrelation in matrix form

    """
    
    dependency= np.cov(data)
    return data.corr()


    
        
#synthetic data geberation

class syntheticdata:
    def __init__(self,linear=True,noise=False,scale=True,valrange=[0,10],n=1000):
        self.linear=linear
        self.noise=noise
        self.scale=scale
        self.n=n
        self.valrange=valrange
        #self.stationary=stationary
        self.step=(self.valrange[1]-self.valrange[0])/self.n
        self.valrange=np.arange(self.valrange[0],self.valrange[1],self.step)
        
        #print(self.linear,self.noise,self.scale)
    
    def generatestationary(self):
        if self.scale==True:
            self.scaler=random.random()
        else:
            self.scaler=1
        if self.noise==True:
            self.noise=np.random.normal(0,1)
        else:
            self.noise=0
        if self.linear==True:
            #y=scale*x+n(0,1)
            #return self.scaler*self.valrange+np.random.normal(0,0.001,self.n)
            mean=np.random.random()
            return mean+np.random.normal(0,0.1,self.n)/2+np.random.normal(0,0.1,self.n)/2 #ma process
    
            
            
        else:
            #y=scale*sin(x)+n(0,1)
            print(len(self.valrange))
            print(len(np.sin(self.valrange)))
            print(len(np.random.normal(0,0.1,self.n)))
            return self.scaler*np.sin(self.valrange)+np.random.normal(0,0.1,self.n)
        
    def generatenonstationary(self):
        if self.scale==True:
            self.scaler=random.random()
        else:
            self.scaler=1
        if self.noise==True:
            self.noise=np.random.normal(0,1)
        else:
            self.noise=0
        if self.linear==True:
            #y=scale*x+n(0,1)
            return self.scaler*self.valrange*np.random.normal(5,1.2,self.n)# mean shifting
            
            
        else:
            #y=scale*sin(x)+n(0,1)
            return self.scaler*np.sin(self.valrange)*np.random.normal(5,1,self.n)
        
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
        
        processdataTS={"Stockprice":ARMA22,"BusPassengers":ARMA30,"dailytemp":ARMA11,"dailytraffic":ARMA03}
        processdfTS=pd.DataFrame(processdataTS)
        return processdfTS

        
    
            
        
        


def univariate_stationary(N):
    t=syntheticdata(True,False,n=N)
    data=t.generatestationary()
    processdataMV={"temp":data}
    processdfMV=pd.DataFrame(processdataMV)
    #processdf.to_csv("sampledatamultivariate.csv")
    return processdfMV





data=univariate_stationary(1000)
plt.plot(data)
plt.show()
#plt.hist(data)