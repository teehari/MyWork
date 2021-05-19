# -*- coding: utf-8 -*-
"""
Created on Tue Jun  2 23:03:11 2020

@author: Hari
"""

from celery import Celery

app = Celery('asyncProc', broker='amqp://guest:guest@localhost//')

@app.task
def add(x, y):
    return x + y



