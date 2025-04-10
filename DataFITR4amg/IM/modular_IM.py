#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Jan  4 13:25:51 2023

@author: lekshmi
"""

#!/usr/bin/env python3
# -*- coding: utf-8 -*-

#from scipy.stats import kstest,poisson,norm,triang,skew,chisquare
import sys
sys.path.append('/home/lekshmi/Downloads/my_app/IM') 
#sys.path.append('./IM') 
from scipy.stats import kstest,skew,chisquare
from scipy.interpolate import make_interp_spline
import random
import matplotlib.pyplot as plt
from tabulate import tabulate
import statsmodels.api as sm
import seaborn as sns
import numpy as np
import pylab as py
import warnings
warnings.filterwarnings('ignore')
from IM import kde_silverman_both
#import kde_silverman_both
import scipy.stats as stats
import statistics
import scipy
import statsmodels.api
import math
import pandas as pd 
import streamlit as st
#import listparamsofdistributions
from IM import listparamsofdistributions

import re

random.seed(42)

class modelmatch:
    def __init__(self,data,typeofdata,title,binhist,gofoption,distlist,distributions,binskde=50):
        self.data=np.sort(data)
        self.datamain=data
        self.typeofdata=typeofdata
        self.title=title
        self.titleplot=str(self.title)+":"+gofoption
        self.binhist=binhist
        self.N=len(self.data)
        self.GOFdata = {"Test": ["KStest", "Chi squared Test"]}
        self.SSEdata = {"Test": []}
        self.GOFpval={}
        self.gofoption=gofoption
        self.binskde=binskde

        
        if self.typeofdata=='discrete':
            self.min=min(self.data)
            self.max=max(self.data)
            
            self.mean=np.mean(self.data)
            self.sd=np.std(self.data)
            #self.lnmean=np.mean(np.log(self.data))
            #self.lnsd=np.std(np.log(self.data))
            self.lamda=1/self.mean #if stats.expon
            self.weibull_param=stats.weibull_min.fit(self.data, floc=0)
            
            self.mode=statistics.mode(self.data)
            self.median=np.median(self.data)
            self.c=(self.mode-self.min)/(self.max-self.min)
            self.binom_n=len(self.data)
            self.bmean=np.unique(self.data,return_counts=True)[0][np.argmax(np.unique(self.data,return_counts=True)[1])]
            self.binom_param=self.mean/self.binom_n
            
            self.geomparam=len(self.data)/sum(self.data)
        
        
    
    def calc_param(self,distribution):
        if distribution=='binom':
            return (self.binom_n,self.binom_param,)
        elif distribution=='poisson':
            return (self.mean,self.min)
        elif distribution=='randint':
            return( self.min,self.max)
        elif distribution=='geom':
            return(len(self.data)/sum(self.data),0)
        else:
            #print(distribution,type(distribution))
            #print(distribution)
            k=getattr(stats,distribution)
            return k.fit(self.data)
        
    #calculating pdf of distribution
    
    def calc_pdf(self,distribution):
        param=self.calc_param(distribution)
        k=getattr(stats,distribution)
        args=param[:-2]
        if self.typeofdata=="continuous":
            return k.pdf(self.data,loc=param[-2],scale=param[-1],*args)
        else:
            return k.pmf(self.data,param[-2],param[-1])
        
    def calc_pdf_data(self,distribution,data): #uses the param of input random variates
        self.dataext=data
        param=self.calc_param(distribution)
        k=getattr(stats,distribution)
        args=param[:-2]
        if self.typeofdata=="continuous":
            return k.pdf(self.dataext,loc=param[-2],scale=param[-1],*args)
        else:
            return k.pmf(self.dataext,param[-2],param[-1])
    
    
         
         
     
   
    
    
    def binning_s(self,num_bins):#give num_bins=anyvalue for discrete data
        self.nbins=num_bins
        self.cnt={}
        bins=[]
        
        if self.nbins!='all':
            maxval=round(max(self.data))
            minval=round(min(self.data))
            interval=(maxval-minval)/self.nbins
            for i in range(self.nbins):
                #print(i,interval)
                bins.append((round((minval+(i*interval)),2),round((minval+(i+1)*interval),2)))
                self.cnt[(round((minval+(i*interval)),2),round((minval+(i+1)*interval),2))]=0
            for j in self.data:
                for k in bins:
                    if j >=k[0] and j<k[1]:
                        self.cnt[k]+=1
                        break
            #print(self.cnt)
            return self.cnt
        elif self.nbins=='all':
            for i in self.data:
                if i in self.cnt:
                    self.cnt[i]+=1
                else:
                    self.cnt[i]=1
            return self.cnt
        else:
            print("enter the right type of data: Discrete or continuous")
            
    def binning(self,num_bins):#give num_bins=anyvalue for discrete data
        self.nbins=num_bins
        self.cnt={}
        bins=[]
        
        if self.nbins!='all':
            maxval=max(self.data)
            minval=min(self.data)
            interval=(maxval-minval)/self.nbins
            for i in range(self.nbins):
                #print(i,interval)
                bins.append((round((minval+(i*interval)),2),round((minval+(i+1)*interval),2)))
                self.cnt[(round((minval+(i*interval)),2),round((minval+(i+1)*interval),2))]=0
            for j in self.data:
                for k in bins:
                    if j >=k[0] and j<k[1]:
                        self.cnt[k]+=1
                        break
            #print(self.cnt)
            return self.cnt
        elif self.nbins=='all':
            for i in self.data:
                if i in self.cnt:
                    self.cnt[i]+=1
                else:
                    self.cnt[i]=1
            return self.cnt
        else:
            print("enter the right type of data: Discrete or continuous")
            
            
    def pickind(self,indbins):
         indices=[]
         self.ind1=[]
         self.ind2=[]
        
         #self.chipdf,self.chiC=np.histogram(self.data,100,density=1)
         self.chipdf,self.chiC=np.histogram(self.data,self.binhist,density=1)
         self.cntchi=self.binning(indbins)
         self.chiCs=self.chiC[:-1]
         self.chipdfs=self.chipdf[:-1]
         self.chiCs=self.chiC
         self.chipdfs=self.chipdf
         
         for i in self.cntchi:
             for j in self.chiC:
                 if j>=i[0]:
                     minind1=j
                     
                     ind11= np.where(self.chiC==j)[0][0]
                     self.ind1.append(ind11)
                     #print("o",j,self.ind1)
                     
                     break
         
             for j in self.chiC:
                 if j>=i[1]:
                     maxind1=j
                     
                     ind22= np.where(self.chiC==j)[0][0]
                     self.ind2.append(ind22)
                     #print("l",j,self.ind2)
                     break
            
         #print("GOT",indices)
         if len(self.ind1)>len(self.ind2):
             self.ind2.append(len(self.chiC)-1)
         for i in range(len(self.ind1)):
             indices.append((self.ind1[i],self.ind2[i]))
         return indices,self.cntchi
         
              
         
         
     
    def mychi(self):
         #self.chiC,self.chipdf=np.histogram(self.data,100,density=1)
         #self.chiC,self.chipdf=np.histogram(self.data,self.binhist,density=1)
         self.chiC,self.chipdf=np.histogram(self.data,self.binskde,density=1)
         #self.chipdf=self.chipdf/sum(self.chipdf)
         self.myind, self.cntchi=self.pickind(6)
         n=len(self.cntchi)
         self.obs=[self.cntchi[i] for i in self.cntchi ]
         self.exp=[]
         #print(len(myind))
         
         for i in self.myind:
             #print(i)
             s=0
             #print("ivide",i)
             for j in range(i[0],i[1]):
                s+=self.chipdf[j]
             #print(s)
             self.exp.append(s)
             
         #print(obs,exp)
         
         self.exp=np.array(self.exp)
         self.exp=self.exp*self.N
         self.exp=self.exp/sum(self.exp)
         
         self.obs=self.obs/np.sum(self.obs)
         #print(len(obs),len(exp))
         #print(obs,exp)
         #print(exp,obs)
         chi,p=scipy.stats.chisquare(self.obs,self.exp,n)
         chi,p=scipy.stats.power_divergence(self.obs,self.exp,ddof=1,lambda_=1)
         return (np.round(chi,4),np.round(p,4))
    
    def GOFtest(self,dist,gofoption):
        self.gofoption=gofoption
        self.dist=dist
        #self.binning(6)
        if self.dist!='kde':
            if self.dist in self.GOFdata:
                
                self.GOFdata[self.dist].append(self.kstest(self.dist))
                #self.GOFdata[self.dist].append(self.kstest_2samp(self.dist))
                self.GOFdata[self.dist].append(self.chisquaredtest(self.dist))
            else:
                self.GOFdata[self.dist]=[]
                self.GOFdata[self.dist].append(self.kstest(self.dist))
                #self.GOFdata[self.dist].append(self.kstest_2samp(self.dist))
                self.GOFdata[self.dist].append(self.chisquaredtest(self.dist))
                #print("ivide",max(self.GOFdata[self.dist]))
            
        if self.dist=="kde":
            if self.dist in self.GOFdata:
                self.GOFdata[self.dist].append(self.Kdeks2())
                self.GOFdata[self.dist].append(self.mychi())
            else:
                self.GOFdata[self.dist]=[]
                self.GOFdata[self.dist].append(self.Kdeks2())
                self.GOFdata[self.dist].append(self.mychi())
            
    
        
        if self.gofoption=="max":
            k=[i[1] for i in self.GOFdata[self.dist]]
            self.GOFpval[self.dist]=max(k)
            return max(k)
        elif self.gofoption=='ks':
                #print(self.dist)
                self.GOFpval[self.dist]=self.GOFdata[self.dist][0][0]
                return self.GOFdata[self.dist][0][0]
        elif self.gofoption=='chi':
                self.GOFpval[self.dist]=self.GOFdata[self.dist][1][0]
                return self.GOFdata[self.dist][1][0]
        else:
            print("invalid option")
            
            
        #return 1    

    def kdecall(self,binskde):
        kdemodel=kde_silverman_both.kde_func(self.data,self.title,binskde)
        #p4kdepdf=kde_silverman_both.resample(self.data,self.kdesize,self.title)
        return kdemodel
    
    def kstest_2samp(self,dist):
        self.dist=dist
        #if self.dist in ['norm','expon','lognorm','weibull_min','triang','gamma','uniform']:
        if 'continuous' in self.distlist:
            pdfhist,C=np.histogram(self.data,self.N,density=1)
            pdf=self.calc_pdf(self.dist)
            #ks,p=stats.ks_2samp(self.data,C)
            ks,p=stats.ks_2samp(pdf,pdfhist)
            #p=-np.log10(p)
        
        elif self.dist=='binom':
            ks,p=stats.kstest(self.data,'binom',args=(self.binom_n,self.binom_param))
        
        elif self.dist=='poisson':
            ks,p=stats.kstest(self.data,'poisson',args=(self.mean,self.min))
            
        else:
            print("Enter the correct distribution: norm,weibull,expon,uniform,binom,triang,poisson")
            return -121
    
        return (np.round(ks,4),np.round(p,4))

    
    
    def bestfit(self,distlist,distributions):
        self.distributions=distributions
        self.distlist=distlist
        self.SSE(distlist,distributions)
        if 'continuous' in self.distlist:
       
           
            self.pdf, self.bin_edges = np.histogram(self.data, bins=self.binhist,density=True )
            #self.pdf=self.pdf/self.pdf.sum()
            #ploting the histogram with 100 bins
            plt.hist(self.data,bins=self.binhist,density = 1,alpha=0.4)
           
            #plotting the pdf obtained from histogram with 100 bins
            #plt.plot(self.bin_edges[:-1],self.pdf,c='r')
            #plt.legend(['histogram("fitting pdf)'])
           
            self.kdecenter,self.kdepdf,self.kdeh=self.kdecall(self.binhist)
            SSEvalkde=self.SSE_kde(self.binskde)          
       
               
            valkde= self.GOFtest('kde', self.gofoption)
            #plt.plot(self.kdecenter, self.kdepdf,color='red', linestyle="solid" )
            #plt.legend(['histogram derived pdf using KDE)'])
            dictpval_details={}
            dictpdf_details={}
            dictpdf_details['data']=self.data
        
            prog_text="Please wait while I fit"
            my_bar=st.progress(0)
            for distset in self.distributions:
                for (dist,p) in zip(distset,range(len(distset))):
                    if dist=='kde':
                        print("hihi")
                    self.distpdf=self.calc_pdf(dist)
                    self.binning(6)
                    pval=self.GOFtest(dist,self.gofoption)
                    dictpdf_details[dist]=self.distpdf
                    dictpval_details[dist]=pval
                    #st.write(p,len(distset))
                    my_bar.progress(p+1)
                my_bar.empty()
           
           
            return dictpdf_details,dictpval_details
           
        if 'discrete' in self.distlist:
            #print(self.data.dtype,"jjjjjj")
            dictpval_details={}
            dictpdf_details={}
            dictpdf_details['data']=self.data
            if self.data.dtype=='int'or 'float':
                if self.data.dtype=='int':
                    self.pdf, self.bin_edges = np.histogram(self.data, bins=max(self.data),density=True )
                if self.data.dtype=='float':
                    self.pdf, self.bin_edges = np.histogram(self.data, bins=self.binhist,density=True )
                #self.pdf, self.bin_edges = np.histogram(self.data, bins=self.binhist,density=True )
                #print(self.bin_edges,self.pdf)
                self.bin_edges=np.round(self.bin_edges)
                self.pdf=self.pdf/self.pdf.sum()
                #print(self.bin_edges,self.pdf)
                #print("1",self.pdf)
                #plt.bar(self.bin_edges[:-1],self.pdf,width=0.1)
                plt.hist(self.data,bins=self.binhist,density = True,alpha=0.4)
                dictpval_details['binedges']=self.bin_edges[:-1]
                dictpval_details['binpdf']=self.pdf
                #plotting the pdf obtained from histogram with 100 bins
                #plt.scatter(self.bin_edges[:-1],self.pdf,c='r',)
                #print("2",self.pdf)
               
                #self.SSE()
                '''self.data1,self.ppdf1=self.sorting(self.data,self.ppdf)
                plt.plot(self.data1,self.ppdf1,c='magenta')'''
           
                #define bins as {0, 1, ..., max(x), max(x)+1}
                bins = np.arange(max(self.data)+2)
                bins=self.binhist
                
                for distset in self.distributions:
                    for dist in distset:
                    
                        #using the bins to compute the density of sampled data
                        if dist=='poisson':
                            self.density_pois , _ = np.histogram(self.data, bins, density=True)
                            self.ppdf=self.calc_pdf('poisson')
                            #self.binning("all")
                            self.binning(self.binhist)
                            self.GOFtest('poisson',self.gofoption)
                            poissp=self.SSEdata['poisson'][self.SSEdata['Test'].index("SSE")]
                            #plt.plot(self.data1,self.ppdf1_cont,c='magenta')
                            #print(self.dist,"here1")
                            plt.plot(self.data,self.ppdf,c='black')
                            dictpdf_details['poisson']=self.ppdf
                            dictpval_details['poisson']=poissp
                     
                        
                         
                        elif dist=='binom':
                   
                            '''self.data1,self.bpdf1=self.sorting(self.data,self.bpdf)
                            plt.plot(self.data1,self.bpdf1,c='blue')'''
                            #bins = np.arange(max(self.data)+2)
                            #using the bins to compute the density of sampled data
                            density_bino , _ = np.histogram(self.data, bins, density=True)
                            self.bpdf=self.calc_pdf('binom')
                            #self.binning('all')
                            self.binning(self.binhist)
                            self.GOFtest('binom',self.gofoption)
                            binop=self.SSEdata['binom'][self.SSEdata['Test'].index("SSE")]
                            #plt.plot(self.data1,self.bpdf1_cont,c='blue',alpha=0.5)
                            plt.plot(self.data,self.bpdf,c='green',alpha=0.5)
                            dictpdf_details['binom']=self.bpdf
                            dictpval_details['binom']=binop
                            
                        elif dist=='geom':
                   
                            '''self.data1,self.bpdf1=self.sorting(self.data,self.bpdf)
                            plt.plot(self.data1,self.bpdf1,c='blue')'''
                            #bins = np.arange(max(self.data)+2)
                            
                            #using the bins to compute the density of sampled data
                            density_geom , _ = np.histogram(self.data, bins, density=True)
                            self.gpdf=self.calc_pdf('geom')
                            #self.binning('all')
                            self.binning(self.binhist)
                            self.GOFtest('geom',self.gofoption)
                            geomp=self.SSEdata['geom'][self.SSEdata['Test'].index("SSE")]
                            #plt.plot(self.data1,self.bpdf1_cont,c='blue',alpha=0.5)
                            plt.plot(self.data,self.gpdf,c='brown',alpha=0.5)
                            dictpdf_details['geom']=self.gpdf
                            dictpval_details['geom']=geomp
                            
                    
                            
                            
                            
                        else:
                            print("The distribution is not a valid discrete distribution",distset)
                return dictpdf_details,dictpval_details
             
          
               
                plt.legend(['poisson:{}'.format(np.round(poissp,4)),'binomial:{}'.format(np.round(binop,4)),])
               
                #plt.legend(['poisson:{}'.format(np.round(poissp,4)),'binomial:{}'.format(np.round(binop,4)),'randint:{}'.format(np.round(ranop,4)),'histogram fitting pmf'])
               
               
                #plt.legend(['histogram derived pdf','normal','exponential','triangular','uniform','binomial','poisson',])
                plt.xlabel('x-values')
                plt.ylabel('pdf')
                plt.title(self.title)
                plt.show()
            else:
                print("Data set does not belong to binomial or poisson distribution")
                return -111
    
    
    

        
    def chisquaredtest(self,dist):
        self.dist=dist
        exp_freq=[]
        #cont_dict={'expon':1,'lognorm':3,'weibull_min':2,'triang':3,'gamma':2,'uniform':2,'norm':2}
        disc_dict={'poisson':2,'binom':2,'geom':1}
        obs_freq= [i for i in self.cnt.values()]       
        if self.typeofdata =='continuous': 
            k=getattr(stats,self.dist) 
            #n=len(obs_freq)-cont_dict[self.dist] 
            n=len(obs_freq)-len(k.fit(self.data)) #gets the number of params of each distribution
            self.param=self.calc_param(self.dist)
            #print("hereher",self.param)
            args=self.param[:-2]
            for r in self.cnt.keys():
                p=k.cdf(r[1],loc=self.param[-2],scale=self.param[-1],*args)-k.cdf(r[0],loc=self.param[-2],scale=self.param[-1],*args)
                exp_freq.append(self.N*np.abs(p))
            #print(self.dist,exp_freq,obs_freq)
   
        elif self.dist in disc_dict:
            k=getattr(stats,self.dist) 
            n=len(obs_freq)-disc_dict[self.dist] 
            self.param=self.calc_param(self.dist)
            #print(self.dist, self.param)
            if type(list(self.cnt.keys())[0])=="numpy.int64":
                #print("here",self.dist)
                exp_freq = [self.N*k.pmf(r, self.param[-2],self.param[-1]) for r in self.cnt.keys()]
            else:
                
                binkeys=[ int(np.mean(i)) for i in list(self.cnt.keys())]
                exp_freq = [self.N*k.pmf(r, self.param[-2],self.param[-1]) for r in binkeys]
                #exp_freq = [self.N*k.pmf(r, self.param[-2],self.param[-1]) for r in self.cnt.keys()]
                
                
        

        else:
            print("Chisquared Test:distribution not supported",self.dist)
            return (-111,-111)
        #print(exp_freq,obs_freq)
        exp_freq=exp_freq/np.sum(exp_freq)
        obs_freq=obs_freq/np.sum(obs_freq)
        #print(self.dist,exp_freq,obs_freq)
        chi,p=scipy.stats.chisquare(obs_freq,exp_freq,n-1)
        chi,p=scipy.stats.power_divergence(obs_freq,exp_freq,ddof=1,lambda_=1)
        return (np.round(chi,4),np.round(p,4))
        
    def updateSSEdata(self,dis,score):
        score=np.round(score,4)
        if dis in self.SSEdata:
            self.SSEdata[dis].append(score)
        else:
            self.SSEdata[dis]=[score]
            
    def SSE_kde(self,binskde):
        self.binskde=binskde
        self.kc=[]
        self.kpdf=[]
        #self.histpdf,histedges=np.histogram(self.data,50,density=1)
        #self.histpdf,histedges=np.histogram(self.data,self.binhist,density=1)
        self.histpdf,histedges=np.histogram(self.data,self.binskde,density=1)
        self.histcentre=(histedges[:-1]+histedges[1:])/2.0
        #self.cent,self.spdf,self.h=self.kdecall(50)
        #self.cent,self.spdf,self.h=self.kdecall(self.binhist)
        self.cent,self.spdf,self.h=self.kdecall(self.binskde)
    
                
        #self.spdf=self.calc_pdf_data(idist, self.histcentre)
        self.score=np.sum(np.power(self.histpdf-self.spdf,2.0))
        self.updateSSEdata('kde',self.score)
        return self.score
    
    def cdf(self,sample,x,sort=False):
        if sort:
            sample.sort()
        cdf=sum(sample<=x)
        cdf=cdf/len(sample)
        return cdf
        
        
    def Kdeks2(self):
        #print(self.N,"here")
        histpdf,histedges=np.histogram(self.data,self.N,density=1)
        histcentre1=(histedges[:-1]+histedges[1:])/2.0
        kkde,pkde=scipy.stats.ks_2samp(histcentre1, self.data)
        return (np.round(kkde,4),np.round(pkde,4))
        

        
        
    def SSE(self,distlist,distributions):
        self.distlist=distlist
        self.distributions=distributions
        if 'SSE' not in self.SSEdata['Test']:
            self.SSEdata['Test'].append('SSE')
        
        
        #cont=['norm','expon','lognorm','weibull_min','triang','gamma','uniform']
            
        self.chulist={}
        if 'continuous' in self.distlist:
            for idistset in self.distributions:
                for idist in idistset:
                    #self.histpdf=self.histpdf/self.histpdf.sum()
                    #self.histpdf,histedges=np.histogram(self.data,50,density=1)
                    self.histpdf,histedges=np.histogram(self.data,self.binhist,density=1)
                    # print(self.histpdf.sum())
                    #self.histpdf1=self.histpdf1/self.histpdf1.sum()
                    #print(self.histpdf.sum())
                    self.histcentre=(histedges[:-1]+histedges[1:])/2.0
                    #self.histcentre,self.histpdf=self.smoothline(self.histcentre1, self.histpdf1)
                    self.spdf=self.calc_pdf_data(idist, self.histcentre)
                    self.score=np.sum(np.power(self.histpdf-self.spdf,2.0))
                    self.ksscore=-np.log10(stats.ks_2samp(self.histpdf, self.spdf)[1])
                    self.chulist[idist]=self.ksscore
                    self.updateSSEdata(idist,self.score)
        
        if 'discrete' in self.distlist:
            
            #self.histpdf,self.histedges=np.histogram(self.data,len(self.binning('all')),density=True)
            self.histpdf,self.histedges=np.histogram(self.data,self.binhist,density=True)
            #print(self.histpdf.sum())
            self.histpdf=self.histpdf/self.histpdf.sum()
            #print(self.histpdf.sum())
            
            self.histcentre=(self.histedges[:-1]+self.histedges[1:])/2.0
            #convert the x values to integers: if they are in float then pmf values will become zero!!
            self.histcentre=np.array(self.histcentre, dtype=int).ravel()
            
            self.spdf=stats.poisson.pmf(self.histcentre,self.mean,loc=self.min)
            self.score=np.sum(np.power(self.histpdf-self.spdf,2.0))
            self.updateSSEdata('poisson',self.score)
            
            self.spdf=stats.binom.pmf(self.histcentre,self.binom_n,self.binom_param)
            self.score=np.sum(np.power(self.histpdf-self.spdf,2))
            self.updateSSEdata('binom',self.score)
            
            self.spdf=stats.geom.pmf(self.histcentre,self.geomparam)
            self.score=np.sum(np.power(self.histpdf-self.spdf,2))
            self.updateSSEdata('geom',self.score)            
            '''self.spdf=stats.randint.pmf(self.histcentre,self.min,self.max)
            self.score=np.sum(np.power(self.histpdf-self.spdf,2))
            self.updateSSEdata('randint',self.score)'''
       
        
        
    def kstest(self,dist):
        self.dist=dist
        #if self.dist in ['norm','expon','lognorm','weibull_min','triang','gamma','uniform']:
        if 'continuous' in self.distlist:
            param=self.calc_param(self.dist)
            ks,p=stats.kstest(self.data,self.dist,param)
        
        elif self.dist=='binom':
            ks,p=stats.kstest(self.data,'binom',args=(self.binom_n,self.binom_param))
        
        elif self.dist=='poisson':
            ks,p=stats.kstest(self.data,'poisson',args=(self.mean,self.min))
        elif self.dist=='geom':
            ks,p=stats.kstest(self.data,'geom',args=(len(self.data)/sum(self.data),min(self.data)))
            
        else:
            print("Enter the correct distribution: norm,weibull,expon,uniform,binom,triang,poisson")
            return -121
    
        return (np.round(ks,4),np.round(p,4))
    

    

    def printresult(self):
        
        for i in self.GOFdata:
            self.GOFdata[i].append(self.SSEdata[i][0])
        GOF=pd.DataFrame(self.GOFdata).T

        GOF.rename({0: GOF.iloc[0][0], 1: GOF.iloc[0][1],2: GOF.iloc[0][2]}, axis=1, inplace=True)

        GOF.drop('Test',axis=0,inplace=True)
        cols=list(GOF.columns)
        #print(cols)
        for i in cols[:2]:
            GOF[i] = GOF[i].apply(lambda X: X[0])
        GOF.reset_index(inplace=True)
        GOF.rename({'index': 'Test'}, axis=1, inplace=True)
        self.GOFfinal=GOF
        #print(self.GOFfinal)
            
        #print("-----------------------------------------"*3)
        #print(self.title)
        #print("-----------------------------------------"*3)
        #print (tabulate((self.GOFdata),headers=self.GOFdata.keys()))
        #print("----------------------------------"*3)
        #print (tabulate((self.SSEdata),headers=self.SSEdata.keys()))
        #print("----------------------------------"*3)
        return GOF,self.SSEdata
        
    
    def smooth(self,X, window):
        box = np.ones(window) / window
        X_smooth = np.convolve(X, box, mode='same')
        return X_smooth
    
    def smoothline(self,xs,ys):
        xnew=None
        window=1
        extpoints = np.linspace(0, len(xs), len(xs) * 1)
        spl = make_interp_spline(range(0, len(xs)), xs, k=3)
        # Compute x-labels
        xnew = spl(extpoints)
        
        
        ynew=None
        
        if ys is not None:
            ys = self.smooth(ys, window)
            # Interpolate ys line
            spl = make_interp_spline(range(0, len(ys)), ys, k=3)
            ynew = spl(extpoints)
            
        return xnew,ynew
    
    
    
def getcontinuousdist():
    continuous_all=[]
    all_dist = [getattr(stats, d) for d in dir(stats) if isinstance(getattr(stats, d), stats.rv_continuous)]
    filtered = [x for x in all_dist if ((x.a <= 0) & (x.b == math.inf))]
    filtered=all_dist
    pat = r's.[a-zA-Z0-9_]+_g'
    
    for i in filtered:
        s = str(i)
        #print(s)
        span=re.search(pat, s).span()
        dist=s[span[0]+2:span[1]-2]
        continuous_all.append(dist)
        
    for i in ['levy_stable','studentized_range','kstwo','skew_norm','vonmises','trapezoid','reciprocal']:
        continuous_all.remove(i)
    return continuous_all
    
'''continuous_popular=['expon','norm','lognorm','triang','uniform','weibull_min','gamma']
discrete_popular=['binom','poisson','geom']

continuous_all=listparamsofdistributions.getcontinuousdist()
#self,data,typeofdata,title,binhist,gofoption,distlist,distributions)

#reciprocal,trapezoid,vonmises
#GOFdf=pd.DataFrame.from_dict(GOFdata)
#GOFdf = GOFdf.set_index('Test')

df=pd.read_csv("sample_data.csv")
data=df['temp']
y= modelmatch(data,'continuous','Weibull distribution',49,'ks',['continuous'],[continuous_popular])
y.bestfit(['continuous'],[continuous_all])
y.printresult()
'''


'''discrete_popular=['binom','poisson','geom']
df=pd.read_csv("sample_data.csv")
data=df['jobarrival_Machine']

df=pd.read_csv("sample_data4.csv")
data=df['timetaken_transport']
d=np.random.geometric(0.4, size=2000)
y= modelmatch(data,'discrete','Weibull distribution',8,'ks',['discrete'],[discrete_popular])
y.bestfit(['discrete'],[discrete_popular])
y.printresult()'''