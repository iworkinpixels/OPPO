#!/usr/bin/env python3
"""Sine Table Generator"""
import numpy as np

tl = 256 # table length
sd = 256 # sine wave depth
tau = 2 * np.pi

f=1

sine = []
exp = [] 
out = []

for x in range(tl):
    value = int(round(-np.log(np.sin((x+0.5)*np.pi/tl/2))/np.log(2)*sd))
    sine.append(value)

for x in range(tl):
    value = round((pow(2, x/256)-1)*1024)
    exp.append(value)

print('sine=', sine)
print('exp=', exp)

# Now prove that we can reconstruct a quarter sine wave.
#for sinpos in range(0,len(sine)):
    # output = (exp[255-(sinval&0xFF)]+1024) >> (sinval>>8)
    # output = output / 2048
    # out.append(output)

# print(out)
