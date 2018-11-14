from pandas import DataFrame as pdf
import numpy as n
from flask import Flask,render_template, g, request, redirect, url_for
from datetime import datetime as dt
from pymongo import *