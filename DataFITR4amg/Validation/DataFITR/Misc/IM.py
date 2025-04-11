

#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from scipy.stats import kstest,poisson,norm,triang,skew,chisquare
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
#import kde_silverman_both

import scipy.stats as stats
import statistics
import scipy
import statsmodels.api
import math
import pandas as pd


random.seed(42)

class modelmatch:
    def __init__(self,data,typeofdata,title,binhist,gofoption):
        self.data=np.sort(data)
        self.datamain=data
        self.typeofdata=typeofdata
        self.title=title
        self.titleplot=str(self.title)+":"+gofoption[0]
        self.binhist=binhist
        self.N=len(self.data)
        self.GOFdata = {"Test": ["KStest", "Chi squared Test"]}
        self.SSEdata = {"Test": []}
        self.GOFpval={}
        self.gofoption=gofoption
        self.kdesize=1000

        if self.typeofdata=='continuous':
            self.min=min(self.data)
            self.max=max(self.data)

            self.mean=np.mean(self.data)
            self.sd=np.std(self.data)
            #self.lnmean=np.mean(np.log(self.data))
            #self.lnsd=np.std(np.log(self.data))
            self.lamda=1/self.mean #if stats.expon
            self.weibull_param=stats.weibull_min.fit(self.data, floc=0)
            self.s, self.lloc, self.lscale = stats.lognorm.fit(self.data, floc=0)
            if any(x < 0 for x in self.data):
                print("There is at least one negative number in the list.")
                self.gamma_param = (1.99,0,1)
            else:
                print("All numbers are non-negative.")
                self.gamma_param=stats.gamma.fit(self.data)
            self.mode=statistics.mode(self.data)
            self.median=np.median(self.data)
            self.c=(self.mode-self.min)/(self.max-self.min)
            self.triang_param=stats.triang.fit(self.data)
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
            self.binom_n=max(self.data)
            self.binom_param=self.mean/self.binom_n



    def calc_param(self,distribution):
        if distribution=='binom':
            return (self.binom_n,self.binom_param,)
        elif distribution=='poisson':
            return (self.mean,self.min)
        elif distribution=='randint':
            return( self.min,self.max)
        else:
            k=getattr(stats,distribution)
            #print(self.data)
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

    def pickind(self,indbins):
         indices=[]

         self.chipdf,self.chiC=np.histogram(self.data,10001,density=1)
         self.cntchi=self.binning(indbins)
         self.chiCs=self.chiC[:-1]
         self.chipdfs=self.chipdf[:-1]

         for i in self.cntchi:
             for j in self.chiC:
                 if j>=i[0]:
                     minind1=j
                     #print(j)
                     ind1=np.where(self.chiC==j)[0][0]
                     break

             for j in self.chiCs:
                 if j>=i[1]:
                     maxind1=j
                     ind2=np.where(self.chiC==j)[0][0]
                     break
             indices.append((ind1,ind2))
         return indices,self.cntchi







    def binning(self,num_bins):#give num_bins=anyvalue for discrete data
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


    def pickind(self,indbins):
         indices=[]


         self.chipdf,self.chiC=np.histogram(self.data,10001,density=1)
         self.cntchi=self.binning(indbins)
         self.chiCs=self.chiC[:-1]
         self.chipdfs=self.chipdf[:-1]

         for i in self.cntchi:
             for j in self.chiC:
                 if j>=i[0]:
                     minind1=j
                     #print(j)
                     ind11= np.where(self.chiC==j)[0][0]
                     break

             for j in self.chiCs:
                 if j>=i[1]:
                     maxind1=j
                     ind22= np.where(self.chiC==j)[0][0]
                     break
             try:
                 indices.append((ind11,ind22))
             except:
                 ind11=len(self.chiC)-2
                 ind22=len(self.chiC)-1
                 indices.append((ind11,ind22))
                 #print("GOT",indices)
         #print("GOT",indices)
         return indices,self.cntchi




    def mychi(self):
         self.chiC,self.chipdf=np.histogram(self.data,100,density=1)
         #self.chipdf=self.chipdf/sum(self.chipdf)
         myind, self.cntchi=self.pickind(10)
         n=len(self.cntchi)
         obs=[self.cntchi[i] for i in self.cntchi ]
         exp=[]
         #print(len(myind))
         for i in myind:
             #print(i)
             s=0
             #print("ivide",i)
             for j in range(i[0],i[1]):
                s+=self.chipdf[j]
             #print(s)
             exp.append(s)

         #print(obs,exp)

         exp=np.array(exp)
         exp=exp*self.N
         exp=exp/sum(exp)

         obs=obs/np.sum(obs)
         #print(len(obs),len(exp))
         #print(obs,exp)
         #print(exp,obs)
         chi,p=scipy.stats.chisquare(obs,exp,)
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
                self.GOFpval[self.dist]=self.GOFdata[self.dist][0][0]
                return self.GOFdata[self.dist][0][0]
        elif self.gofoption=='chi':
                self.GOFpval[self.dist]=self.GOFdata[self.dist][1][0]
                return self.GOFdata[self.dist][1][0]
        else:
            print("invalid option")


        #return 1

    def kdecall(self,binskde):
        kdemodel=kde_func(self.data,self.title,binskde)
        #p4kdepdf=kde_silverman_both.resample(self.data,self.kdesize,self.title)
        return kdemodel

    def kstest_2samp(self,dist):
        self.dist=dist
        if self.dist in ['norm','expon','lognorm','weibull_min','triang','gamma','uniform']:
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

        return (np.round(ks,7),np.round(p,7))


    def bestfit(self):
        #estimating pdf based on 100 bins from histogram function
        ####self.pdf, self.bin_edges = np.histogram(self.data, bins=self.binhist,density=True )
        #self.pdf=self.pdf/self.pdf.sum()
        #ploting the histogram with 100 bins
        ####plt.hist(self.data,bins=self.binhist,density = 1,alpha=0.4)
        #plotting the pdf obtained from histogram with 100 bins
        ####plt.plot(self.bin_edges[:-1],self.pdf,c='r')
        ####plt.legend(['histogram("fitting pdf)'])
        cont=['norm','expon','lognorm','dweibull','triang','gamma','uniform',]
        self.SSE()
        if self.typeofdata=='continuous':

            self.pdf, self.bin_edges = np.histogram(self.data, bins=self.binhist,density=True )
            #self.pdf=self.pdf/self.pdf.sum()
            #ploting the histogram with 100 bins
            plt.hist(self.data,bins=self.binhist,density = 1,alpha=0.4)

            #plotting the pdf obtained from histogram with 100 bins
            #plt.plot(self.bin_edges[:-1],self.pdf,c='r')
            #plt.legend(['histogram("fitting pdf)'])

            self.kdecenter,self.kdepdf,self.kdeh=self.kdecall(100)
            SSEvalkde=self.SSE_kde()

            '''if self.gofoption=='ks':
                valkde=self.Kdeks2()

            elif self.gofoption=='chi':
                valkde=self.mychi()[0]'''


            valkde= self.GOFtest('kde', self.gofoption)
            plt.plot(self.kdecenter, self.kdepdf,color='red', linestyle="solid" )
            #plt.legend(['histogram derived pdf using KDE)'])



            self.npdf=self.calc_pdf('norm')
            self.binning(6)
            normp=self.GOFtest('norm',self.gofoption)
            #print(normp)
            plt.plot(self.data,self.npdf,c='black')
            #plt.legend(['normal'])

            self.epdf=self.calc_pdf('expon')
            self.binning(6)
            exponp=self.GOFtest('expon',self.gofoption)
            plt.plot(self.data,self.epdf,c='g')
            #plt.legend(['exponential'])

            self.tpdf=self.calc_pdf('triang')
            self.binning(6)
            triangp=self.GOFtest('triang',self.gofoption)
            plt.plot(self.data,self.tpdf,c='brown')
            #plt.legend(['triangular'])

            self.wpdf=self.calc_pdf('weibull_min')
            self.binning(6)
            weibp=self.GOFtest('weibull_min',self.gofoption)
            plt.plot(self.data,self.wpdf,c='yellow')
            #plt.legend(['weibull_min'])

            self.updf=self.calc_pdf('uniform')
            self.binning(6)
            unip=self.GOFtest('uniform',self.gofoption)
            plt.plot(self.data,self.updf,c='orange')
            #plt.legend(['uniform'])

            self.lpdf=self.calc_pdf('lognorm')
            self.binning(6)
            lnp=self.GOFtest('lognorm',self.gofoption)
            plt.plot(self.data,self.lpdf,linestyle='dashed',c='rosybrown')
            #plt.legend(['lognorm'])

            self.gpdf=self.calc_pdf('gamma')
            self.binning(6)
            gamnp=self.GOFtest('gamma',self.gofoption)
            plt.plot(self.data,self.gpdf,linestyle='dashed',c='blue')
            #plt.legend(['gamma'])

            '''plt.legend(['histogram derived pdf:{}'.format(np.round(valkde,4)),'normal:{}'.format(np.round(normp,4)),'exponential:{}'.format(np.round(exponp,4)),'triangular:{}'.format(np.round(triangp,4)),'weibull:{}'.format(np.round(weibp,4)),'uniform:{}'.format(np.round(unip,4)),'lognorm:{}'.format(np.round(lnp,4)),'gamma:{}'.format(np.round(gamnp,4))])
            #plt.legend(['histogram derived pdf','normal','exponential','triangular','uniform','binomial','poisson',])
            plt.xlabel('x-values')
            plt.ylabel('pdf')
            plt.title(self.title)'''
            plt.grid()
            plt.show()

        if self.typeofdata=='discrete':
            if self.data.dtype=='int':
                self.pdf, self.bin_edges = np.histogram(self.data, bins=self.binhist,density=True )
                #print(self.bin_edges)
                self.bin_edges=np.round(self.bin_edges)
                #self.pdf=self.pdf/self.pdf.sum()
                #print("1",self.pdf)
                plt.bar(self.bin_edges[:-1],self.pdf,width=0.1)
                #plotting the pdf obtained from histogram with 100 bins
                plt.scatter(self.bin_edges[:-1],self.pdf,c='r',)
                #print("2",self.pdf)

                #self.SSE()
                '''self.data1,self.ppdf1=self.sorting(self.data,self.ppdf)
                plt.plot(self.data1,self.ppdf1,c='magenta')'''

                #define bins as {0, 1, ..., max(x), max(x)+1}
                bins = np.arange(max(self.data)+2)
                #using the bins to compute the density of sampled data
                self.density_pois , _ = np.histogram(self.data, bins-.5, density=True)
                self.ppdf=self.calc_pdf('poisson')
                self.binning("all")
                self.GOFtest('poisson',gofoption)
                poissp=self.SSEdata['poisson'][self.SSEdata['Test'].index("SSE")]
                #plt.plot(self.data1,self.ppdf1_cont,c='magenta')
                plt.plot(self.data,self.ppdf,c='black')



                '''self.data1,self.bpdf1=self.sorting(self.data,self.bpdf)
                plt.plot(self.data1,self.bpdf1,c='blue')'''
                bins = np.arange(max(self.data)+2)
                #using the bins to compute the density of sampled data
                density_bino , _ = np.histogram(self.data, bins-.5, density=True)
                self.bpdf=self.calc_pdf('binom')
                self.binning('all')
                self.GOFtest('binom',gofoption)
                binop=self.SSEdata['binom'][self.SSEdata['Test'].index("SSE")]
                #plt.plot(self.data1,self.bpdf1_cont,c='blue',alpha=0.5)
                plt.plot(self.data,self.bpdf,c='green',alpha=0.5)


                '''bins = np.arange(max(self.data)+2)
                #using the bins to compute the density of sampled data
                density_bino , _ = np.histogram(self.data, bins-.5, density=True)
                self.dupdf=self.calc_pdf('randint')
                self.binning('all')
                #self.GOFtest('disUniform',gofoption)
                ranop=self.SSEdata['randint'][self.SSEdata['Test'].index("SSE")]
                #plt.plot(self.data1,self.bpdf1_cont,c='blue',alpha=0.5)
                plt.plot(self.data,self.dupdf,c='magenta',alpha=0.5)
                '''
                #plotting the samples density
                #plt.scatter(bins[:-1],density_pois)
                #plt.plot(bins[:-1], stats.poisson.pmf(bins[:-1], 1/np.mean(y.data)), 'violet', ms=8, label='poisson2')
                #plotting the actual density

                plt.legend(['poisson:{}'.format(np.round(poissp,4)),'binomial:{}'.format(np.round(binop,4)),'histogram fitting pmf'])

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
        cont_dict={'expon':1,'lognorm':3,'weibull_min':2,'triang':3,'gamma':2,'uniform':2,'norm':2}
        disc_dict={'poisson':2,'binom':2}
        obs_freq= [i for i in self.cnt.values()]
        if self.dist in cont_dict:
            k=getattr(stats,self.dist)
            n=len(obs_freq)-cont_dict[self.dist]
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
            exp_freq = [self.N*k.pmf(r, self.param[-2],self.param[-1]) for r in self.cnt.keys()]


        else:
            print("Chisquared Test:distribution not supported",self.dist)
            return (-111,-111)

        exp_freq=exp_freq/np.sum(exp_freq)
        obs_freq=obs_freq/np.sum(obs_freq)
        chi,p=scipy.stats.chisquare(obs_freq,exp_freq,n-1)
        return (np.round(chi,4),np.round(p,4))

    def updateSSEdata(self,dis,score):
        if dis in self.SSEdata:
            self.SSEdata[dis].append(score)
        else:
            self.SSEdata[dis]=[score]

    def SSE_kde(self):
        self.kc=[]
        self.kpdf=[]

        self.histpdf,histedges=np.histogram(self.data,50,density=1)
        self.histcentre=(histedges[:-1]+histedges[1:])/2.0
        self.cent,self.spdf,self.h=self.kdecall(50)


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

        histpdf,histedges=np.histogram(self.data,self.N,density=1)
        histcentre1=(histedges[:-1]+histedges[1:])/2.0
        kkde,pkde=scipy.stats.ks_2samp(histcentre1, self.data)
        return (np.round(kkde,4),np.round(pkde,4))




    def SSE(self):
        if 'SSE' not in self.SSEdata['Test']:
            self.SSEdata['Test'].append('SSE')


        cont=['norm','expon','lognorm','weibull_min','triang','gamma','uniform']

        self.chulist={}
        if self.typeofdata=='continuous':
            for idist in cont:
                #self.histpdf=self.histpdf/self.histpdf.sum()
                self.histpdf,histedges=np.histogram(self.data,50,density=1)
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

        if self.typeofdata=='discrete':

            self.histpdf,self.histedges=np.histogram(self.data,len(self.binning('all')),density=True)
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

            '''self.spdf=stats.randint.pmf(self.histcentre,self.min,self.max)
            self.score=np.sum(np.power(self.histpdf-self.spdf,2))
            self.updateSSEdata('randint',self.score)'''



    def kstest(self,dist):
        self.dist=dist
        if self.dist in ['norm','expon','lognorm','weibull_min','triang','gamma','uniform']:
            param=self.calc_param(self.dist)
            ks,p=stats.kstest(self.data,self.dist,param)

        elif self.dist=='binom':
            ks,p=stats.kstest(self.data,'binom',args=(self.binom_n,self.binom_param))

        elif self.dist=='poisson':
            ks,p=stats.kstest(self.data,'poisson',args=(self.mean,self.min))

        else:
            print("Enter the correct distribution: norm,weibull,expon,uniform,binom,triang,poisson")
            return -121

        return (np.round(ks,4),np.round(p,4))


    def printresult(self):
        print("--------------------------------------"*3)
        print(self.title)
        print("--------------------------------------"*3)
        print (tabulate((self.GOFdata),headers=self.GOFdata.keys()))
        print("--------------------------------------"*3)
        print (tabulate((self.SSEdata),headers=self.SSEdata.keys()))
        print("--------------------------------------"*3)


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




