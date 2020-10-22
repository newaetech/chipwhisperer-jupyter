import chipwhisperer as cw
import time
import zarr
import numpy as np
from cwtvla.ktp import FixedVRandomText, FixedVRandomKey, SemiFixedVRandomText, verify_AES
import cwtvla.analysis as analysis
import matplotlib.pyplot as plt
from tqdm import trange

def setup_device(name):
    scope = cw.scope()
    if name == "CW305":
        scope.gain.db = 25
        scope.adc.samples = 129
        scope.adc.offset = 0
        scope.adc.basic_mode = "rising_edge"
        scope.clock.clkgen_freq = 7370000
        scope.clock.adc_src = "extclk_x4"
        scope.trigger.triggers = "tio4"
        scope.io.tio1 = "serial_rx"
        scope.io.tio2 = "serial_tx"
        scope.io.hs2 = "disabled"
        target = cw.target(scope, cw.targets.CW305, bsfile="cw305_top.bit", force=False)
        target.vccint_set(1.0)
        # we only need PLL1:
        target.pll.pll_enable_set(True)
        target.pll.pll_outenable_set(False, 0)
        target.pll.pll_outenable_set(True, 1)
        target.pll.pll_outenable_set(False, 2)

        # run at 10 MHz:
        target.pll.pll_outfreq_set(10E6, 1)

        # 1ms is plenty of idling time
        target.clkusbautooff = True
        target.clksleeptime = 1
    else:
        target = cw.target(scope)
        scope.default_setup()
        scope.adc.samples = 24400
    if name == "XMEGA":
        cw.program_target(scope, cw.programmers.XMEGAProgrammer, "AES-xmega.hex")
    elif name == "STM32F3":
        cw.program_target(scope, cw.programmers.STM32FProgrammer, "AES.hex")
    elif name == "STM32F3-mbed":
        cw.program_target(scope, cw.programmers.STM32FProgrammer, "AES-mbed.hex")
    elif name == "K82F":
        scope.adc.samples=3500
    elif name == "STM32F4":
        cw.program_target(scope, cw.programmers.STM32FProgrammer, "AES-f4.hex")
        scope.adc.samples=5000

    return scope,target

def random_v_random_capture(platform, key_len=16, N=10000):
    #may not be working
    scope,target = setup_device(platform)
    ktp = FixedVRandomText(key_len)
    store = zarr.DirectoryStore('data/{}-{}-{}.zarr'.format(platform,N,key_len))
    root = zarr.group(store=store, overwrite=True)

    zwaves = root.zeros('traces/waves', shape=(2*N, scope.adc.samples), chunks=(2500, None), dtype='float64')
    ztextins = root.zeros('traces/textins', shape=(2*N, 16), chunks=(2500, None), dtype='uint8')

    waves = zwaves[:,:]
    textins = ztextins[:,:]
    
    for i in trange(2*N):
        key, text = ktp.next_group_B()
        trace = cw.capture_trace(scope, target, text, key)
        while trace is None:
            trace = cw.capture_trace(scope, target, text, key)

        if not verify_AES(text, key, trace.textout):
            raise ValueError("Encryption failed")
        #project.traces.append(trace)
        waves[i, :] = trace.wave
        textins[i, :] = np.array(text)
    zwaves[:,:] = waves[:,:]
    ztextins[:,:] = textins[:,:]
    print("Last encryption took {} samples".format(scope.adc.trig_count))



def do_invariant_test(ktp_class, platform, N=10000, key_len=16):
    # may not be working
    scope, target = setup_device(platform)
    #scope.adc.offset = 20000
    ktp = ktp_class(key_len)
    #ktp = FixedVRandomKey(key_len)
    #store = zarr.DirectoryStore('SFvR/{}-{}-{}-{}.zarr'.format(platform, ktp._name, N, key_len))
    #root = zarr.group(store=store, overwrite=True)
    root = zarr.group("")
    zgroup1 = root.zeros('traces/group1', shape=(N, scope.adc.samples), chunks=(2500, None), dtype='float64')
    zgroup2 = root.zeros('traces/group2', shape=(N, scope.adc.samples), chunks=(2500, None), dtype='float64')

    group1 = zgroup1[:,:]
    group2 = zgroup2[:,:]
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

    
if __name__ == "__main__":
    from guppy import hpy
    hp = hpy()
    hp.setrelheap()
    z = zarr.open("SFvR/STM32F4-SemiFixedVRandomText-5000-16.zarr")
    print(z.tree())
    group1 = z.traces.group1[:,:]
    group2 = z.traces.group2[:,:]
    print(hp.heap())
    t = analysis.t_test(group1, group2)
    import matplotlib.pyplot as plt
    plt.figure()
    plt.plot(t[0])
    plt.plot(t[1])
    plt.show()
    #func = analysis.roundinout_hd
    #analysis.eval_rand_v_rand(waves, textins, func, round_range=range(2,3), plot=True)