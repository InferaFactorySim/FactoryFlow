# @title whole code

# @title Simulation of PCB Assembly Line
# ref model

import simpy,random,scipy
#import wrapper
#from perf_measure import performanceEval
import numpy as np
import time
import matplotlib.pyplot as plt

import simpy
import random
import csv
from scipy.stats import expon, triang, uniform, norm
import pandas as pd
import numpy as np

#print(f'STARTING SIMULATION')
#print(f'----------------------------------')

#Parameters

#-------------------------------------------------


# @title performance evaluation


class performanceEval:
    def throughput(self, total_num_products, total_plant_time):
        return total_num_products / (total_plant_time / 60)

    def cycletime(self, product_time):
        return np.mean(product_time)

    def resourceutil(self, servicetime, total_plant_time):
        return sum(servicetime) / total_plant_time

    def reserve_util(self, listA, time):
        unittaken = [listA[i] - listA[i + 1] for i in range(len(listA) - 1)]
        return sum(unittaken) / (time / 60)

# Refactored performance function
def performance(delays, total_plant_time, ru_time,throughput, num_good ):
    metrics={}

    perf_eval = performanceEval()
    metrics["throughput"] = throughput
    metrics['num_good'] = num_good
    metrics["total_plant_time"] = total_plant_time

    for item in delays:
      metrics[f"{item}_cycletime"] = perf_eval.cycletime(delays[item])
      metrics[f"{item}_util"] = perf_eval.resourceutil(ru_time[item], total_plant_time)

    return metrics

# @title n_sim

def wrappersim(delays):
    w= wrapperforIM()
    inp=delays
    #fit=["KDE","KDE","KDE","KDE"]
    fit=["STDDST","STDDST","STDDST","STDDST"]
    bind=[100,100,100,100]
    typd=['continuous','continuous','continuous','continuous',]
    w.transformX(inp,fit,bind,typd,'ks',10000)
    #w.transformX({'sum':d}, ["STDDST"], [100], ['continuous'])
    outforwrapper=w.printWrapperresult()
    size=10000
    outdictwrapper={}
    for i in outforwrapper:
        if i in inp:
            gendist=getattr(scipy.stats, outforwrapper[i][0])
            params=outforwrapper[i][1]
            loc=params[-2]
            scale=params[-1]
            args=params[:-2]
            outdictwrapper[i]=gendist.rvs(loc=loc,scale=scale,*args,size=size)
    return outdictwrapper,outforwrapper





def board_loader(env, num_boards, loader_store, delay_list,resource_times):
    for i in range(num_boards):
        start = env.now

        delay= scipy.stats.expon.rvs(loc=0.0,scale=0.5,size=1)
        delay=float(delay[0])
        yield env.timeout(delay)  # mean = 2


        delay_list['load'].append(delay)
        resource_times['load'].append(delay)
        yield loader_store.put((f'PCB-{i}', env.now))

def solder_printer(env, loader_store, printer_store, delay_list,resource_times):
    # Triangular(1, 2, 3): c = (mode - low) / (high - low) = (2-1)/(3-1) = 0.5
    while True:
        pcb, _ = yield loader_store.get()
        start = env.now
        args=[0.5]
        delay = scipy.stats.triang.rvs(*args,loc=1.0,scale=2.0,size=1)
        delay=float(delay[0])
        yield env.timeout(delay)  # (low=1, mode=2, high=3)
        delay_list['solder'].append(delay)
        resource_times['solder'].append(delay)
        yield printer_store.put((pcb, env.now))

def component_placer(env, printer_store, placer_store, delay_list,resource_times):
    while True:
        pcb, _ = yield printer_store.get()
        start = env.now
        delay = scipy.stats.uniform.rvs(loc=3.0,scale=6,size=1)
        delay=float(delay[0])
        yield env.timeout(delay)  # Uniform(3,6) => loc=3, scale=3

        delay_list['place'].append(delay)
        resource_times['place'].append(delay)
        yield placer_store.put((pcb, env.now))

def reflow_oven(env, placer_store, oven_store, delay_list,resource_times):
    while True:
        pcb, _ = yield placer_store.get()
        start = env.now
        delay = scipy.stats.norm.rvs(loc=2,scale=0.25,size=1)
        delay=float(delay[0])
        yield env.timeout(delay)  # avoid negative values
        delay_list['reflow'].append(delay)
        resource_times['reflow'].append(delay)
        yield oven_store.put((pcb, env.now))

def inspection(env, oven_store, inspect_store, delay_list,resource_times):
    while True:
        pcb, _ = yield oven_store.get()
        start = env.now
        delay= scipy.stats.expon.rvs(loc=0.0,scale=3,size=1)
        delay=float(delay[0])
        yield env.timeout(delay)  # mean = 3
        delay_list['inspect'].append(delay)
        resource_times['inspect'].append(delay)
        yield inspect_store.put((pcb, env.now))

def packing(env, inspect_store, delay_list,resource_times, packed_boards):
    while True:
        pcb, _ = yield inspect_store.get()
        start = env.now
        delay = scipy.stats.uniform.rvs(loc=2,scale=4, size=1)
        delay=float(delay[0])
        yield env.timeout(delay)  # Uniform(2,4) => loc=2, scale=2
        delay_list['pack'].append(delay)

        resource_times['pack'].append(delay)

        packed_boards.append(pcb)
#-------------------------------------------------

def sim(num_boards=100):
    env = simpy.Environment()
    delay_list = {step: [] for step in ['load', 'solder', 'place', 'reflow', 'inspect', 'pack']}
    resource_times = {step: [] for step in ['load', 'solder', 'place', 'reflow', 'inspect', 'pack']}
    packed_boards = []

    # Define buffers between steps
    loader_store = simpy.Store(env)
    printer_store = simpy.Store(env)
    placer_store = simpy.Store(env)
    oven_store = simpy.Store(env)
    inspect_store = simpy.Store(env)

    # Launch processes
    env.process(board_loader(env, num_boards, loader_store, delay_list, resource_times))
    env.process(solder_printer(env, loader_store, printer_store, delay_list, resource_times))
    env.process(component_placer(env, printer_store, placer_store, delay_list, resource_times))
    env.process(reflow_oven(env, placer_store, oven_store, delay_list, resource_times))
    env.process(inspection(env, oven_store, inspect_store, delay_list, resource_times))
    env.process(packing(env, inspect_store, delay_list, resource_times, packed_boards))

    # Run simulation
    env.run()
    total_plant_time = env.now
    num_finished_goods = len(packed_boards)
    throughput = num_finished_goods / (total_plant_time / 60)
    # print(f"Finished Boards: {num_finished_goods}")
    # print(f"Total Plant Time: {total_plant_time:.2f} mins")
    # print(f"Throughput: {throughput:.2f} boards per hour")

    return total_plant_time,delay_list,resource_times, throughput, num_finished_goods




def n_sim(n_runs=10, num_boards=100):
    print("Starting simulations...")
    perf_eval = performanceEval()
    all_metrics = []

    for run in range(n_runs):
        #print(f"\nRun {run + 1}/{n_runs}")

        # Run the simulation
        total_plant_time, delay_list, resource_times, throughput, num_finished_goods = sim(num_boards)

        # Compute performance metrics using provided function
        metrics = performance(
            delays=delay_list,
            total_plant_time=total_plant_time,
            ru_time=resource_times,
            throughput=throughput,
            num_good=num_finished_goods
        )

       
        all_metrics.append(metrics)

    # Aggregate results: mean of each metric
    avg_metrics = {}
    keys = all_metrics[0].keys()
    for key in keys:
        avg_metrics[key] = np.mean([m[key] for m in all_metrics])

    return avg_metrics


start=time.time()
print("starting")
n=1
k=(n_sim(n_runs=10000, num_boards=100))
end=time.time()
print("\ntimetaken",end-start)
print("\nResults",k)

def wrappersim(delays):
    w= wrapperforIM()
    inp=delays
    for name in inp:
            print(name,inp)
    #fit=["KDE","KDE","KDE","KDE","KDE","KDE"]
    gof=["SSE","SSE","SSE","SSE","SSE","SSE"]
    fit=["STDDST","STDDST","STDDST","STDDST","STDDST","STDDST"]
    kdesiz=[60,60,60,60,60,60]
    bind=[100,100,100,100,100,100]
    typd=['continuous','continuous','continuous','continuous','continuous','continuous',]
    w.transformX(inp,fit,bind,typd,gof,kdesiz)
    #w.transformX({'sum':d}, ["STDDST"], [100], ['continuous'])
    outforwrapper=w.printWrapperresult()
    size=10000
    outdictwrapper={}
    for i in outforwrapper:
        if i in inp:
            gendist=getattr(scipy.stats, outforwrapper[i][0])
            params=outforwrapper[i][1]
            loc=params[-2]
            scale=params[-1]
            args=params[:-2]
            outdictwrapper[i]=gendist.rvs(loc=loc,scale=scale,*args,size=size)
    return outdictwrapper
# @title 1-round wrappersimmer
def nsim_forwrapper():

    total_plant_time, delay_list, resource_times, throughput, num_finished_goods = sim(num_boards=100)
    #print("total_plant_time",total_plant_time

    odict=wrappersim(delay_list)
    print(odict)

nsim_forwrapper()