from pandas import DataFrame as pdf
import numpy as n
from flask import Flask,render_template, g, request, redirect, url_for
from datetime import datetime as dt,timedelta
from pymongo import MongoClient as mcx
from collections import OrderedDict as odict
from copy import copy,deepcopy

def jroads():
	doc=odict()
	doc['connexion']='localhost:27017'
	doc['dbase']='jroad'
	return doc
