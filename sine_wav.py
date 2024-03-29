#!/usr/bin/env python3

import numpy as np
import math
from scipy.io import wavfile

sinelut=np.array([2137, 1731, 1543, 1419, 1326, 1252, 1190, 1137, 1091, 1050, 1013, 979, 949, 920, 894, 869, 846, 825, 804, 785, 767, 749, 732, 717, 701, 687, 672, 659, 646, 633, 621, 609, 598, 587, 576, 566, 556, 546, 536, 527, 518, 509, 501, 492, 484, 476, 468, 461, 453, 446, 439, 432, 425, 418, 411, 405, 399, 392, 386, 380, 375, 369, 363, 358, 352, 347, 341, 336, 331, 326, 321, 316, 311, 307, 302, 297, 293, 289, 284, 280, 276, 271, 267, 263, 259, 255, 251, 248, 244, 240, 236, 233, 229, 226, 222, 219, 215, 212, 209, 205, 202, 199, 196, 193, 190, 187, 184, 181, 178, 175, 172, 169, 167, 164, 161, 159, 156, 153, 151, 148, 146, 143, 141, 138, 136, 134, 131, 129, 127, 125, 122, 120, 118, 116, 114, 112, 110, 108, 106, 104, 102, 100, 98, 96, 94, 92, 91, 89, 87, 85, 83, 82, 80, 78, 77, 75, 74, 72, 70, 69, 67, 66, 64, 63, 62, 60, 59, 57, 56, 55, 53, 52, 51, 49, 48, 47, 46, 45, 43, 42, 41, 40, 39, 38, 37, 36, 35, 34, 33, 32, 31, 30, 29, 28, 27, 26, 25, 24, 23, 23, 22, 21, 20, 20, 19, 18, 17, 17, 16, 15, 15, 14, 13, 13, 12, 12, 11, 10, 10, 9, 9, 8, 8, 7, 7, 7, 6, 6, 5, 5, 5, 4, 4, 4, 3, 3, 3, 2, 2, 2, 2, 1, 1, 1, 1, 1, 1, 1, 0, 0, 0, 0, 0, 0, 0, 0])
explut=np.array([0, 3, 6, 8, 11, 14, 17, 20, 22, 25, 28, 31, 34, 37, 40, 42, 45, 48, 51, 54, 57, 60, 63, 66, 69, 72, 75, 78, 81, 84, 87, 90, 93, 96, 99, 102, 105, 108, 111, 114, 117, 120, 123, 126, 130, 133, 136, 139, 142, 145, 148, 152, 155, 158, 161, 164, 168, 171, 174, 177, 181, 184, 187, 190, 194, 197, 200, 204, 207, 210, 214, 217, 220, 224, 227, 231, 234, 237, 241, 244, 248, 251, 255, 258, 262, 265, 268, 272, 276, 279, 283, 286, 290, 293, 297, 300, 304, 308, 311, 315, 318, 322, 326, 329, 333, 337, 340, 344, 348, 352, 355, 359, 363, 367, 370, 374, 378, 382, 385, 389, 393, 397, 401, 405, 409, 412, 416, 420, 424, 428, 432, 436, 440, 444, 448, 452, 456, 460, 464, 468, 472, 476, 480, 484, 488, 492, 496, 501, 505, 509, 513, 517, 521, 526, 530, 534, 538, 542, 547, 551, 555, 560, 564, 568, 572, 577, 581, 585, 590, 594, 599, 603, 607, 612, 616, 621, 625, 630, 634, 639, 643, 648, 652, 657, 661, 666, 670, 675, 680, 684, 689, 693, 698, 703, 708, 712, 717, 722, 726, 731, 736, 741, 745, 750, 755, 760, 765, 770, 774, 779, 784, 789, 794, 799, 804, 809, 814, 819, 824, 829, 834, 839, 844, 849, 854, 859, 864, 869, 874, 880, 885, 890, 895, 900, 906, 911, 916, 921, 927, 932, 937, 942, 948, 953, 959, 964, 969, 975, 980, 986, 991, 996, 1002, 1007, 1013, 1018])

sampleRate = 44100
frequency = 440
phase = -0.14 # to make this match up with the np.sin() based sine wave we are using for testing.
phase_d = 0.0
length = 5
tableLength = 256
tau = 2 * np.pi

class EnvelopeGenerator:
    a = 0.0
    d = 0.0
    s = 0.0
    r = 0.0
    amp = 0.0
    note_on = 0.0
    note_off = 0.0
    state = 'o'

    def __init__(self):
        self.a = 0.1
        self.d = 0.1
        self.s = 0.5
        self.r = 0.1
        self.amp = 0.0
        self.note_on = 0.0
        self.note_off = 0.0
        self.state = 'o' # o=off, a=attack, d=decay, s=sustain, r=release 

    def sAmp(self, time):
        global explut
        
        amp = explut[255]
        l = time - self.note_on
        if l <= 0:
            return 2048
        if l > 0:
            if l < self.a:                                                      # We are in the attack phase
                factor = (l/self.a)
                index = int(factor * 256)
                index = min(255, index)
                amp = explut[~index]

            if l > self.a and l < (self.a + self.d):                            # We are in the decay phase
                factor = (l - self.a) / self.d
                low = int(self.s * 256)
                diff = (255 - low)

                index = int(factor * diff)
                index = min(255, index) 
                amp = explut[index]

            if l > (self.a+self.d):                                            # We are in the sustain phase
                index = int(self.s * 256)
                amp = explut[~index]

            if time > self.note_off and time < (self.note_off + self.r):            # Note has been released, so we are in the release phase
                factor = (time - self.note_off) / self.r
                high = int(self.s * 256)
                index = int((1.0-factor) * high)
                index = abs(min(255,index))
                amp = explut[~index]
            
            if time >= self.note_off + self.r:
                amp = 2048

        return amp

class Operator:

    def __init__(self):
        self.f = 440.0
        self.phase = 0.0
        self.phase_d = 0
        self.env = EnvelopeGenerator()
        self.sv = np.vectorize(self.sineValues)

    def setf(self, f):
        global sampleRate
        global tau
        self.f = f
        self.phase_d = (tau * f) / sampleRate

    def incrementPhase(self):
        global tau
        self.phase = (self.phase + self.phase_d) % tau
    
    def expValue(self, sinval):
        global explut
        return (explut[255-(sinval&0xFF)]+1024) >> (sinval>>8)
 

    def sineValues(self, samples):
        global sinelut
        global tableLength
        global tau
        global sampleRate

        # return np.sin(tau * frequency * samples) # uncomment this to make a math based sine.
        self.incrementPhase()

        sineIndex = self.phase * tableLength / tau
        sineIndex = int(sineIndex * 4) % tableLength
        
        amp = self.env.sAmp(samples)
        amp = int(amp)

        if self.phase < np.pi / 2:
            sinval = sinelut[sineIndex] + amp 
            output = self.expValue(sinval)
        elif self.phase < np.pi :
            sinval = sinelut[~sineIndex] + amp
            output = self.expValue(sinval)
        elif self.phase < 3 * np.pi / 2 :
            sinval = sinelut[sineIndex] + amp
            output = -self.expValue(sinval)
        elif phase < tau:
            sinval = sinelut[~sineIndex] + amp
            output = -self.expValue(sinval)
        output = output/2048
        output = output
        return output

op1 = Operator()
op1.setf(440.0)
op1.env.a = 1.5
op1.env.d = 0.5
op1.env.s = 0.75
op1.env.r = 0.5
op1.env.note_on = 0.25
op1.env.note_off = 4.0

samples = np.linspace(0, length, sampleRate * length)  #  Produces a 5 second Audio-File
y = op1.sv(samples)

wavfile.write('TableSine.wav', sampleRate, y)
