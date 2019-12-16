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
        # self.op2 = Operator(1, op2[0], op2[1], op2[2], op2[3], op2[4], op1[5])
        # self.op3 = Operator(0, op3[0], op3[1], op3[2], op3[3], op3[4], op3[5])
        # self.op4 = Operator(1, op4[0], op4[1], op4[2], op4[3], op4[4], op1[5])
        self.note_on = 0.0
        self.note_off = 0.0
        self.z = np.vectorize(self.sampleAt)

    def __init__(self):
        self.op1 = Operator()
        self.op2 = Operator()
        # self.op3 = Operator()
        # self.op4 = Operator()
        self.op1.index = 0
        self.op2.index = 1
        # self.op3.index = 2
        # self.op4.index = 3
        self.note_on = 0.0
        self.note_off = 0.0
        self.z = np.vectorize(self.sampleAt)

    def envLength(self):
        #return self.op1.a + self.op1.d + 0.25 + self.op1.r
        return max(self.op1.a, self.op2.a) + max(self.op1.d, self.op2.d) + 0.25 + max(self.op1.r, self.op2.r)
        # return max(self.op1.a,self.op2.a,self.op3.a,self.op4.a) + max(self.op1.d,self.op2.d,self.op3.a,self.op4.a) + 0.25 + max(self.op1.r,self.op2.r,self.op3.r,self.op4.r)

    def sampleAt(self, t):
        # s = self.op1.sOsc(t, self.note_on, self.note_off)
        s = self.op1.sOscFM(t, self.note_on, self.note_off, self.op2.sOsc(t, self.note_on, self.note_off), self.op2.k)
        # s += self.op3.sOscFM(t, self.note_on, self.note_off, self.op4.sOsc(t, self.note_on, self.note_off), self.op4.k)

        if t > self.note_off + self.op1.r + 0.25:
            self.reset()
        return s

    def reset(self):
        self.op1.randomize()
        self.op2.randomize()
        # self.op3.randomize()
        # self.op4.randomize()
        new = self.envLength()
        self.note_on = self.note_on + new
        self.note_off = self.note_on + new
        self.dump()

    def dump(self):
        self.op1.dump()
        self.op2.dump()
        # self.op3.dump()
        # self.op4.dump()
        print("RATIO:", round(self.op2.f/self.op1.f, 2))
        # print("RATIOS:",round(self.op2.f/self.op1.f, 2),round(self.op4.f/self.op3.f, 2))
        print("")

class Operator:
    q1 = np.pi / 2      # half of pi
    q2 = np.pi          # pi
    q3 = np.pi * 1.5    # 1.5 * pi
    q4 = 2 * np.pi      # tau

    tableLength = 256
    sinelut=np.array([2137, 1731, 1543, 1419, 1326, 1252, 1190, 1137, 1091, 1050, 1013, 979, 949, 920, 894, 869, 846, 825, 804, 785, 767, 749, 732, 717, 701, 687, 672, 659, 646, 633, 621, 609, 598, 587, 576, 566, 556, 546, 536, 527, 518, 509, 501, 492, 484, 476, 468, 461, 453, 446, 439, 432, 425, 418, 411, 405, 399, 392, 386, 380, 375, 369, 363, 358, 352, 347, 341, 336, 331, 326, 321, 316, 311, 307, 302, 297, 293, 289, 284, 280, 276, 271, 267, 263, 259, 255, 251, 248, 244, 240, 236, 233, 229, 226, 222, 219, 215, 212, 209, 205, 202, 199, 196, 193, 190, 187, 184, 181, 178, 175, 172, 169, 167, 164, 161, 159, 156, 153, 151, 148, 146, 143, 141, 138, 136, 134, 131, 129, 127, 125, 122, 120, 118, 116, 114, 112, 110, 108, 106, 104, 102, 100, 98, 96, 94, 92, 91, 89, 87, 85, 83, 82, 80, 78, 77, 75, 74, 72, 70, 69, 67, 66, 64, 63, 62, 60, 59, 57, 56, 55, 53, 52, 51, 49, 48, 47, 46, 45, 43, 42, 41, 40, 39, 38, 37, 36, 35, 34, 33, 32, 31, 30, 29, 28, 27, 26, 25, 24, 23, 23, 22, 21, 20, 20, 19, 18, 17, 17, 16, 15, 15, 14, 13, 13, 12, 12, 11, 10, 10, 9, 9, 8, 8, 7, 7, 7, 6, 6, 5, 5, 5, 4, 4, 4, 3, 3, 3, 2, 2, 2, 2, 1, 1, 1, 1, 1, 1, 1, 0, 0, 0, 0, 0, 0, 0, 0])
    explut=np.array([0, 3, 6, 8, 11, 14, 17, 20, 22, 25, 28, 31, 34, 37, 40, 42, 45, 48, 51, 54, 57, 60, 63, 66, 69, 72, 75, 78, 81, 84, 87, 90, 93, 96, 99, 102, 105, 108, 111, 114, 117, 120, 123, 126, 130, 133, 136, 139, 142, 145, 148, 152, 155, 158, 161, 164, 168, 171, 174, 177, 181, 184, 187, 190, 194, 197, 200, 204, 207, 210, 214, 217, 220, 224, 227, 231, 234, 237, 241, 244, 248, 251, 255, 258, 262, 265, 268, 272, 276, 279, 283, 286, 290, 293, 297, 300, 304, 308, 311, 315, 318, 322, 326, 329, 333, 337, 340, 344, 348, 352, 355, 359, 363, 367, 370, 374, 378, 382, 385, 389, 393, 397, 401, 405, 409, 412, 416, 420, 424, 428, 432, 436, 440, 444, 448, 452, 456, 460, 464, 468, 472, 476, 480, 484, 488, 492, 496, 501, 505, 509, 513, 517, 521, 526, 530, 534, 538, 542, 547, 551, 555, 560, 564, 568, 572, 577, 581, 585, 590, 594, 599, 603, 607, 612, 616, 621, 625, 630, 634, 639, 643, 648, 652, 657, 661, 666, 670, 675, 680, 684, 689, 693, 698, 703, 708, 712, 717, 722, 726, 731, 736, 741, 745, 750, 755, 760, 765, 770, 774, 779, 784, 789, 794, 799, 804, 809, 814, 819, 824, 829, 834, 839, 844, 849, 854, 859, 864, 869, 874, 880, 885, 890, 895, 900, 906, 911, 916, 921, 927, 932, 937, 942, 948, 953, 959, 964, 969, 975, 980, 986, 991, 996, 1002, 1007, 1013, 1018])
    def __init__(self, i, f, a, d, s, r, k):
        self.index = i              # Index of the current operator
        self.f = f                  # frequency that the operator is running at 
        self.a = a                  # attack time (in seconds)
        self.d = d                  # decay time (in seconds)
        self.s = s                  # sustain level (0.0 - 1.0)
        self.r = r                  # release time (in seconds)
        self.k = k                  # level / fm index

    def __init__(self):
        self.index = 1
        self.f = 440.00
        self.a = 0.1
        self.d = 0.1
        self.s = 1.00
        self.r = 0.1
        self.k = 1.00

    def sineIndex(self, t):
        phase =  (self.q4 * self.f * t)  % self.q4
        i = phase * self.tableLength / self.q4
        i = int(i * 4) % self.tableLength
        output = 0.0
        if phase < self.q1:
            sinval = self.sinelut[i]
            output = (self.explut[255-(sinval&0xFF)]+1024) >> (sinval>>8)
        elif phase < self.q2:
            sinval = self.sinelut[~i]
            output = (self.explut[255-(sinval&0xFF)]+1024) >> (sinval>>8)
        elif phase < self.q3:
            sinval = self.sinelut[i]
            output = -((self.explut[255-(sinval&0xFF)]+1024) >> (sinval>>8))
        elif phase < self.q4:
            sinval = self.sinelut[~i]
            output = -((self.explut[(255-sinval&0xFF)]+1024) >> (sinval>>8))
        output=output/2048
        return output

    def sOscFM(self, t, note_on, note_off, msamp=0.0, mk=0.0):
        # out = exp(logsin(phase2 + exp(logsin(phase1) + gain1)) + gain2)
        unmod = self.sineIndex(t)
        index = self.q4 * self.sineIndex(unmod) + (mk * msamp)
        index = int(index) % self.tableLength
        return self.sAmp(t, note_on, note_off) * self.sineIndex(index)
    
    def sOsc(self, t, note_on, note_off):
        return self.sAmp(t, note_on, note_off) * self.sineIndex(t)

    def sAmp(self, time):
        amp = 0.0
        l = time - self.note_on

        if note_on > self.note_off:
            if l < self.a:                                                  # We are in the attack phase
                amp = (l/self.a)                                            # Raise the amplitude to 1 over the course of the attack time
            
            if l > self.a and l < (self.a + self.d):                        # We are in the decay phase
                amp = ((l - self.a) / self.d) * (self.s - 1) + 1            # Reduce the amplitude to the sustain amplitude over the course of the decay time 

            if l > (self.a+self.d):                                         # We are in the sustain phase
                amp = self.d                                                # Maintain the sustain amplitude until the note is released

        else:                                                               # Note has been released, so we are in the release phase
            amp = ((time-self.note_off) / self.r) * (0.0 - self.s) + self.s      # Reduce the amplitude to 0 over the course of the release time

        if amp < 0.0001:
            amp = 0.0                                                       # Amplitude should not be negative and should not be extremely small
        return amp

    def randomize(self):
        self.f = round(0.01 + random.random() * 440, 2)
        self.a = round(0.1 + random.random() * 2, 2)
        self.d = round(0.01 + random.random() * 2, 2)
        self.s = round(0.01 + random.random(), 2)
        self.r = round(0.1 + random.random() * 2, 2)
        self.k = round(0.01 + random.random() * 12, 2)

    def dump(self):
        print("OP"+str(self.index)+":","F:"+str(self.f).rjust(7), "  K:"+str(self.k).rjust(8), '  ADSR:['+str(self.a).rjust(4), str(self.d).rjust(4), str(self.s).rjust(4), str(self.r).rjust(4)+']')

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
