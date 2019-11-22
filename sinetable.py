#!/usr/bin/env python3
"""Sine Table Generator"""
import numpy as np

statement = "self.sine = ["
inc = (2*np.pi) / 256

for x in range(256):
    print(inc * x)
    if x < 255:
        statement += str(round(np.sin(x*inc),6))+','
    else:
        statement += str(round(np.sin(x*inc),6))+']'
print(statement)
print("")

