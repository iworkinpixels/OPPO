#!/usr/bin/env python3
"""FM Synth"""
import argparse
import sys
import random 

import numpy as np
import sounddevice as sd
import time as pytime 

class Operator:
    def __init__(self, i, f, a, d, s, r, k):
        self.index = i                          # Index of the current operator
        self.f = f                              # frequency that the operator is running at 
        self.a = a                              # attack time (in seconds)
        self.d = d                              # decay time (in seconds)
        self.s = s                              # sustain level (0.0 - 1.0)
        self.r = r                              # release time (in seconds)
        self.k = k                              # level / fm index
        self.note_on = 0.0                      # time the note off was received
        self.note_off = 0.0                     # time the note off was received 
        self.amp = np.vectorize(self.sAmp)


    def sOsc(self, t):
            return self.amp(t) * np.sin(2 * np.pi * self.f * t)

    def noteOn(self, t):
        self.note_on = t

    def noteOff(self, t):
        self.note_off = t
   
    def sAmp(self, time):
        amp = 0.0
        l = time - self.note_on

        if self.note_on > self.note_off:
            if l < self.a:                                                  # We are in the attack phase
                amp = (l/self.a)                                            # Raise the amplitude to 1 over the course of the attack time
            
            if l > self.a and l < (self.a + self.d):                        # We are in the decay phase
                amp = ((l - self.a) / self.d) * (self.s - 1) + 1            # Reduce the amplitude to the sustain amplitude over the course of the decay time 

            if l > (self.a+self.d):                                         # We are in the sustain phase
                amp = self.d                                                # Maintain the sustain amplitude until the note is released

        else:                                                               # Note has been released, so we are in the release phase
            amp = ((time-self.note_off) / self.r) * (0.0 - self.s) + self.s  # Reduce the amplitude to 0 over the course of the release time
            if self.index == 0 and time > self.note_off + self.r + 0.25:           # Only do this for Operator 1, which is the carrier
                reset()

        if amp < 0.0001:
            amp = 0.0                                                       # Amplitude should not be negative and should not be extremely small
        return amp

def int_or_str(text):
    """Helper function for argument parsing."""
    try:
        return int(text)
    except ValueError:
        return text


parser = argparse.ArgumentParser(add_help=False)
parser.add_argument(
    '-l', '--list-devices', action='store_true',
    help='show list of audio devices and exit')
args, remaining = parser.parse_known_args()
if args.list_devices:
    print(sd.query_devices())
    parser.exit(0)
parser = argparse.ArgumentParser(
    description=__doc__,
    formatter_class=argparse.RawDescriptionHelpFormatter,
    parents=[parser])
parser.add_argument(
    '-d', '--device', type=int_or_str,
    help='output device (numeric ID or substring)')
parser.add_argument(
    '-a', '--amplitude', type=float, default=0.2,
    help='amplitude (default: %(default)s)')
args = parser.parse_args(remaining)

def reset():
    op1.note_on += op1.a + op1.d + op1.r + 0.5
    op2.note_on += op1.a + op1.d + op1.r + 0.5
    op1.note_off = op1.note_on + op1.a + op1.d + 0.25
    op2.note_off = op2.note_on + op2.a + op2.d + 0.25

f1 = 440 * random.random()
f2 = 440 * random.random()
k1 = 50 * random.random()
k2 = 50 * random.random()

a1 = random.random()
d1 = random.random()
s1 = random.random()
r1 = random.random()

a2 = random.random()
d2 = random.random()
s2 = random.random()
r2 = random.random()

op1 = Operator(0, f1, a1, d1, s1, r1, k1)
op2 = Operator(1, f2, a2, d2, s2, r2, k2)
reset()

print("RATIO: ",op2.f/op1.f)
print("OP1: ",op1.f,op1.a,op1.d,op1.s,op1.r,op1.k)
print("OP2: ",op2.f,op2.a,op2.d,op2.s,op2.r,op2.k)
print("")


start_idx = 0
try:
    samplerate = sd.query_devices(args.device, 'output')['default_samplerate']

    def callback(outdata, frames, time, status):
        if status:
            print(status, file=sys.stderr)
        global start_idx

        t = (start_idx + np.arange(frames)) / samplerate
        t = t.reshape(-1, 1)
        
        outdata[:] = args.amplitude * (np.cos(op1.sOsc(t) + op2.k * op2.sOsc(t)))
        start_idx += frames

    with sd.OutputStream(device=args.device, channels=1, callback=callback,
                         samplerate=samplerate, latency=0.050):
        print('#' * 80)
        print('press Return to quit')
        print('#' * 80)
        input()
except KeyboardInterrupt:
    parser.exit('')
except Exception as e:
    parser.exit(type(e).__name__ + ': ' + str(e))
