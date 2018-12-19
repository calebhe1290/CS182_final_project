# -*- coding: utf-8 -*-
"""
Created on Mon Dec 17 21:15:28 2018

@author: caleb
"""
import csv
import pandas as pd
from pgmpy.models import BayesianModel
from pgmpy.estimators import MaximumLikelihoodEstimator
from calendar import monthrange
from pgmpy.inference import VariableElimination


"""
OPEN FILES, IMPORT AND CLEAN DATA

"""
data = {}
nydata = {}
index_to_field = {}
nyindex_to_field = {}
fields = []
nyfields = []
with open('data.csv', newline='') as csvfile:
    reader = csv.reader(csvfile, delimiter=',', quotechar='|')
    for j, row in enumerate(reader):
        if j == 0:
            for i, elt in enumerate(row):
                print('i:' + str(i))
                if i >= 2 and i <= 6:
                    index_to_field[i] = elt
                    data[elt] = []
                    fields.append(elt)
        else:
            for i, elt in enumerate(row):
                if i >= 2 and i <= 6:
                    #print('i: ' + str(i))
                    if elt == '':
                        data[index_to_field[i]].append(None)
                    else:
                        data[index_to_field[i]].append(elt)

with open('nydata.csv', newline='') as csvfile:
    reader = csv.reader(csvfile, delimiter=',', quotechar='|')
    for j, row in enumerate(reader):
        if j == 0:
            for i, elt in enumerate(row):
                print('i:' + str(i))
                if i >= 2 and i <= 6:
                    nyindex_to_field[i] = elt
                    nydata[elt] = []
                    nyfields.append(elt)
        else:
            for i, elt in enumerate(row):
                if i >= 2 and i <= 6:
                    #print('i: ' + str(i))
                    if elt == '':
                        nydata[nyindex_to_field[i]].append(None)
                    else:
                        nydata[nyindex_to_field[i]].append(elt)
data['GTMP'] = []
nydata['GTMP'] = []
with open('globaltemp.csv', newline='') as csvfile:
    reader = csv.reader(csvfile, delimiter=',', quotechar='|')
    for j, row in enumerate(reader):
        year = int(row[0][0:4])
        month = int(row[0][4:6])
        days = monthrange(year, month)[1]
        for i in range(days):
            data['GTMP'].append(row[1])
            nydata['GTMP'].append(row[1])

assert (len(data['GTMP']) == len(data['WTHR']))
assert (len(data['WTHR']) == len(data['TMIN']))
assert (len(data['TMIN']) == len(data['TMAX']))
assert (len(data['TMAX']) == len(data['PRCP']))
assert (len(data['PRCP']) == len(data['AWND']))
print(data.keys())

def clean(data):
    length = len(data['GTMP'])
    
    for i in range(length):
        label_prcp, prcp = None, data['PRCP'][i]
        label_tmax, tmax = None, data['TMAX'][i]
        label_tmin, tmin = None, data['TMIN'][i]
        label_awnd, awnd = None, data['AWND'][i]
        label_gtmp, gtmp = None, data['GTMP'][i]
        
        # PRCP
        if prcp == None:
            label_prcp = 0
        elif float(prcp) <= 0.1:
            label_prcp = 0
        elif float(prcp) <= 0.3:
            label_prcp = 1
        else:
            label_prcp = 2
        data['PRCP'][i] = label_prcp
        
        # TMAX
        if tmax == None:
            label_tmax = 0
        elif int(tmax) <= 40:
            label_tmax = 0
        elif int(tmax) <= 70:
            label_tmax = 1
        else:
            label_tmax = 2
        data['TMAX'][i] = label_tmax
        
        # TMIN
        if tmin == None:
            label_tmin = 0
        elif int(tmin) <= 40:
            label_tmin = 0
        elif int(tmin) <= 70:
            label_tmin = 1
        else:
            label_tmin = 2
        data['TMIN'][i] = label_tmin
        
        # AWND
        if awnd == None:
            label_awnd = 0
        elif float(awnd) <= 8:
            label_awnd = 0
        elif float(awnd) <= 16:
            label_awnd = 1
        else:
            label_awnd = 2
        data['AWND'][i] = label_awnd
    
        # GTMP
        if gtmp == None:
            label_gtmp = None
        elif float(gtmp) <= 0.0:
            label_gtmp = 0
        elif float(gtmp) <= 0.1:
            label_gtmp = 1
        elif float(gtmp) <= 0.2:
            label_gtmp = 2
        elif float(gtmp) <= 0.3:
            label_gtmp = 3
        elif float(gtmp) <= 0.4:
            label_gtmp = 4
        elif float(gtmp) <= 0.5:
            label_gtmp = 5
        elif float(gtmp) <= 0.6:
            label_gtmp = 6
        elif float(gtmp) <= 0.7:
            label_gtmp = 7
        elif float(gtmp) <= 0.8:
            label_gtmp = 8
        elif float(gtmp) <= 0.9:
            label_gtmp = 9
        else:
            label_gtmp = 10
        data['GTMP'][i] = label_gtmp

# CLEAN

clean(data)
clean(nydata)

pandata = pd.DataFrame(data=data)
npandata = pd.DataFrame(data=nydata)
ny_test_pandata = npandata[:1000]

# Learn the model from the Boston data
G = BayesianModel()
G.add_nodes_from(['GTMP','PRCP','TMAX','TMIN', 'AWND',  'WTHR'])
G.add_edges_from([('GTMP', 'TMAX'),('GTMP', 'TMIN'),('TMAX', 'PRCP'),('TMIN','PRCP'),('TMAX', 'AWND'),('TMIN','AWND'),('AWND', 'WTHR'),('PRCP','WTHR')])
G.fit(pandata)
assert(G.check_model())

# Perform inference on Boston data
inference = VariableElimination(G)
for i in range(11):
    phi_query = inference.query(variables=['WTHR'],evidence={'GTMP':i})
    print(phi_query['WTHR'])
    print(" given global temperature of " + str(i))
# Test the model on the New York data
ny_test_pandata = ny_test_pandata.copy()
ny_test_pandata.drop('WTHR', axis=1,inplace=True)
ny_pred = G.predict(ny_test_pandata)
print('total number of severe weather incidences: ')
print(ny_pred.sum(axis=0))

# NOW REMOVE GLOBAL TEMPERATURE
data.pop('GTMP')
nydata.pop('GTMP')

pandata = pd.DataFrame(data=data)
npandata = pd.DataFrame(data=nydata)
ny_test_pandata = npandata[:1000]

# Learn the model from the Boston data
G = BayesianModel()
G.add_nodes_from(['PRCP','TMAX','TMIN', 'AWND',  'WTHR'])
G.add_edges_from([('TMAX', 'PRCP'),('TMIN','PRCP'),('TMAX', 'AWND'),('TMIN','AWND'),('AWND', 'WTHR'),('PRCP','WTHR')])
G.fit(pandata)
assert(G.check_model())

# Test the model on the New York data
ny_test_pandata = ny_test_pandata.copy()
ny_test_pandata.drop('WTHR', axis=1,inplace=True)
ny_pred = G.predict(ny_test_pandata)
print('total number of severe weather incidences: ')
print(ny_pred.sum(axis=0))