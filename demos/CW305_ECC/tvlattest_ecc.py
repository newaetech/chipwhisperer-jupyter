#!/usr/bin/python
# -*- coding: utf-8 -*-
#
# Copyright (c) 2019-2021, NewAE Technology Inc
# All rights reserved.
#
# Find this and more at newae.com - this file is part of the chipwhisperer
# project, http://www.assembla.com/spaces/chipwhisperer
#
#    This file is part of chipwhisperer.
#
#    chipwhisperer is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    chipwhisperer is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Lesser General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with chipwhisperer.  If not, see <http://www.gnu.org/licenses/>.
#=================================================
import random
from ecpy.curves import Curve, Point

class TVLATTest_ECC(object):
    """Class for getting key and text for TVLA T-Tests.

    Basic usage::

        import chipwhisperer as cw
        import tvlattest_ecc as TVLA
        ktp = TVLA.TVLATTest_ECC(curve)
        ktp.init(num_traces, groups ) # init with the number of traces you plan to
                                      # capture and the list of groups to use
        k, P, group = ktp.next()

    """
    _name = "TVLA Rand vs Fixed"
    _description = "Welsh T-Test with random/fixed plaintext."

    def __init__(self, curve):
        """Args:
            curve (ecpy.curves.Curve): Curve used.
        """
        self._fixed_P = None
        self._fixed_k = None
        self.curve = curve
        self.tries = 100 # number of tries to generate a new random point on curve or k value before giving up


    def init(self, traces, groups):
        """Initialize key text pattern for a specific number of traces.

        Args:
            traces (int): Number of traces to initialize for.
            groups (list of ints): Groups to use.

        """
        self._fixed_P = Point(0x6B17D1F2_E12C4247_F8BCE6E5_63A440F2_77037D81_2DEB33A0_F4A13945_D898C296, 
                              0x4FE342E2_FE1A7F9B_8EE7EB4A_7C0F9E16_2BCE3357_6B315ECE_CBB64068_37BF51F5, 
                              self.curve)
        self._fixed_k = 0x8CAFF271_6695A595_E76B8D97_F69F9E92_F96AB92E_7D598F3D_C525B33A_71898139

        self.groups = groups
        self.num_groups = len(groups)
        per_group = int(traces/len(groups))
        last_group = traces - per_group*(len(groups)-1)
        self.group_count_left = [per_group] * (len(groups)-1)
        self.group_count_left.append(last_group)


    def new_point(self, bits=256):
        for i in range(self.tries):
            x = random.getrandbits(bits)
            y = self.curve.y_recover(x)
            if x > 0 and y:
                P = Point(x, y, self.curve, check=True)
                # shouldn't be necessary but let's check anwyway:
                assert self.curve.is_on_curve(P)
                return P
        raise ValueError("Failed to generate a random point after %d tries!" % self.tries)


    def new_k(self, bits=256):
        for i in range(self.tries):
            k = random.getrandbits(bits)
            if k < self.curve.order and k > 0:
                return k
        raise ValueError("Failed to generate a valid random k after %d tries!" % self.tries)

    def special_k(self, bits=256):
        """ returns a k with MSB set
        """
        for i in range(self.tries):
            k = random.getrandbits(bits)
            k |= 2**(bits-1)
            if k < self.curve.order and k > 0:
                return k
        raise ValueError("Failed to generate a valid random k after %d tries!" % self.tries)



    def attackable_k(self):
        """ Returns a valid random k with k[255:254] = 01, 10 or 11.
        Arbitrary k's could be attacked but present a special case.
        """
        for i in range(self.tries):
            k = random.getrandbits(256)
            if k < self.curve.order and k > 0 and len(hex(k)) == 66 and (k >> 254) > 0:
                return k
        raise ValueError("Failed to generate a valid random k after %d tries!" % self.tries)


    def new_k_hw(self, min_weight, max_weight, check=True):
        """ Returns valid random k with Hamming weight randomly chosen between min_weight and max_weight (inclusive)
        """
        hw = random.randint(min_weight, max_weight)
        for i in range(self.tries):
            k = 0
            bits_turned_on = []
            for j in range(hw):
                bit = random.randint(0,255)
                while bit in bits_turned_on:
                    bit = random.randint(0,255)
                bits_turned_on.append(bit)
                k += 2**bit
            if k < self.curve.order:
                if check:
                    p = lambda n:n and 1+p(n&(n-1))
                    assert hw == p(k)
                return k
        raise ValueError("Failed to generate a valid random k after %d tries!" % self.tries)


    def new_pair(self):
        rand = random.random()
        num_tot = sum(self.group_count_left)
        interval = float(1/self.num_groups)
        if num_tot == 0:
            for group_index in range(self.num_groups):
                if rand < interval*(group_index+1):
                    group = self.groups[group_index]
                    break
        else:
            for group_index in range(self.num_groups):
                cutoff = float(sum(self.group_count_left[0:group_index+1]) / num_tot)
                if rand < cutoff:
                    group = self.groups[group_index]
                    break

        # Fixed k and P:
        if group == 0:
            k = self._fixed_k
            P = self._fixed_P

        # Fixed k, random P:
        elif group == 1:
            k = self._fixed_k
            P = self.new_point()

        # Random k, fixed P:
        elif group == 2:
            k = self.new_k(256)
            P = self._fixed_P

        # Random k < 2**10, fixed P:
        elif group == 3:
            k = self.new_k(10)
            P = self._fixed_P

        # Random k with Hamming weight <= 26, fixed P:
        elif group == 4:
            k = self.new_k_hw(1, 26)
            P = self._fixed_P

        # Random k with Hamming weight >= 230, fixed P:
        elif group == 5:
            k = self.new_k_hw(230, 255)
            P = self._fixed_P

        # Fixed k, random P with x coordinate < 1024:
        elif group == 6:
            k = self._fixed_k
            P = self.new_point(bits=10)

        # Random k < 2**40, fixed P:
        elif group == 7:
            k = self.new_k(40)
            P = self._fixed_P

        # Random k with Hamming weight between 26 and 52, fixed P:
        elif group == 8:
            k = self.new_k_hw(26, 52)
            P = self._fixed_P

        # Random k with 'punctured' zeros:
        elif group == 9:
            k = self.new_k(256)
            # puncture bit 32 80% of the time:
            if random.random() > 0.2:
                k = k & ~2**32
            # puncture bit 64 95% of the time:
            if random.random() > 0.05:
                k = k & ~2**64
            # puncture bits 128-129 80% of the time:
            if random.random() > 0.2:
                k = k & ~2**128
                k = k & ~2**129
            # puncture bits 160-163 80% of the time:
            if random.random() > 0.2:
                k = k & ~2**160
                k = k & ~2**161
                k = k & ~2**162
                k = k & ~2**163
            P = self._fixed_P

        # Random k with longer strings of 'punctured' zeros:
        elif group == 10:
            P = self._fixed_P
            k = self.new_k(256)
            # puncture bit 32-39 80% of the time:
            if random.random() > 0.2:
                for i in range(32,40):
                    k = k & ~2**i
            # puncture bits 64-79 95% of the time:
            if random.random() > 0.05:
                for i in range(64,80):
                    k = k & ~2**i
            # puncture bits 96-127 80% of the time:
            if random.random() > 0.2:
                for i in range(96,128):
                    k = k & ~2**i

        # Random k with more distinct strings of 'punctured' zeros:
        elif group == 11:
            P = self._fixed_P
            k = self.new_k(256)
            # puncture bit 16-31 95% of the time:
            if random.random() > 0.05:
                for i in range(16,32):
                    k = k & ~2**i
            # puncture bits 120-135 95% of the time:
            if random.random() > 0.05:
                for i in range(120,136):
                    k = k & ~2**i
            # puncture bits 208-239 95% of the time:
            if random.random() > 0.05:
                for i in range(208,240):
                    k = k & ~2**i

        # Random k with more distinct strings of filled-in ones (opposite of group 11):
        elif group == 12:
            P = self._fixed_P
            k = self.new_k(256)
            # puncture bit 16-31 95% of the time:
            if random.random() > 0.05:
                for i in range(16,32):
                    k = k | 2**i
            # puncture bits 120-135 95% of the time:
            if random.random() > 0.05:
                for i in range(120,136):
                    k = k | 2**i
            # puncture bits 208-239 95% of the time:
            if random.random() > 0.05:
                for i in range(208,240):
                    k = k | 2**i

        # Random k with short strings of 'punctured' zeros:
        elif group == 13:
            P = self._fixed_P
            k = self.new_k(256)
            # puncture bits 32-33, always:
            for i in range(32,34):
                k = k & ~2**i
            # puncture bits 128-130, always:
            for i in range(128,131):
                k = k & ~2**i
            # puncture bits 224-227, always:
            for i in range(224,228):
                k = k & ~2**i

        # Random k with different short strings of 'punctured' zeros:
        elif group == 14:
            P = self._fixed_P
            k = self.new_k(256)
            # puncture bits 160-161, always:
            for i in range(160,162):
                k = k & ~2**i
            # puncture bits 200-203, always:
            for i in range(200,204):
                k = k & ~2**i
            # puncture bits 224-225, always:
            for i in range(224,226):
                k = k & ~2**i
            # puncture bits 240-243, always:
            for i in range(240,244):
                k = k & ~2**i

        # Random k with fixed leading 1:
        elif group == 15:
            P = self._fixed_P
            k = self.special_k(256)



        else:
            raise ValueError("No defined behaviour for group %d" % group)

        if self.group_count_left[group_index] > 0:
            self.group_count_left[group_index] -= 1

        return k, P, group


    def next(self):
        """Returns the next k and P pair

        Returns:
            k (int)
            P (ecpy.curves.Point)
            group (int): 0 = constant k, constant P
                         1 = constant k, varying P
                         2 = varying k, constant P
                         3 = varying k in [1,1024], constant P
                         4 = varying k with HW in [1,26], constant P
                         5 = varying k with HW in [230, 255], constant P

        """
        return self.new_pair()


