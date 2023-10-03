#!/usr/bin/env python
# coding: utf-8

# # OpenNeuro Dataset Query by NIDM-Terms Example

# In[1]:


import ipywidgets as widgets
import json
import os
from os import system
from os.path import join,basename
import pandas as pd
from IPython.display import display
try:
    from cognitiveatlas.api import get_concept, get_disorder
except ImportError:
    system('python -m pip install cognitiveatlas')
    from cognitiveatlas.api import get_concept, get_disorder
try:
    import glob2
except ImportError:
    system('python -m pip install glob2')
    import glob2
import requests


# In[2]:


# set up uber jsonld dictionary
data={}
# for all jsonld documents in this repo, load them into a graph
for dataset in glob2.glob("../../terms/OpenNeuro_BIDS_terms/OpenNeuro_jsonld/**"):
    #print(basename(dataset))
    # set top-level data key to datset number
    data[basename(dataset)] = {}
    # loop through all jsonld files and get isAbouts
    for jsonldfile in glob2.glob(join(dataset,"**","*.jsonld")):
        #load jsonld file
        #if basename(dataset) == '000001':
        #print("Loading jsonld file: %s for dataset: %s" %(jsonldfile,basename(dataset)))
        with open(jsonldfile) as f:
            # load jsonld document and set key for each variable to source_variable
            tmp = json.load(f)
            for var,properties in tmp.items(): 
                #print(properties)
                data[basename(dataset)][properties['sourceVariable']] = properties

    


# In[3]:


# find all isAbout concepts in data dictionary
isAbout_term_labels={}
for key,val in data.items():
    for subkey,subval in data[key].items():
        for variable,jsonld_elements in data[key][subkey].items():
            #print("variable=%s" %variable)
            #print("json_elements=%s" %jsonld_elements)
            if (variable == "isAbout"):
                # isAbout concepts stored as dictionary if single item or 
                # list of dictionaries if multiple items
                if isinstance(jsonld_elements,dict):
                    #print(jsonld_elements)
                    if (jsonld_elements['@id'] not in isAbout_term_labels.keys()) and (jsonld_elements['label'] != ""):
                        isAbout_term_labels[jsonld_elements['@id']] = jsonld_elements['label']
                        
                # here we have multiple isAbouts
                elif isinstance(jsonld_elements,list):
                    for elements in jsonld_elements:
                        #print(elements)
                        if (elements['@id'] not in isAbout_term_labels.keys()) and (elements['label'] != "") :
                            isAbout_term_labels[elements['@id']] = elements['label']
                    
                     


# In[ ]:


def doIsAboutQuery(queryTerms):
    matching_datasets={}
    # print("Running query on datasets for terms: %s" %queryTerms)
    for term in queryTerms:
        # run query by looking for url matching queryTerms in isAbout_terms_labels
        # which has mapping between isAbout URL and it's label
        for isabout_key, isabout_value in isAbout_term_labels.items():
            #print("isabout_value=%s" %isabout_value)
            # check if isAbout_terms_labels value is the term we're looking for
            if isabout_value == term:
                #print("found match")
                matching_datasets[term] = []
                # sometimes we have more than 1 isAbout URL so loop through them looking
                # for a match wtih our query term URL
                for dataset,dataset_variables in data.items():
                    for source_variables,dataset_annotations in dataset_variables.items():
                        #print(dataset_annotations)
                        for key,value in dataset_annotations.items():
                            #print("looking for isAbout match %s" %(str(isabout_key)))
                            #print("value: %s" %str(value))
                            if (str(key)=='isAbout') and (str(isabout_key) in str(value)):
                                #print("found match")
                                # if dataset isn't already in the matching_datasets list then append
                                dataset_url = "https://openneuro.org/datasets/ds" + dataset
                                if dataset_url not in matching_datasets[term]:
                                    matching_datasets[term].append("https://openneuro.org/datasets/ds" + dataset)
                           
    return matching_datasets


def doSourceVariableQuery(queryTerms):
    matching_datasets = {}
    # print("Running query on datasets for terms: %s" %queryTerms)
    for term in queryTerms:
        matching_datasets[term] = []
        # run query by looking for url matching queryTerms in isAbout_terms_labels
        # which has mapping between isAbout URL and it's label
        for dataset, dataset_variables in data.items():
            for source_variables, dataset_annotations in dataset_variables.items():
                # print(dataset_annotations)
                for key, value in dataset_annotations.items():
                    if (str(key) == 'sourceVariable') and (str(term) in str(value)):
                        # print("found match")
                        # if dataset isn't already in the matching_datasets list then append
                        dataset_url = "https://openneuro.org/datasets/ds" + dataset
                        if dataset_url not in matching_datasets[term]:
                            matching_datasets[term].append("https://openneuro.org/datasets/ds" + dataset)

    return matching_datasets

# for each isAbout term, query number of datasets with this concept annotation and 
# save in dictionary of isAbout term x number of datasets
isAbout_dataset_counts={}
for isabout_key, isabout_value in isAbout_term_labels.items():
    datasets = doIsAboutQuery([isabout_value])
    isAbout_dataset_counts[isabout_value] = len(datasets[isabout_value])

# output counts
isAbout_dataframe = pd.DataFrame(list(isAbout_dataset_counts.items()), columns=['Concept', 'Dateset Counts'])
isAbout_dataframe.to_csv("isAbout_concept_overlap_openneuro_datasets.csv")

variables_dataset_counts={}
for dataset, dataset_variables in data.items():
    for variable, var_struct in dataset_variables.items():
        datasets = doSourceVariableQuery([variable])
        variables_dataset_counts[variable] = len(datasets[variable])

# output counts
variables_dataframe = pd.DataFrame(list(variables_dataset_counts.items()), columns=['SourceVariable', 'Dateset Counts'])
variables_dataframe.to_csv("dataset_sourcevariables_overlap_openneuro_datasets.csv")




