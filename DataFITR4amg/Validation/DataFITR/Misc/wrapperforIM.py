#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# @title WrapperforIM

import numpy as np
import IM
import kde_silverman
import pandas as pd
from tabulate import tabulate
import scipy
from scipy.stats import uniform, randint
class wrapperforIM:
    def __init__(self):
        self.df_continuous = pd.DataFrame(index=range(0, 10), columns=['dist', 'SSE', 'CHI','KS','PARAMS'])
        self.df_discrete = pd.DataFrame(index=range(0, 2), columns=['dist', 'SSE','PARAMS'])

        global inputdict,kdedict,nofitdict
        inputdict={}
        kdedict={}
        nofitdict={}



    def transformX(self, X_dict,fitform,bins,typeofdata,gofoption,kdesize):
        self.gofoption=gofoption
        self.X_dict=X_dict
        self.fitform=fitform
        self.bins=bins
        self.typeofdata=typeofdata
        self.kdesize=kdesize
        disc=['binom','poisson']
        cont=['norm','expon','lognorm','weibull','triangular','gamma','uniform']
        if self.typeofdata=='discrete':
            self.dist_list=disc
        elif self.typeofdata=='continuous':
            self.dist_list=cont

        j=0
        for name in self.X_dict:
            print(name)
            if self.fitform[j]=='STDDST':
                self.fitDST(self.X_dict[name],self.fitform[j],self.typeofdata[j],name,self.bins[j],j,gofoption)
            elif self.fitform[j]=='KDE':
                self.fitKDE(self.X_dict[name],name)
            elif self.fitform[j]=='RAW':
                print("Using input data as is.")
                self.nofit(self.X_dict[name],name)

            j=j+1


    def nofit(self,data,name):
        self.name=name
        self.data=data
        nofitdict[name]=self.data





    def fitDST(self,data,fitform,typ,name,numbin,j,gofoption):
            global inputdict
            #print("here")
            if typ=='continuous':
                self.model= IM.modelmatch(data,typ,name,numbin,self.gofoption)
                f=self.model.bestfit()
                if f==-111:
                    self.nofit(data,name)
                    print("returning data as is. Find the data in nofitdict")
                    return
                self.model.printresult()

                if self.gofoption in ['ks','chi']:
                    GOF=self.model.GOFdata
                    GOFlist=self.model.GOFpval
                    #print("hhhhh",self.model.GOFpval)
                    keys_cont=[i for i in GOF.keys()]
                    #print(keys_cont)
                    maxgof=keys_cont[1]
                    for i in GOFlist:
                        if GOFlist[i]<GOFlist[maxgof]:
                            maxgof=i
                    distpval=[]
                    for i in GOFlist:
                        if round(GOFlist[i],3)==round(GOFlist[maxgof]):
                            distpval.append(i)
                else:
                    GOF=self.model.GOFdata
                    GOFlist=self.model.GOFpval
                    #print("hhhhh",self.model.GOFpval)
                    keys_cont=[i for i in GOF.keys()]
                    #print(keys_cont)
                    maxgof=keys_cont[1]
                    for i in GOFlist:
                        if GOFlist[i]>GOFlist[maxgof]:
                            maxgof=i
                    distpval=[]
                    for i in GOFlist:
                        if round(GOFlist[i],3)==round(GOFlist[maxgof]):
                            distpval.append(i)

                if len(distpval)!=1:
                    SSdata=self.model.SSEdata
                    keys=[i for i in SSdata.keys()]
                    maxsse=keys[1]
                    for i in keys[1:]:
                        if SSdata[i]<SSdata[maxsse]:
                            maxsse=i
                    if maxsse in distpval:
                        maxgof=maxsse

                print(name,maxgof)
                if maxgof =="kde":
                    self.fitKDE(data,name)

                else:
                    params= self.model.calc_param(maxgof)
                    inputdict[name]=(maxgof,params)
            elif typ=='discrete':
                self.model= IM_Lek.modelmatch(data,typ,name,numbin,self.gofoption)
                f=self.model.bestfit()
                if f==-111:
                    self.nofit(data,name)
                    print("returning data as is. Find the data in nofitdict")
                    return
                #self.model.printresult()
                SSdata=self.model.SSEdata
                keys=[i for i in SSdata.keys()]
                maxsse=keys[1]
                for i in keys[1:]:
                    if SSdata[i]<SSdata[maxsse]:
                        maxsse=i

                    maxgof=maxsse
                params= self.model.calc_param(maxgof)
                inputdict[name]=(maxgof,params)

    def printWrapperresult(self):

        #print(inputdict)
        #print("--------------------------------------"*3)
        #print (tabulate((inputdict),headers=inputdict.keys()))
        return inputdict

    def retkderesult(self):
        return kdedict

    def nofitresult(self):
        return nofitdict



    def fitKDE(self,data,name):
        self.data=data
        self.name=name

        #model=kde_silverman_both.kde_func(self.data,self.name)
        kdedict[self.name]=resample(self.data,self.kdesize,self.name)



