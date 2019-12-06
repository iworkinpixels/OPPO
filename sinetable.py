#!/usr/bin/env python3
"""Sine Table Generator"""
import numpy as np
import math
import struct

tl = 256 # table length
sd = 256 # sine wave depth
tau = 2 * np.pi

f=1

def dump_output(sinpos, sinval, exppos, expval, significand, exponent,outstr):
    print('SPOS:',"{:03d}".format(sinpos))                                  # sine table position
    print('SVAL:',"{:04d}".format(sinval),format(sinval,'016b'))            # sine table value
    print('EPOS:',"{:04d}".format(exppos),format(exppos,'08b'))             # exp table position
    print('EVAL:',"{:04d}".format(expval),format(expval,'016b'))            # exp table value
    print('SIGV:',"{:04d}".format(significand),format(significand,'010b'))  # significand value
    print('EXPV:',"{:04d}".format(exponent),format(exponent,'03b'))         # exponent value
    print('ACTL:',math.exp(-sinval))                                        # The actual value we want (calculated using math.exp(-sinval))
    print('EXPT:',outstr)                                                   # A string representing the binary we are currently outputting. Hoping to use it to see what I'm doing wrong.
    print('')


def twos_complement(value, bitWidth=4):
    if value >= 2**bitWidth:
        # This catches when someone tries to give a value that is out of range
        raise ValueError("Value: {} out of range of {}-bit value.".format(value, bitWidth))
    else:
        output = ~value
        print("INP:", format(value,'08b'))
        print("DEC:", value)
        print("OUT:", format(output,'08b'))
        print("DEC:", output)
        print('')
        return output

sine = []
exp = [] 
out = []


for x in range(tl):
    value = int(round(-np.log(np.sin((x+0.5)*np.pi/tl/2))/np.log(2)*sd))
    sine.append(value)

for x in range(tl):
    value = int(round((pow(2, x/tl)-1)*1024))
    exp.append(value)

print('\n-LOGSIN:')
print('IDX DEC  BINARY')
for x in range(0,len(sine)):
    print("{:03d}".format(x), "{:04d}".format(sine[x]), format(sine[x],'016b'))
print('\nEXP:')
print('IDX DEC  BINARY')
for x in range(0,len(exp)):
    print("{:03d}".format(x), "{:04d}".format(exp[x]), format(exp[x],'016b'))

print("")

# Now prove that we can reconstruct a quarter sine wave.
for sinpos in range(0,len(sine)):
    sinval = sine[sinpos]
    exppos = sinval & 0xFF # read the table at the position defined by the 8 LSB of the input
    expval = exp[exppos]
    significand = 1024 + expval
    exponent = math.floor(expval%256)
    output = (significand / pow(2,exponent))/1024
    outstr = format(significand,'010b')+' '+format(exponent,'03b')
    dump_output(sinpos, sinval, exppos, expval, significand, exponent, outstr)
    out.append(output)
    print('OUTP:',output)
    print('\n')

print(out)
