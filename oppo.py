#!/usr/bin/env python3
"""FM Synth"""
import argparse
import sys
import random 

import numpy as np
import sounddevice as sd
import time as pytime 

class Voice:
    def __init__(self, op1, op2):
        self.op1 = Operator(0, op1[0], op1[1], op1[2], op1[3], op1[4], op1[5])
        self.op2 = Operator(1, op2[0], op2[1], op2[2], op2[3], op2[4], op1[5])
        self.op3 = Operator(0, op3[0], op3[1], op3[2], op3[3], op3[4], op3[5])
        self.op4 = Operator(1, op4[0], op4[1], op4[2], op4[3], op4[4], op1[5])
        self.note_on = 0.0
        self.note_off = 0.0
        self.z = np.vectorize(self.sampleAt)

    def __init__(self):
        self.op1 = Operator()
        self.op2 = Operator()
        self.op3 = Operator()
        self.op4 = Operator()
        self.op1.index = 0
        self.op2.index = 1
        self.op3.index = 2
        self.op4.index = 3
        self.note_on = 0.0
        self.note_off = 0.0
        self.z = np.vectorize(self.sampleAt)

    def envLength(self):
        return max(self.op1.a,self.op2.a,self.op3.a,self.op4.a) + max(self.op1.d,self.op2.d,self.op3.a,self.op4.a) + 0.25 + max(self.op1.r,self.op2.r,self.op3.r,self.op4.r)

    def sampleAt(self, t):
        s = self.op1.sOscFM(t, self.note_on, self.note_off, self.op2.sOsc(t, self.note_on, self.note_off), self.op2.k)
        s += self.op3.sOscFM(t, self.note_on, self.note_off, self.op4.sOsc(t, self.note_on, self.note_off), self.op4.k)

        if t > self.note_off + max(self.op1.r,self.op3.r) + 0.25:
            self.reset()
        return s

    def reset(self):
        self.op1.randomize()
        self.op2.randomize()
        self.op3.randomize()
        self.op4.randomize()
        self.op1.dump()
        self.op2.dump()
        self.op3.dump()
        self.op4.dump()
        new = self.envLength()
        self.note_on = self.note_on + new
        self.note_off = self.note_on + new
        print("RATIOS:",round(self.op2.f/self.op1.f, 2),round(self.op4.f/self.op3.f, 2))
        print("")

class Operator:
    sine = [0.0,0.024541,0.049068,0.073565,0.098017,0.122411,0.14673,0.170962,0.19509,0.219101,0.24298,0.266713,0.290285,0.313682,0.33689,0.359895,0.382683,0.405241,0.427555,0.449611,0.471397,0.492898,0.514103,0.534998,0.55557,0.575808,0.595699,0.615232,0.634393,0.653173,0.671559,0.689541,0.707107,0.724247,0.740951,0.757209,0.77301,0.788346,0.803208,0.817585,0.83147,0.844854,0.857729,0.870087,0.881921,0.893224,0.903989,0.91421,0.92388,0.932993,0.941544,0.949528,0.95694,0.963776,0.970031,0.975702,0.980785,0.985278,0.989177,0.99248,0.995185,0.99729,0.998795,0.999699,1.0,0.999699,0.998795,0.99729,0.995185,0.99248,0.989177,0.985278,0.980785,0.975702,0.970031,0.963776,0.95694,0.949528,0.941544,0.932993,0.92388,0.91421,0.903989,0.893224,0.881921,0.870087,0.857729,0.844854,0.83147,0.817585,0.803208,0.788346,0.77301,0.757209,0.740951,0.724247,0.707107,0.689541,0.671559,0.653173,0.634393,0.615232,0.595699,0.575808,0.55557,0.534998,0.514103,0.492898,0.471397,0.449611,0.427555,0.405241,0.382683,0.359895,0.33689,0.313682,0.290285,0.266713,0.24298,0.219101,0.19509,0.170962,0.14673,0.122411,0.098017,0.073565,0.049068,0.024541,0.0,-0.024541,-0.049068,-0.073565,-0.098017,-0.122411,-0.14673,-0.170962,-0.19509,-0.219101,-0.24298,-0.266713,-0.290285,-0.313682,-0.33689,-0.359895,-0.382683,-0.405241,-0.427555,-0.449611,-0.471397,-0.492898,-0.514103,-0.534998,-0.55557,-0.575808,-0.595699,-0.615232,-0.634393,-0.653173,-0.671559,-0.689541,-0.707107,-0.724247,-0.740951,-0.757209,-0.77301,-0.788346,-0.803208,-0.817585,-0.83147,-0.844854,-0.857729,-0.870087,-0.881921,-0.893224,-0.903989,-0.91421,-0.92388,-0.932993,-0.941544,-0.949528,-0.95694,-0.963776,-0.970031,-0.975702,-0.980785,-0.985278,-0.989177,-0.99248,-0.995185,-0.99729,-0.998795,-0.999699,-1.0,-0.999699,-0.998795,-0.99729,-0.995185,-0.99248,-0.989177,-0.985278,-0.980785,-0.975702,-0.970031,-0.963776,-0.95694,-0.949528,-0.941544,-0.932993,-0.92388,-0.91421,-0.903989,-0.893224,-0.881921,-0.870087,-0.857729,-0.844854,-0.83147,-0.817585,-0.803208,-0.788346,-0.77301,-0.757209,-0.740951,-0.724247,-0.707107,-0.689541,-0.671559,-0.653173,-0.634393,-0.615232,-0.595699,-0.575808,-0.55557,-0.534998,-0.514103,-0.492898,-0.471397,-0.449611,-0.427555,-0.405241,-0.382683,-0.359895,-0.33689,-0.313682,-0.290285,-0.266713,-0.24298,-0.219101,-0.19509,-0.170962,-0.14673,-0.122411,-0.098017,-0.073565,-0.049068,-0.024541]
    def __init__(self, i, f, a, d, s, r, k):
        self.index = i                          # Index of the current operator
        self.f = f                              # frequency that the operator is running at 
        self.a = a                              # attack time (in seconds)
        self.d = d                              # decay time (in seconds)
        self.s = s                              # sustain level (0.0 - 1.0)
        self.r = r                              # release time (in seconds)
        self.k = k                              # level / fm index

    def __init__(self):
        self.index = 1
        self.f = 440.00
        self.a = 0.01
        self.d = 0.01
        self.s = 1.00
        self.r = 0.01
        self.k = 1.00

    def sineIndex(self, t):
        return int(round(256 * (((self.f * 2 * np.pi * t) % (2 * np.pi)) / (2 * np.pi)))) - 1

    def sOscFM(self, t, note_on, note_off, msamp, mk):
        # print(t,self.sineIndex(t))
        index = (2 * np.pi) * self.sine[self.sineIndex(t)] + (mk * msamp)
        index = int(index) % 256
        return self.sAmp(t, note_on, note_off) * self.sine[index]
    
    def sOsc(self, t, note_on, note_off):
        return self.sAmp(t, note_on, note_off) * self.sine[self.sineIndex(t)]

    def sAmp(self, time, note_on, note_off):
        amp = 0.0
        l = time - note_on

        if note_on > note_off:
            if l < self.a:                                                  # We are in the attack phase
                amp = (l/self.a)                                            # Raise the amplitude to 1 over the course of the attack time
            
            if l > self.a and l < (self.a + self.d):                        # We are in the decay phase
                amp = ((l - self.a) / self.d) * (self.s - 1) + 1            # Reduce the amplitude to the sustain amplitude over the course of the decay time 

            if l > (self.a+self.d):                                         # We are in the sustain phase
                amp = self.d                                                # Maintain the sustain amplitude until the note is released

        else:                                                               # Note has been released, so we are in the release phase
            amp = ((time-note_off) / self.r) * (0.0 - self.s) + self.s      # Reduce the amplitude to 0 over the course of the release time

        if amp < 0.0001:
            amp = 0.0                                                       # Amplitude should not be negative and should not be extremely small
        return amp

    def randomize(self):
        self.f = round(0.01 + random.random() * 440, 2)
        self.a = round(0.01 + random.random() * 2, 2)
        self.d = round(0.01 + random.random() * 2, 2)
        self.s = round(0.01 + random.random(), 2)
        self.r = round(0.01 + random.random() * 2, 2)
        self.k = round(0.01 + random.random() * 2000, 2)

    def dump(self):
        print("OP"+str(self.index)+":","F:"+str(self.f).rjust(7), "  K:"+str(self.k).rjust(6), '  ADSR:['+str(self.a).rjust(4), str(self.d).rjust(4), str(self.s).rjust(4), str(self.r).rjust(4)+']')

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

voice1 = Voice()
voice2 = Voice()

start_idx = 0
try:
    samplerate = sd.query_devices(args.device, 'output')['default_samplerate']

    def callback(outdata, frames, time, status):
        if status:
            print(status, file=sys.stderr)
        global start_idx

        t = (start_idx + np.arange(frames)) / samplerate
        t = t.reshape(-1, 1)
        
        outdata[:] = args.amplitude * voice1.z(t) 
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
