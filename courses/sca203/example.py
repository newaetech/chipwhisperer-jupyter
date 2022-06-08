# do capture for TVLA

#... setup, get scope, target
from tqmd import trange
import chipwhisperer as cw
scope = cw.scope()
target = cw.target(scope)
scope.default_setup()

# capture traces...
N = 50000 #total traces = 2*n

from cwtvla.ktp import FixedVRandomText, verify_AES
import numpy as np
key_len = 16
ktp = FixedVRandomText(key_len)

group1 = np.zeros((N, scope.adc.samples), dtype='float64')
group2 = np.zeros((N, scope.adc.samples), dtype='float64')
for i in trange(N):
    key, text = ktp.next_group_A()

    trace = cw.capture_trace(scope, target, text, key)
    while trace is None:
        trace = cw.capture_trace(scope, target, text, key)

    if not verify_AES(text, key, trace.textout):
        raise ValueError("Encryption failed")
    group1[i,:] = trace.wave[:]

    key, text = ktp.next_group_B() 
    trace = cw.capture_trace(scope, target, text, key)
    while trace is None:
        trace = cw.capture_trace(scope, target, text, key)

    group2[i,:] = trace.wave[:]
    if not verify_AES(text, key, trace.textout):
        raise ValueError("Encryption failed")

# do analysis
from cwtvla.analysis import t_test, check_t_test
t_val = t_test(group1, group2)
fp = check_t_test(t_val)

if len(fp) > 0:
    print("Failed T Test @ {}".format(fp))
else:
    print("Passed T Test")

import matplotlib.pyplot as plt 
plt.figure()
plt.plot(t_val[0])
plt.plot(t_val[1])
plt.show()

# do rand_v_rand
## setup scope,target
N = 100000

import numpy as np
ktp = FixedVRandomText(key_len)
waves = np.zeros((N, scope.adc.samples), dtype='float64')
textins = np.zeros((N, 16), dtype='uint8')

for i in trange(N):
    key, text = ktp.next_group_B()
    trace = cw.capture_trace(scope, target, text, key)
    while trace is None:
        trace = cw.capture_trace(scope, target, text, key)

    if not verify_AES(text, key, trace.textout):
        raise ValueError("Encryption failed")
    #project.traces.append(trace)
    waves[i, :] = trace.wave
    textins[i, :] = np.array(text)

## test rand_v_rand
from cwtvla.analysis import eval_rand_v_rand, roundinout_hd

eval_rand_v_rand(waves, textins, roundinout_hd, round_range=range(2,3), \
 byte_range=range(0, 2), bit_range=range(0, 2), plot=True)