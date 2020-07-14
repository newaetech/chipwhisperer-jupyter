import os, random
import sys
import numpy as np
#include <unistd.h>
#include "1_1-1_0.h"

sbox = (
#0 1 2 3 4 5 6 7 8 9 A B C D E F
0x63, 0x7c, 0x77, 0x7b, 0xf2, 0x6b, 0x6f, 0xc5, 0x30, 0x01, 0x67, 0x2b, 0xfe, 0xd7, 0xab, 0x76, #0
0xca, 0x82, 0xc9, 0x7d, 0xfa, 0x59, 0x47, 0xf0, 0xad, 0xd4, 0xa2, 0xaf, 0x9c, 0xa4, 0x72, 0xc0, #1
0xb7, 0xfd, 0x93, 0x26, 0x36, 0x3f, 0xf7, 0xcc, 0x34, 0xa5, 0xe5, 0xf1, 0x71, 0xd8, 0x31, 0x15, #2
0x04, 0xc7, 0x23, 0xc3, 0x18, 0x96, 0x05, 0x9a, 0x07, 0x12, 0x80, 0xe2, 0xeb, 0x27, 0xb2, 0x75, #3
0x09, 0x83, 0x2c, 0x1a, 0x1b, 0x6e, 0x5a, 0xa0, 0x52, 0x3b, 0xd6, 0xb3, 0x29, 0xe3, 0x2f, 0x84, #4
0x53, 0xd1, 0x00, 0xed, 0x20, 0xfc, 0xb1, 0x5b, 0x6a, 0xcb, 0xbe, 0x39, 0x4a, 0x4c, 0x58, 0xcf, #5
0xd0, 0xef, 0xaa, 0xfb, 0x43, 0x4d, 0x33, 0x85, 0x45, 0xf9, 0x02, 0x7f, 0x50, 0x3c, 0x9f, 0xa8, #6
0x51, 0xa3, 0x40, 0x8f, 0x92, 0x9d, 0x38, 0xf5, 0xbc, 0xb6, 0xda, 0x21, 0x10, 0xff, 0xf3, 0xd2, #7
0xcd, 0x0c, 0x13, 0xec, 0x5f, 0x97, 0x44, 0x17, 0xc4, 0xa7, 0x7e, 0x3d, 0x64, 0x5d, 0x19, 0x73, #8
0x60, 0x81, 0x4f, 0xdc, 0x22, 0x2a, 0x90, 0x88, 0x46, 0xee, 0xb8, 0x14, 0xde, 0x5e, 0x0b, 0xdb, #9
0xe0, 0x32, 0x3a, 0x0a, 0x49, 0x06, 0x24, 0x5c, 0xc2, 0xd3, 0xac, 0x62, 0x91, 0x95, 0xe4, 0x79, #A
0xe7, 0xc8, 0x37, 0x6d, 0x8d, 0xd5, 0x4e, 0xa9, 0x6c, 0x56, 0xf4, 0xea, 0x65, 0x7a, 0xae, 0x08, #B
0xba, 0x78, 0x25, 0x2e, 0x1c, 0xa6, 0xb4, 0xc6, 0xe8, 0xdd, 0x74, 0x1f, 0x4b, 0xbd, 0x8b, 0x8a, #C
0x70, 0x3e, 0xb5, 0x66, 0x48, 0x03, 0xf6, 0x0e, 0x61, 0x35, 0x57, 0xb9, 0x86, 0xc1, 0x1d, 0x9e, #D
0xe1, 0xf8, 0x98, 0x11, 0x69, 0xd9, 0x8e, 0x94, 0x9b, 0x1e, 0x87, 0xe9, 0xce, 0x55, 0x28, 0xdf, #E
0x8c, 0xa1, 0x89, 0x0d, 0xbf, 0xe6, 0x42, 0x68, 0x41, 0x99, 0x2d, 0x0f, 0xb0, 0x54, 0xbb, 0x16
)

rsbox = (
0x52, 0x09, 0x6a, 0xd5, 0x30, 0x36, 0xa5, 0x38, 0xbf, 0x40, 0xa3, 0x9e, 0x81, 0xf3, 0xd7, 0xfb,
0x7c, 0xe3, 0x39, 0x82, 0x9b, 0x2f, 0xff, 0x87, 0x34, 0x8e, 0x43, 0x44, 0xc4, 0xde, 0xe9, 0xcb,
0x54, 0x7b, 0x94, 0x32, 0xa6, 0xc2, 0x23, 0x3d, 0xee, 0x4c, 0x95, 0x0b, 0x42, 0xfa, 0xc3, 0x4e,
0x08, 0x2e, 0xa1, 0x66, 0x28, 0xd9, 0x24, 0xb2, 0x76, 0x5b, 0xa2, 0x49, 0x6d, 0x8b, 0xd1, 0x25,
0x72, 0xf8, 0xf6, 0x64, 0x86, 0x68, 0x98, 0x16, 0xd4, 0xa4, 0x5c, 0xcc, 0x5d, 0x65, 0xb6, 0x92,
0x6c, 0x70, 0x48, 0x50, 0xfd, 0xed, 0xb9, 0xda, 0x5e, 0x15, 0x46, 0x57, 0xa7, 0x8d, 0x9d, 0x84,
0x90, 0xd8, 0xab, 0x00, 0x8c, 0xbc, 0xd3, 0x0a, 0xf7, 0xe4, 0x58, 0x05, 0xb8, 0xb3, 0x45, 0x06,
0xd0, 0x2c, 0x1e, 0x8f, 0xca, 0x3f, 0x0f, 0x02, 0xc1, 0xaf, 0xbd, 0x03, 0x01, 0x13, 0x8a, 0x6b,
0x3a, 0x91, 0x11, 0x41, 0x4f, 0x67, 0xdc, 0xea, 0x97, 0xf2, 0xcf, 0xce, 0xf0, 0xb4, 0xe6, 0x73,
0x96, 0xac, 0x74, 0x22, 0xe7, 0xad, 0x35, 0x85, 0xe2, 0xf9, 0x37, 0xe8, 0x1c, 0x75, 0xdf, 0x6e,
0x47, 0xf1, 0x1a, 0x71, 0x1d, 0x29, 0xc5, 0x89, 0x6f, 0xb7, 0x62, 0x0e, 0xaa, 0x18, 0xbe, 0x1b,
0xfc, 0x56, 0x3e, 0x4b, 0xc6, 0xd2, 0x79, 0x20, 0x9a, 0xdb, 0xc0, 0xfe, 0x78, 0xcd, 0x5a, 0xf4,
0x1f, 0xdd, 0xa8, 0x33, 0x88, 0x07, 0xc7, 0x31, 0xb1, 0x12, 0x10, 0x59, 0x27, 0x80, 0xec, 0x5f,
0x60, 0x51, 0x7f, 0xa9, 0x19, 0xb5, 0x4a, 0x0d, 0x2d, 0xe5, 0x7a, 0x9f, 0x93, 0xc9, 0x9c, 0xef,
0xa0, 0xe0, 0x3b, 0x4d, 0xae, 0x2a, 0xf5, 0xb0, 0xc8, 0xeb, 0xbb, 0x3c, 0x83, 0x53, 0x99, 0x61,
0x17, 0x2b, 0x04, 0x7e, 0xba, 0x77, 0xd6, 0x26, 0xe1, 0x69, 0x14, 0x63, 0x55, 0x21, 0x0c, 0x7d
)

# Rcon = (
#0x8d, 0x01, 0x02, 0x04, 0x08, 0x10, 0x20, 0x40, 0x80, 0x1b, 0x36, 0x6c, 0xd8, 0xab, 0x4d, 0x9a,
#0x2f, 0x5e, 0xbc, 0x63, 0xc6, 0x97, 0x35, 0x6a, 0xd4, 0xb3, 0x7d, 0xfa, 0xef, 0xc5, 0x91, 0x39,
#0x72, 0xe4, 0xd3, 0xbd, 0x61, 0xc2, 0x9f, 0x25, 0x4a, 0x94, 0x33, 0x66, 0xcc, 0x83, 0x1d, 0x3a,
#0x74, 0xe8, 0xcb, 0x8d, 0x01, 0x02, 0x04, 0x08, 0x10, 0x20, 0x40, 0x80, 0x1b, 0x36, 0x6c, 0xd8,
#0xab, 0x4d, 0x9a, 0x2f, 0x5e, 0xbc, 0x63, 0xc6, 0x97, 0x35, 0x6a, 0xd4, 0xb3, 0x7d, 0xfa, 0xef,
#0xc5, 0x91, 0x39, 0x72, 0xe4, 0xd3, 0xbd, 0x61, 0xc2, 0x9f, 0x25, 0x4a, 0x94, 0x33, 0x66, 0xcc,
#0x83, 0x1d, 0x3a, 0x74, 0xe8, 0xcb, 0x8d, 0x01, 0x02, 0x04, 0x08, 0x10, 0x20, 0x40, 0x80, 0x1b,
#0x36, 0x6c, 0xd8, 0xab, 0x4d, 0x9a, 0x2f, 0x5e, 0xbc, 0x63, 0xc6, 0x97, 0x35, 0x6a, 0xd4, 0xb3,
#0x7d, 0xfa, 0xef, 0xc5, 0x91, 0x39, 0x72, 0xe4, 0xd3, 0xbd, 0x61, 0xc2, 0x9f, 0x25, 0x4a, 0x94,
#0x33, 0x66, 0xcc, 0x83, 0x1d, 0x3a, 0x74, 0xe8, 0xcb, 0x8d, 0x01, 0x02, 0x04, 0x08, 0x10, 0x20,
#0x40, 0x80, 0x1b, 0x36, 0x6c, 0xd8, 0xab, 0x4d, 0x9a, 0x2f, 0x5e, 0xbc, 0x63, 0xc6, 0x97, 0x35,
#0x6a, 0xd4, 0xb3, 0x7d, 0xfa, 0xef, 0xc5, 0x91, 0x39, 0x72, 0xe4, 0xd3, 0xbd, 0x61, 0xc2, 0x9f,
#0x25, 0x4a, 0x94, 0x33, 0x66, 0xcc, 0x83, 0x1d, 0x3a, 0x74, 0xe8, 0xcb, 0x8d, 0x01, 0x02, 0x04,
#0x08, 0x10, 0x20, 0x40, 0x80, 0x1b, 0x36, 0x6c, 0xd8, 0xab, 0x4d, 0x9a, 0x2f, 0x5e, 0xbc, 0x63,
#0xc6, 0x97, 0x35, 0x6a, 0xd4, 0xb3, 0x7d, 0xfa, 0xef, 0xc5, 0x91, 0x39, 0x72, 0xe4, 0xd3, 0xbd,
#0x61, 0xc2, 0x9f, 0x25, 0x4a, 0x94, 0x33, 0x66, 0xcc, 0x83, 0x1d, 0x3a, 0x74, 0xe8, 0xcb
#)

def S(x):	return sbox[x]
def R(x):	return rsbox[x]

TableMul2_8 = np.zeros([256, 256], dtype=np.uint8)

def MakeTableMul2_8():
    aa = 0
    bb = 0
    r = 0
    t = 0
    for a in range(256 ):
        for b in range(a, 256 ):
            aa=a
            bb=b
            r=0
            while aa != 0:
                if (aa & 1) != 0: r=r^bb
                t=bb & 0x80
                bb=bb<<1
                if t != 0: bb=bb^0x1b
                aa=aa>>1
            TableMul2_8[a][b]=TableMul2_8[b][a]=r

def Multiply(a,b):	return TableMul2_8[a][b]

# char Inverse( char a)
#{
#static TableInverse = (0x00,0x01,0x8d,0xf6,0xcb,0x52,0x7b,0xd1,0xe8,0x4f,0x29,0xc0,0xb0,0xe1,0xe5,0xc7,0x74,0xb4,0xaa,0x4b,0x99,0x2b,0x60,0x5f,0x58,0x3f,0xfd,0xcc,0xff,0x40,0xee,0xb2,0x3a,0x6e,0x5a,0xf1,0x55,0x4d,0xa8,0xc9,0xc1,0x0a,0x98,0x15,0x30,0x44,0xa2,0xc2,0x2c,0x45,0x92,0x6c,0xf3,0x39,0x66,0x42,0xf2,0x35,0x20,0x6f,0x77,0xbb,0x59,0x19,0x1d,0xfe,0x37,0x67,0x2d,0x31,0xf5,0x69,0xa7,0x64,0xab,0x13,0x54,0x25,0xe9,0x09,0xed,0x5c,0x05,0xca,0x4c,0x24,0x87,0xbf,0x18,0x3e,0x22,0xf0,0x51,0xec,0x61,0x17,0x16,0x5e,0xaf,0xd3,0x49,0xa6,0x36,0x43,0xf4,0x47,0x91,0xdf,0x33,0x93,0x21,0x3b,0x79,0xb7,0x97,0x85,0x10,0xb5,0xba,0x3c,0xb6,0x70,0xd0,0x06,0xa1,0xfa,0x81,0x82,0x83,0x7e,0x7f,0x80,0x96,0x73,0xbe,0x56,0x9b,0x9e,0x95,0xd9,0xf7,0x02,0xb9,0xa4,0xde,0x6a,0x32,0x6d,0xd8,0x8a,0x84,0x72,0x2a,0x14,0x9f,0x88,0xf9,0xdc,0x89,0x9a,0xfb,0x7c,0x2e,0xc3,0x8f,0xb8,0x65,0x48,0x26,0xc8,0x12,0x4a,0xce,0xe7,0xd2,0x62,0x0c,0xe0,0x1f,0xef,0x11,0x75,0x78,0x71,0xa5,0x8e,0x76,0x3d,0xbd,0xbc,0x86,0x57,0x0b,0x28,0x2f,0xa3,0xda,0xd4,0xe4,0x0f,0xa9,0x27,0x53,0x04,0x1b,0xfc,0xac,0xe6,0x7a,0x07,0xae,0x63,0xc5,0xdb,0xe2,0xea,0x94,0x8b,0xc4,0xd5,0x9d,0xf8,0x90,0x6b,0xb1,0x0d,0xd6,0xeb,0xc6,0x0e,0xcf,0xad,0x08,0x4e,0xd7,0xe3,0x5d,0x50,0x1e,0xb3,0x5b,0x23,0x38,0x34,0x68,0x46,0x03,0x8c,0xdd,0x9c,0x7d,0xa0,0xcd,0x1a,0x41,0x1c)
#return TableInverse[a]
#}
###* Index variables
# x[0] = 1
# x[1] = K_1[0,0]
# x[2] = K_0[1,3]
# x[3] = K_0[0,0]
# x[4] = K_1[0,1]
# x[5] = K_0[0,1]
# x[6] = K_1[0,2]
# x[7] = K_0[0,2]
# x[8] = K_1[0,3]
# x[9] = K_0[0,3]
# x[10] = K_1[1,0]
# x[11] = K_0[2,3]
# x[12] = K_0[1,0]
# x[13] = K_1[1,1]
# x[14] = K_0[1,1]
# x[15] = K_1[1,2]
# x[16] = K_0[1,2]
# x[17] = K_1[1,3]
# x[18] = K_1[2,0]
# x[19] = K_0[3,3]
# x[20] = K_0[2,0]
# x[21] = K_1[2,1]
# x[22] = K_0[2,1]
# x[23] = K_1[2,2]
# x[24] = K_0[2,2]
# x[25] = K_1[2,3]
# x[26] = K_1[3,0]
# x[27] = K_0[3,0]
# x[28] = K_1[3,1]
# x[29] = K_0[3,1]
# x[30] = K_1[3,2]
# x[31] = K_0[3,2]
# x[32] = K_1[3,3]
# x[33] = X_0[3,3]
# x[34] = P[3,3]
# x[35] = X_0[3,2]
# x[36] = P[3,2]
# x[37] = X_0[3,1]
# x[38] = P[3,1]
# x[39] = X_0[3,0]
# x[40] = P[3,0]
# x[41] = X_0[2,3]
# x[42] = P[2,3]
# x[43] = X_0[2,2]
# x[44] = P[2,2]
# x[45] = X_0[2,1]
# x[46] = P[2,1]
# x[47] = X_0[2,0]
# x[48] = P[2,0]
# x[49] = X_0[1,3]
# x[50] = P[1,3]
# x[51] = X_0[1,2]
# x[52] = P[1,2]
# x[53] = X_0[1,1]
# x[54] = P[1,1]
# x[55] = X_0[1,0]
# x[56] = P[1,0]
# x[57] = X_0[0,3]
# x[58] = P[0,3]
# x[59] = X_0[0,2]
# x[60] = P[0,2]
# x[61] = X_0[0,1]
# x[62] = P[0,1]
# x[63] = X_0[0,0]
# x[64] = P[0,0]
# x[65] = W_0[3,3]
# x[66] = W_0[3,2]
# x[67] = W_0[3,1]
# x[68] = W_0[3,0]
# x[69] = W_0[2,3]
# x[70] = W_0[2,2]
# x[71] = W_0[2,1]
# x[72] = W_0[2,0]
# x[73] = W_0[1,3]
# x[74] = W_0[1,2]
# x[75] = W_0[1,1]
# x[76] = W_0[1,0]
# x[77] = W_0[0,3]
# x[78] = W_0[0,2]
# x[79] = W_0[0,1]
# x[80] = W_0[0,0]
# x[81] = K_2[0,0]
# x[82] = K_2[0,1]
# x[83] = K_2[0,2]
# x[84] = K_2[0,3]
# x[85] = K_2[1,0]
# x[86] = K_2[1,1]
# x[87] = K_2[1,2]
# x[88] = K_2[1,3]
# x[89] = K_2[2,0]
# x[90] = K_2[2,1]
# x[91] = K_2[2,2]
# x[92] = K_2[2,3]
# x[93] = K_2[3,0]
# x[94] = K_2[3,1]
# x[95] = K_2[3,2]
# x[96] = K_2[3,3]
# x[97] = X_1[3,3]
# x[98] = X_1[3,2]
# x[99] = X_1[3,1]
# x[100] = X_1[3,0]
# x[101] = X_1[2,3]
# x[102] = X_1[2,2]
# x[103] = X_1[2,1]
# x[104] = X_1[2,0]
# x[105] = X_1[1,3]
# x[106] = X_1[1,2]
# x[107] = X_1[1,1]
# x[108] = X_1[1,0]
# x[109] = X_1[0,3]
# x[110] = X_1[0,2]
# x[111] = X_1[0,1]
# x[112] = X_1[0,0]
# x[113] = W_1[3,3]
# x[114] = W_1[3,2]
# x[115] = W_1[3,1]
# x[116] = W_1[3,0]
# x[117] = W_1[2,3]
# x[118] = W_1[2,2]
# x[119] = W_1[2,1]
# x[120] = W_1[2,0]
# x[121] = W_1[1,3]
# x[122] = W_1[1,2]
# x[123] = W_1[1,1]
# x[124] = W_1[1,0]
# x[125] = W_1[0,3]
# x[126] = W_1[0,2]
# x[127] = W_1[0,1]
# x[128] = W_1[0,0]
# x[129] = X_2[3,3]
# x[130] = X_2[3,2]
# x[131] = X_2[3,1]
# x[132] = X_2[3,0]
# x[133] = X_2[2,3]
# x[134] = X_2[2,2]
# x[135] = X_2[2,1]
# x[136] = X_2[2,0]
# x[137] = X_2[1,3]
# x[138] = X_2[1,2]
# x[139] = X_2[1,1]
# x[140] = X_2[1,0]
# x[141] = X_2[0,3]
# x[142] = X_2[0,2]
# x[143] = X_2[0,1]
# x[144] = X_2[0,0]
# x[145] = X'_2[3,3]
# x[146] = X'_2[3,2]
# x[147] = X'_2[3,1]
# x[148] = X'_2[3,0]
# x[149] = X'_2[2,3]
# x[150] = X'_2[2,2]
# x[151] = X'_2[2,1]
# x[152] = X'_2[2,0]
# x[153] = X'_2[1,3]
# x[154] = X'_2[1,2]
# x[155] = X'_2[1,1]
# x[156] = X'_2[1,0]
# x[157] = X'_2[0,3]
# x[158] = X'_2[0,2]
# x[159] = X'_2[0,1]
# x[160] = X'_2[0,0]
#*/
def Attack(Known):
    x0=Known[0] # 1 
    x129=Known[1] # X_2[3,3] 
    x130=Known[2] # X_2[3,2] 
    x131=Known[3] # X_2[3,1] 
    x132=Known[4] # X_2[3,0] 
    x133=Known[5] # X_2[2,3] 
    x134=Known[6] # X_2[2,2] 
    x135=Known[7] # X_2[2,1] 
    x136=Known[8] # X_2[2,0] 
    x137=Known[9] # X_2[1,3] 
    x138=Known[10] # X_2[1,2] 
    x139=Known[11] # X_2[1,1] 
    x140=Known[12] # X_2[1,0] 
    x141=Known[13] # X_2[0,3] 
    x142=Known[14] # X_2[0,2] 
    x143=Known[15] # X_2[0,1] 
    x144=Known[16] # X_2[0,0] 
    x34=Known[17] # P[3,3] 
    x36=Known[18] # P[3,2] 
    x38=Known[19] # P[3,1] 
    x40=Known[20] # P[3,0] 
    x42=Known[21] # P[2,3] 
    x44=Known[22] # P[2,2] 
    x46=Known[23] # P[2,1] 
    x48=Known[24] # P[2,0] 
    x50=Known[25] # P[1,3] 
    x52=Known[26] # P[1,2] 
    x54=Known[27] # P[1,1] 
    x56=Known[28] # P[1,0] 
    x58=Known[29] # P[0,3] 
    x60=Known[30] # P[0,2] 
    x62=Known[31] # P[0,1] 
    x64=Known[32] # P[0,0] 
    x145=Known[33] # X'_2[3,3] 
    x146=Known[34] # X'_2[3,2] 
    x147=Known[35] # X'_2[3,1] 
    x148=Known[36] # X'_2[3,0] 
    x149=Known[37] # X'_2[2,3] 
    x150=Known[38] # X'_2[2,2] 
    x151=Known[39] # X'_2[2,1] 
    x152=Known[40] # X'_2[2,0] 
    x153=Known[41] # X'_2[1,3] 
    x154=Known[42] # X'_2[1,2] 
    x155=Known[43] # X'_2[1,1] 
    x156=Known[44] # X'_2[1,0] 
    x157=Known[45] # X'_2[0,3] 
    x158=Known[46] # X'_2[0,2] 
    x159=Known[47] # X'_2[0,1] 
    x160=Known[48] # X'_2[0,0] 
    x1=x159 ^ x158 ^ x143 ^ x142
    x47=x152 ^ x150 ^ x136 ^ x134 ^ x48
    x11=R(x156 ^ x155 ^ x140 ^ x139)
    x8=R(x147 ^ x131)
    x2=R(x160 ^ x158 ^ x144 ^ x142 ^ x1 ^ x0)
    x9=R(x148 ^ x132 ^ S(x8))
    x63=x64 ^ x1 ^ x0 ^ S(x2)
    x100=R(x145 ^ x131 ^ x129)
    x108=R(x153 ^ x2)
    x112=R(x158 ^ x144 ^ x142)
    x17=R(x144 ^ x1 ^ Multiply(0x02,x0) ^ S(x112))
    x102=R(x150 ^ x136 ^ x134)
    x104=Multiply(0x71,x155) ^ Multiply(0x71,x154) ^ x151 ^ Multiply(0xa8,x146) ^ Multiply(0x71,x139) ^ Multiply(0x71,x138) ^ x136 ^ x135 ^ Multiply(0xa8,x130) ^ Multiply(0x39,x112) ^ Multiply(0x71,x108) ^ Multiply(0xa8,x100) ^ Multiply(0x39,x1) ^ S(x102) ^ Multiply(0xe1,S(x63)) ^ Multiply(0xa8,S(x8))
    x106=R(x139 ^ x137 ^ x2 ^ S(x108))
    x110=R(x157 ^ x142 ^ x141 ^ x9 ^ x8)
    x59=x142 ^ x60 ^ x1 ^ Multiply(0x02,x0) ^ S(x110) ^ S(x17)
    if (S(x59))==(Multiply(0xc0,x149) ^ Multiply(0xc0,x134) ^ Multiply(0xc0,x133) ^ Multiply(0x76,x110) ^ Multiply(0x2d,x106) ^ Multiply(0xc0,x102) ^ Multiply(0x2d,x17) ^ Multiply(0x76,x9) ^ Multiply(0x76,x8) ^ Multiply(0x2d,x2) ^ Multiply(0xc0,S(x104)) ^ Multiply(0x9a,S(x47))):
        x57=x58 ^ x9
        x101=R(x135 ^ x134 ^ Multiply(0x07,x110) ^ Multiply(0x04,x106) ^ x102 ^ Multiply(0x04,x17) ^ Multiply(0x07,x9) ^ Multiply(0x07,x8) ^ Multiply(0x04,x2) ^ S(x104) ^ Multiply(0x0b,S(x59)) ^ Multiply(0x09,S(x47)))
        x105=R(x138 ^ x137 ^ x17 ^ S(x108))
        x109=R(x141 ^ x60 ^ x59 ^ x8 ^ x1 ^ Multiply(0x02,x0) ^ S(x17))
        x55=Multiply(0xb7,x151) ^ Multiply(0x9a,x146) ^ Multiply(0xb7,x136) ^ Multiply(0xb7,x134) ^ Multiply(0x9a,x130) ^ Multiply(0xec,x112) ^ Multiply(0x28,x110) ^ x108 ^ Multiply(0xea,x106) ^ Multiply(0xb7,x104) ^ Multiply(0xb7,x102) ^ Multiply(0x9a,x100) ^ x56 ^ Multiply(0xea,x17) ^ Multiply(0x28,x9) ^ Multiply(0x28,x8) ^ Multiply(0xea,x2) ^ Multiply(0xec,x1) ^ Multiply(0xb7,S(x104)) ^ Multiply(0xb7,S(x102)) ^ Multiply(0xb7,S(x101)) ^ Multiply(0xc0,S(x63)) ^ Multiply(0x0d,S(x59)) ^ Multiply(0x78,S(x47)) ^ S(x11) ^ Multiply(0x9a,S(x8))
        if (S(x55))==(Multiply(0xf7,x110) ^ Multiply(0xf6,x109) ^ Multiply(0x4e,x106) ^ Multiply(0x4f,x105) ^ Multiply(0x9e,x102) ^ Multiply(0x9e,x101) ^ x17 ^ Multiply(0x9e,x11) ^ Multiply(0xf7,x9) ^ x8 ^ Multiply(0x4e,x2) ^ Multiply(0x25,S(x59)) ^ Multiply(0x26,S(x57)) ^ Multiply(0x02,S(x47))):
            x53=x154 ^ x56 ^ x55 ^ x54 ^ x17 ^ x2 ^ S(x105) ^ S(x11)
            if (S(x53))==(Multiply(0xd9,x146) ^ Multiply(0xd9,x130) ^ Multiply(0x91,x112) ^ Multiply(0x38,x108) ^ Multiply(0xd9,x100) ^ Multiply(0x38,x56) ^ Multiply(0x38,x55) ^ Multiply(0x91,x1) ^ Multiply(0x71,S(x63)) ^ Multiply(0x38,S(x11)) ^ Multiply(0xd9,S(x8))):
                x45=x136 ^ x134 ^ Multiply(0x8e,x112) ^ Multiply(0x8e,x109) ^ Multiply(0x8d,x108) ^ Multiply(0x8d,x105) ^ x104 ^ x101 ^ Multiply(0x8d,x56) ^ Multiply(0x8d,x55) ^ x46 ^ Multiply(0x8d,x17) ^ x11 ^ Multiply(0x8e,x8) ^ Multiply(0x8e,x1) ^ S(x104) ^ S(x102) ^ Multiply(0x8b,S(x63)) ^ Multiply(0x8b,S(x57)) ^ Multiply(0x89,S(x55)) ^ Multiply(0x89,S(x53)) ^ Multiply(0x8d,S(x11))
                if (S(x45))==(Multiply(0x8d,x109) ^ Multiply(0x8d,x105) ^ Multiply(0x8d,x17) ^ Multiply(0x8d,x8) ^ Multiply(0x8c,S(x57)) ^ Multiply(0x8d,S(x55))):
                    x43=Multiply(0x8e,x112) ^ Multiply(0x8d,x108) ^ Multiply(0x03,x105) ^ x104 ^ x101 ^ Multiply(0x8d,x56) ^ Multiply(0x8d,x55) ^ x46 ^ x45 ^ x44 ^ Multiply(0x03,x17) ^ x11 ^ Multiply(0x8e,x1) ^ Multiply(0x8b,S(x63)) ^ Multiply(0x02,S(x57)) ^ Multiply(0x07,S(x55)) ^ Multiply(0x89,S(x53)) ^ Multiply(0x07,S(x45)) ^ Multiply(0x8d,S(x11))
                    if (S(x43))==(Multiply(0x8d,x112) ^ Multiply(0x8d,x108) ^ Multiply(0x8d,x56) ^ Multiply(0x8d,x55) ^ Multiply(0x8d,x1) ^ Multiply(0x8c,S(x63)) ^ Multiply(0x8d,S(x53)) ^ Multiply(0x8d,S(x11))):
                        x51=x154 ^ x153 ^ x138 ^ x137 ^ x52 ^ x17 ^ x2
                        x103=R(x134 ^ x133 ^ Multiply(0x03,x105) ^ x101 ^ Multiply(0x03,x17) ^ S(x104) ^ Multiply(0x02,S(x57)) ^ Multiply(0x07,S(x55)) ^ Multiply(0x07,S(x45)))
                        x107=R(x140 ^ x137 ^ x52 ^ x51 ^ x17 ^ S(x108))
                        x111=R(x143 ^ x60 ^ x59 ^ x9 ^ x8 ^ x1 ^ Multiply(0x02,x0) ^ S(x17))
                        x41=x42 ^ x11
                        if (S(x41))==(Multiply(0xd9,x111) ^ Multiply(0x91,x107) ^ Multiply(0x48,x105) ^ Multiply(0x38,x103) ^ Multiply(0x38,x101) ^ Multiply(0xd9,x60) ^ Multiply(0xd9,x59) ^ Multiply(0x91,x52) ^ Multiply(0x91,x51) ^ Multiply(0x38,x44) ^ Multiply(0x38,x43) ^ Multiply(0xd9,x17) ^ Multiply(0x38,x11) ^ Multiply(0xd9,x9) ^ Multiply(0xd9,x8) ^ Multiply(0x91,x2) ^ Multiply(0x70,S(x57)) ^ Multiply(0xa8,S(x55)) ^ Multiply(0x71,S(x51)) ^ Multiply(0xa8,S(x45))):
                            x39=Multiply(0x02,x105) ^ Multiply(0xf7,x104) ^ Multiply(0xf7,x101) ^ x100 ^ Multiply(0xf7,x46) ^ Multiply(0xf7,x45) ^ Multiply(0xf7,x44) ^ Multiply(0xf7,x43) ^ x40 ^ Multiply(0x02,x17) ^ Multiply(0xf7,x11) ^ Multiply(0xf4,S(x63)) ^ Multiply(0xf5,S(x57)) ^ Multiply(0xf3,S(x55)) ^ Multiply(0xf6,S(x53)) ^ Multiply(0xf3,S(x45)) ^ Multiply(0xf4,S(x43)) ^ S(x9)
                            if (S(x39))==(Multiply(0x8d,x107) ^ Multiply(0x8c,x105) ^ Multiply(0x8d,x103) ^ Multiply(0x8d,x101) ^ Multiply(0x8d,x52) ^ Multiply(0x8d,x51) ^ Multiply(0x8d,x44) ^ Multiply(0x8d,x43) ^ x17 ^ Multiply(0x8d,x11) ^ Multiply(0x8d,x2) ^ S(x57) ^ Multiply(0x8e,S(x55)) ^ Multiply(0x8c,S(x51)) ^ Multiply(0x8e,S(x45)) ^ Multiply(0x8d,S(x41))):
                                x37=x131 ^ x38 ^ S(x100) ^ S(x8)
                                if (S(x37))==(Multiply(0xd1,x106) ^ Multiply(0xb9,x104) ^ Multiply(0xb9,x102) ^ Multiply(0x68,x100) ^ Multiply(0xb9,x46) ^ Multiply(0xb9,x45) ^ Multiply(0xb9,x44) ^ Multiply(0xb9,x43) ^ Multiply(0x68,x40) ^ Multiply(0x68,x39) ^ Multiply(0xd1,x17) ^ Multiply(0xd1,x2) ^ S(x63) ^ Multiply(0x68,S(x59)) ^ Multiply(0xd1,S(x53)) ^ S(x47) ^ S(x43) ^ Multiply(0x68,S(x9))):
                                    x99=Multiply(0x03,x104) ^ Multiply(0x03,x103) ^ Multiply(0x8f,x100) ^ Multiply(0x03,x46) ^ Multiply(0x03,x45) ^ Multiply(0x8e,x40) ^ Multiply(0x8e,x39) ^ x38 ^ x37 ^ Multiply(0x89,S(x63)) ^ Multiply(0x8c,S(x53)) ^ Multiply(0x02,S(x51)) ^ Multiply(0x89,S(x43)) ^ Multiply(0x07,S(x41)) ^ Multiply(0x07,S(x39)) ^ Multiply(0x8e,S(x9))
                                    x35=x130 ^ x40 ^ x39 ^ x36 ^ S(x99) ^ S(x9) ^ S(x8)
                                    if (S(x35))==(Multiply(0xf6,x103) ^ Multiply(0xf6,x101) ^ Multiply(0x52,x99) ^ Multiply(0xf6,x44) ^ Multiply(0xf6,x43) ^ Multiply(0x52,x40) ^ Multiply(0x52,x39) ^ Multiply(0x52,x38) ^ Multiply(0x52,x37) ^ Multiply(0xf6,x11) ^ Multiply(0xf6,S(x57)) ^ Multiply(0xf6,S(x55)) ^ Multiply(0xa4,S(x51)) ^ Multiply(0xf7,S(x45)) ^ Multiply(0xa5,S(x41)) ^ Multiply(0xa5,S(x39)) ^ Multiply(0x52,S(x9))):
                                        x98=x102 ^ x101 ^ x40 ^ x39 ^ x38 ^ x37 ^ x36 ^ x35 ^ x11 ^ Multiply(0x02,S(x59)) ^ S(x57) ^ S(x55) ^ Multiply(0x03,S(x47)) ^ Multiply(0x02,S(x45)) ^ S(x37) ^ Multiply(0x03,S(x35)) ^ S(x9)
                                        x33=x129 ^ x38 ^ x37 ^ x34 ^ S(x98) ^ S(x8)
                                        if (S(x33))==(Multiply(0x8d,x100) ^ Multiply(0x8d,x40) ^ Multiply(0x8d,x39) ^ Multiply(0x8c,S(x63)) ^ Multiply(0x8d,S(x53)) ^ Multiply(0x8d,S(x43)) ^ Multiply(0x8d,S(x9))):
                                            x32=x40 ^ x39 ^ x38 ^ x37 ^ x36 ^ x35 ^ x34 ^ x33 ^ S(x9)
                                            if (S(x32))==(x133 ^ x46 ^ x45 ^ x11 ^ S(x103)):
                                                x25=x101 ^ S(x57) ^ S(x55) ^ Multiply(0x02,S(x45)) ^ Multiply(0x03,S(x35))
                                                if (S(x25))==(x137 ^ x54 ^ x53 ^ x2 ^ S(x108)):
                                                    x19=x34 ^ x33
                                                    if (S(x19))==(x48 ^ x47 ^ x46 ^ x45 ^ x44 ^ x43 ^ x25 ^ x11):
                                                        x97=x32 ^ Multiply(0x03,S(x57)) ^ S(x55) ^ S(x45) ^ Multiply(0x02,S(x35))
                                                        if (S(x97))==(x132 ^ x38 ^ x37 ^ x36 ^ x35 ^ x32 ^ x19 ^ S(x8)):
                                                            x61=x62 ^ x60 ^ x59 ^ x9 ^ x8 ^ x1
                                                            if (S(x61))==(Multiply(0xf6,x99) ^ Multiply(0xf6,x36) ^ Multiply(0xf6,x35) ^ Multiply(0xf6,x32) ^ Multiply(0xf6,x19) ^ Multiply(0xf6,S(x51)) ^ Multiply(0xf6,S(x41)) ^ Multiply(0xf7,S(x39))):
                                                                x49=x50 ^ x2
                                                                if (S(x49))==(x98 ^ x32 ^ x19 ^ Multiply(0x03,S(x59)) ^ S(x47) ^ Multiply(0x02,S(x37))):
                                                                    x3=x1 ^ x0 ^ S(x2)
                                                                    x4=x60 ^ x59 ^ x9 ^ x8
                                                                    x5=x4 ^ x1
                                                                    x6=x9 ^ x8
                                                                    x7=x6 ^ x4
                                                                    x10=x54 ^ x53 ^ x52 ^ x51 ^ x17 ^ x2
                                                                    x12=x10 ^ S(x11)
                                                                    x13=x52 ^ x51 ^ x17 ^ x2
                                                                    x14=x13 ^ x10
                                                                    x15=x17 ^ x2
                                                                    x16=x15 ^ x13
                                                                    x18=x46 ^ x45 ^ x44 ^ x43 ^ x25 ^ x11
                                                                    x20=x18 ^ S(x19)
                                                                    x21=x44 ^ x43 ^ x25 ^ x11
                                                                    x22=x21 ^ x18
                                                                    x23=x25 ^ x11
                                                                    x24=x23 ^ x21
                                                                    x26=x38 ^ x37 ^ x36 ^ x35 ^ x32 ^ x19
                                                                    x27=x26 ^ S(x9)
                                                                    x28=x36 ^ x35 ^ x32 ^ x19
                                                                    x29=x28 ^ x26
                                                                    x30=x32 ^ x19
                                                                    x31=x30 ^ x28
                                                                    x65=Multiply(0x03,S(x57)) ^ S(x55) ^ S(x45) ^ Multiply(0x02,S(x35))
                                                                    x66=Multiply(0x03,S(x59)) ^ S(x49) ^ S(x47) ^ Multiply(0x02,S(x37))
                                                                    x67=Multiply(0x03,S(x61)) ^ S(x51) ^ S(x41) ^ Multiply(0x02,S(x39))
                                                                    x68=Multiply(0x03,S(x63)) ^ S(x53) ^ S(x43) ^ Multiply(0x02,S(x33))
                                                                    x69=S(x57) ^ S(x55) ^ Multiply(0x02,S(x45)) ^ Multiply(0x03,S(x35))
                                                                    x70=S(x59) ^ S(x49) ^ Multiply(0x02,S(x47)) ^ Multiply(0x03,S(x37))
                                                                    x71=S(x61) ^ S(x51) ^ Multiply(0x02,S(x41)) ^ Multiply(0x03,S(x39))
                                                                    x72=S(x63) ^ S(x53) ^ Multiply(0x02,S(x43)) ^ Multiply(0x03,S(x33))
                                                                    x73=S(x57) ^ Multiply(0x02,S(x55)) ^ Multiply(0x03,S(x45)) ^ S(x35)
                                                                    x74=S(x59) ^ Multiply(0x02,S(x49)) ^ Multiply(0x03,S(x47)) ^ S(x37)
                                                                    x75=S(x61) ^ Multiply(0x02,S(x51)) ^ Multiply(0x03,S(x41)) ^ S(x39)
                                                                    x76=S(x63) ^ Multiply(0x02,S(x53)) ^ Multiply(0x03,S(x43)) ^ S(x33)
                                                                    x77=Multiply(0x02,S(x57)) ^ Multiply(0x03,S(x55)) ^ S(x45) ^ S(x35)
                                                                    x78=Multiply(0x02,S(x59)) ^ Multiply(0x03,S(x49)) ^ S(x47) ^ S(x37)
                                                                    x79=Multiply(0x02,S(x61)) ^ Multiply(0x03,S(x51)) ^ S(x41) ^ S(x39)
                                                                    x80=Multiply(0x02,S(x63)) ^ Multiply(0x03,S(x53)) ^ S(x43) ^ S(x33)
                                                                    x81=x1 ^ Multiply(0x02,x0) ^ S(x17)
                                                                    x82=x81 ^ x4
                                                                    x83=x82 ^ x6
                                                                    x84=x83 ^ x8
                                                                    x85=x10 ^ S(x25)
                                                                    x86=x85 ^ x13
                                                                    x87=x86 ^ x15
                                                                    x88=x87 ^ x17
                                                                    x89=x18 ^ S(x32)
                                                                    x90=x89 ^ x21
                                                                    x91=x90 ^ x23
                                                                    x92=x91 ^ x25
                                                                    x93=x26 ^ S(x8)
                                                                    x94=x93 ^ x28
                                                                    x95=x94 ^ x30
                                                                    x96=x95 ^ x32
                                                                    x113=S(x98)
                                                                    x114=S(x99)
                                                                    x115=S(x100)
                                                                    x116=S(x97)
                                                                    x117=S(x103)
                                                                    x118=S(x104)
                                                                    x119=S(x101)
                                                                    x120=S(x102)
                                                                    x121=S(x108)
                                                                    x122=S(x105)
                                                                    x123=S(x106)
                                                                    x124=S(x107)
                                                                    x125=S(x109)
                                                                    x126=S(x110)
                                                                    x127=S(x111)
                                                                    x128=S(x112)


                                                                    print("# Solution found :\n")
                                                                    K_0 = np.zeros((4, 4), dtype=np.uint8)
                                                                    K_1 = np.zeros((4, 4), dtype=np.uint8)
                                                                    K_1[0][0] = x1
                                                                    K_0[1][3] = x2
                                                                    K_0[0][0] = x3
                                                                    K_1[0][1] = x4
                                                                    K_0[0][1] = x5
                                                                    K_1[0][2] = x6
                                                                    K_0[0][2] = x7
                                                                    K_1[0][3] = x8
                                                                    K_0[0][3] = x9
                                                                    K_1[1][0] = x10
                                                                    K_0[2][3] = x11
                                                                    K_0[1][0] = x12
                                                                    K_1[1][1] = x13
                                                                    K_0[1][1] = x14
                                                                    K_1[1][2] = x15
                                                                    K_0[1][2] = x16
                                                                    K_1[1][3] = x17
                                                                    K_1[2][0] = x18
                                                                    K_0[3][3] = x19
                                                                    K_0[2][0] = x20
                                                                    K_1[2][1] = x21
                                                                    K_0[2][1] = x22
                                                                    K_1[2][2] = x23
                                                                    K_0[2][2] = x24
                                                                    K_1[2][3] = x25
                                                                    K_1[3][0] = x26
                                                                    K_0[3][0] = x27
                                                                    K_1[3][1] = x28
                                                                    K_0[3][1] = x29
                                                                    K_1[3][2] = x30
                                                                    K_0[3][2] = x31
                                                                    K_1[3][3] = x32
                                                                    print(K_0)
                                                                    print(K_1)

                                                                    #print("# Solution found :\n")
                                                                    #print("K_1[0,0] = %02x\n" % (x1))
                                                                    #print("K_0[1,3] = %02x\n" % (x2))
                                                                    #print("K_0[0,0] = %02x\n" % (x3))
                                                                    #print("K_1[0,1] = %02x\n" % (x4))
                                                                    #print("K_0[0,1] = %02x\n" % (x5))
                                                                    #print("K_1[0,2] = %02x\n" % (x6))
                                                                    #print("K_0[0,2] = %02x\n" % (x7))
                                                                    #print("K_1[0,3] = %02x\n" % (x8))
                                                                    #print("K_0[0,3] = %02x\n" % (x9))
                                                                    #print("K_1[1,0] = %02x\n" % (x10))
                                                                    #print("K_0[2,3] = %02x\n" % (x11))
                                                                    #print("K_0[1,0] = %02x\n" % (x12))
                                                                    #print("K_1[1,1] = %02x\n" % (x13))
                                                                    #print("K_0[1,1] = %02x\n" % (x14))
                                                                    #print("K_1[1,2] = %02x\n" % (x15))
                                                                    #print("K_0[1,2] = %02x\n" % (x16))
                                                                    #print("K_1[1,3] = %02x\n" % (x17))
                                                                    #print("K_1[2,0] = %02x\n" % (x18))
                                                                    #print("K_0[3,3] = %02x\n" % (x19))
                                                                    #print("K_0[2,0] = %02x\n" % (x20))
                                                                    #print("K_1[2,1] = %02x\n" % (x21))
                                                                    #print("K_0[2,1] = %02x\n" % (x22))
                                                                    #print("K_1[2,2] = %02x\n" % (x23))
                                                                    #print("K_0[2,2] = %02x\n" % (x24))
                                                                    #print("K_1[2,3] = %02x\n" % (x25))
                                                                    #print("K_1[3,0] = %02x\n" % (x26))
                                                                    #print("K_0[3,0] = %02x\n" % (x27))
                                                                    #print("K_1[3,1] = %02x\n" % (x28))
                                                                    #print("K_0[3,1] = %02x\n" % (x29))
                                                                    #print("K_1[3,2] = %02x\n" % (x30))
                                                                    #print("K_0[3,2] = %02x\n" % (x31))
                                                                    #print("K_1[3,3] = %02x\n" % (x32))
                                                                    #print("X_0[3,3] = %02x\n" % (x33))
                                                                    #print("P[3,3] = %02x\n" % (x34))
                                                                    #print("X_0[3,2] = %02x\n" % (x35))
                                                                    #print("P[3,2] = %02x\n" % (x36))
                                                                    #print("X_0[3,1] = %02x\n" % (x37))
                                                                    #print("P[3,1] = %02x\n" % (x38))
                                                                    #print("X_0[3,0] = %02x\n" % (x39))
                                                                    #print("P[3,0] = %02x\n" % (x40))
                                                                    #print("X_0[2,3] = %02x\n" % (x41))
                                                                    #print("P[2,3] = %02x\n" % (x42))
                                                                    #print("X_0[2,2] = %02x\n" % (x43))
                                                                    #print("P[2,2] = %02x\n" % (x44))
                                                                    #print("X_0[2,1] = %02x\n" % (x45))
                                                                    #print("P[2,1] = %02x\n" % (x46))
                                                                    #print("X_0[2,0] = %02x\n" % (x47))
                                                                    #print("P[2,0] = %02x\n" % (x48))
                                                                    #print("X_0[1,3] = %02x\n" % (x49))
                                                                    #print("P[1,3] = %02x\n" % (x50))
                                                                    #print("X_0[1,2] = %02x\n" % (x51))
                                                                    #print("P[1,2] = %02x\n" % (x52))
                                                                    #print("X_0[1,1] = %02x\n" % (x53))
                                                                    #print("P[1,1] = %02x\n" % (x54))
                                                                    #print("X_0[1,0] = %02x\n" % (x55))
                                                                    #print("P[1,0] = %02x\n" % (x56))
                                                                    #print("X_0[0,3] = %02x\n" % (x57))
                                                                    #print("P[0,3] = %02x\n" % (x58))
                                                                    #print("X_0[0,2] = %02x\n" % (x59))
                                                                    #print("P[0,2] = %02x\n" % (x60))
                                                                    #print("X_0[0,1] = %02x\n" % (x61))
                                                                    #print("P[0,1] = %02x\n" % (x62))
                                                                    #print("X_0[0,0] = %02x\n" % (x63))
                                                                    #print("P[0,0] = %02x\n" % (x64))
                                                                    #print("W_0[3,3] = %02x\n" % (x65))
                                                                    #print("W_0[3,2] = %02x\n" % (x66))
                                                                    #print("W_0[3,1] = %02x\n" % (x67))
                                                                    #print("W_0[3,0] = %02x\n" % (x68))
                                                                    #print("W_0[2,3] = %02x\n" % (x69))
                                                                    #print("W_0[2,2] = %02x\n" % (x70))
                                                                    #print("W_0[2,1] = %02x\n" % (x71))
                                                                    #print("W_0[2,0] = %02x\n" % (x72))
                                                                    #print("W_0[1,3] = %02x\n" % (x73))
                                                                    #print("W_0[1,2] = %02x\n" % (x74))
                                                                    #print("W_0[1,1] = %02x\n" % (x75))
                                                                    #print("W_0[1,0] = %02x\n" % (x76))
                                                                    #print("W_0[0,3] = %02x\n" % (x77))
                                                                    #print("W_0[0,2] = %02x\n" % (x78))
                                                                    #print("W_0[0,1] = %02x\n" % (x79))
                                                                    #print("W_0[0,0] = %02x\n" % (x80))
                                                                    #print("K_2[0,0] = %02x\n" % (x81))
                                                                    #print("K_2[0,1] = %02x\n" % (x82))
                                                                    #print("K_2[0,2] = %02x\n" % (x83))
                                                                    #print("K_2[0,3] = %02x\n" % (x84))
                                                                    #print("K_2[1,0] = %02x\n" % (x85))
                                                                    #print("K_2[1,1] = %02x\n" % (x86))
                                                                    #print("K_2[1,2] = %02x\n" % (x87))
                                                                    #print("K_2[1,3] = %02x\n" % (x88))
                                                                    #print("K_2[2,0] = %02x\n" % (x89))
                                                                    #print("K_2[2,1] = %02x\n" % (x90))
                                                                    #print("K_2[2,2] = %02x\n" % (x91))
                                                                    #print("K_2[2,3] = %02x\n" % (x92))
                                                                    #print("K_2[3,0] = %02x\n" % (x93))
                                                                    #print("K_2[3,1] = %02x\n" % (x94))
                                                                    #print("K_2[3,2] = %02x\n" % (x95))
                                                                    #print("K_2[3,3] = %02x\n" % (x96))
                                                                    #print("X_1[3,3] = %02x\n" % (x97))
                                                                    #print("X_1[3,2] = %02x\n" % (x98))
                                                                    #print("X_1[3,1] = %02x\n" % (x99))
                                                                    #print("X_1[3,0] = %02x\n" % (x100))
                                                                    #print("X_1[2,3] = %02x\n" % (x101))
                                                                    #print("X_1[2,2] = %02x\n" % (x102))
                                                                    #print("X_1[2,1] = %02x\n" % (x103))
                                                                    #print("X_1[2,0] = %02x\n" % (x104))
                                                                    #print("X_1[1,3] = %02x\n" % (x105))
                                                                    #print("X_1[1,2] = %02x\n" % (x106))
                                                                    #print("X_1[1,1] = %02x\n" % (x107))
                                                                    #print("X_1[1,0] = %02x\n" % (x108))
                                                                    #print("X_1[0,3] = %02x\n" % (x109))
                                                                    #print("X_1[0,2] = %02x\n" % (x110))
                                                                    #print("X_1[0,1] = %02x\n" % (x111))
                                                                    #print("X_1[0,0] = %02x\n" % (x112))
                                                                    #print("W_1[3,3] = %02x\n" % (x113))
                                                                    #print("W_1[3,2] = %02x\n" % (x114))
                                                                    #print("W_1[3,1] = %02x\n" % (x115))
                                                                    #print("W_1[3,0] = %02x\n" % (x116))
                                                                    #print("W_1[2,3] = %02x\n" % (x117))
                                                                    #print("W_1[2,2] = %02x\n" % (x118))
                                                                    #print("W_1[2,1] = %02x\n" % (x119))
                                                                    #print("W_1[2,0] = %02x\n" % (x120))
                                                                    #print("W_1[1,3] = %02x\n" % (x121))
                                                                    #print("W_1[1,2] = %02x\n" % (x122))
                                                                    #print("W_1[1,1] = %02x\n" % (x123))
                                                                    #print("W_1[1,0] = %02x\n" % (x124))
                                                                    #print("W_1[0,3] = %02x\n" % (x125))
                                                                    #print("W_1[0,2] = %02x\n" % (x126))
                                                                    #print("W_1[0,1] = %02x\n" % (x127))
                                                                    #print("W_1[0,0] = %02x\n" % (x128))
                                                                    #print("X_2[3,3] = %02x\n" % (x129))
                                                                    #print("X_2[3,2] = %02x\n" % (x130))
                                                                    #print("X_2[3,1] = %02x\n" % (x131))
                                                                    #print("X_2[3,0] = %02x\n" % (x132))
                                                                    #print("X_2[2,3] = %02x\n" % (x133))
                                                                    #print("X_2[2,2] = %02x\n" % (x134))
                                                                    #print("X_2[2,1] = %02x\n" % (x135))
                                                                    #print("X_2[2,0] = %02x\n" % (x136))
                                                                    #print("X_2[1,3] = %02x\n" % (x137))
                                                                    #print("X_2[1,2] = %02x\n" % (x138))
                                                                    #print("X_2[1,1] = %02x\n" % (x139))
                                                                    #print("X_2[1,0] = %02x\n" % (x140))
                                                                    #print("X_2[0,3] = %02x\n" % (x141))
                                                                    #print("X_2[0,2] = %02x\n" % (x142))
                                                                    #print("X_2[0,1] = %02x\n" % (x143))
                                                                    #print("X_2[0,0] = %02x\n" % (x144))
                                                                    #print("X'_2[3,3] = %02x\n" % (x145))
                                                                    #print("X'_2[3,2] = %02x\n" % (x146))
                                                                    #print("X'_2[3,1] = %02x\n" % (x147))
                                                                    #print("X'_2[3,0] = %02x\n" % (x148))
                                                                    #print("X'_2[2,3] = %02x\n" % (x149))
                                                                    #print("X'_2[2,2] = %02x\n" % (x150))
                                                                    #print("X'_2[2,1] = %02x\n" % (x151))
                                                                    #print("X'_2[2,0] = %02x\n" % (x152))
                                                                    #print("X'_2[1,3] = %02x\n" % (x153))
                                                                    #print("X'_2[1,2] = %02x\n" % (x154))
                                                                    #print("X'_2[1,1] = %02x\n" % (x155))
                                                                    #print("X'_2[1,0] = %02x\n" % (x156))
                                                                    #print("X'_2[0,3] = %02x\n" % (x157))
                                                                    #print("X'_2[0,2] = %02x\n" % (x158))
                                                                    #print("X'_2[0,1] = %02x\n" % (x159))
                                                                    #print("X'_2[0,0] = %02x\n" % (x160))
                                                                    return K_0

def Generator( Known):
    x0=1
    x2=1+(rand()%255)
    x8=1+(rand()%255)
    x9=1+(rand()%255)
    x11=1+(rand()%255)
    x17=1+(rand()%255)
    x19=1+(rand()%255)
    x25=1+(rand()%255)
    x32=1+(rand()%255)
    x33=1+(rand()%255)
    x35=1+(rand()%255)
    x37=1+(rand()%255)
    x39=1+(rand()%255)
    x41=1+(rand()%255)
    x43=1+(rand()%255)
    x45=1+(rand()%255)
    x47=1+(rand()%255)
    x49=1+(rand()%255)
    x51=1+(rand()%255)
    x53=1+(rand()%255)
    x55=1+(rand()%255)
    x57=1+(rand()%255)
    x59=1+(rand()%255)
    x61=1+(rand()%255)
    x63=1+(rand()%255)
    print(x32, Multiply(0x03, S(x57)), S(x55), S(x45), Multiply(0x02, S(x35)))
    x97=x32 ^ Multiply(0x03,S(x57)) ^ S(x55) ^ S(x45) ^ Multiply(0x02,S(x35))
    x98=x32 ^ x19 ^ Multiply(0x03,S(x59)) ^ S(x49) ^ S(x47) ^ Multiply(0x02,S(x37))
    x99=1+(rand()%255)
    x100=1+(rand()%255)
    x101=x25 ^ S(x57) ^ S(x55) ^ Multiply(0x02,S(x45)) ^ Multiply(0x03,S(x35))
    x102=x25 ^ x11 ^ S(x59) ^ S(x49) ^ Multiply(0x02,S(x47)) ^ Multiply(0x03,S(x37))
    x103=1+(rand()%255)
    x104=1+(rand()%255)
    x105=x17 ^ S(x57) ^ Multiply(0x02,S(x55)) ^ Multiply(0x03,S(x45)) ^ S(x35)
    x106=x17 ^ x2 ^ S(x59) ^ Multiply(0x02,S(x49)) ^ Multiply(0x03,S(x47)) ^ S(x37)
    x107=1+(rand()%255)
    x108=1+(rand()%255)
    x109=x8 ^ Multiply(0x02,S(x57)) ^ Multiply(0x03,S(x55)) ^ S(x45) ^ S(x35)
    x110=x9 ^ x8 ^ Multiply(0x02,S(x59)) ^ Multiply(0x03,S(x49)) ^ S(x47) ^ S(x37)
    x111=1+(rand()%255)
    x112=1+(rand()%255)
    x160=x112 ^ x0 ^ S(x112) ^ Multiply(0x02,S(x63)) ^ Multiply(0x03,S(x53)) ^ S(x43) ^ S(x33) ^ S(x2)
    x1=x112 ^ Multiply(0x02,S(x63)) ^ Multiply(0x03,S(x53)) ^ S(x43) ^ S(x33)
    x3=x1 ^ x0 ^ S(x2)
    x4=x111 ^ Multiply(0x02,S(x61)) ^ Multiply(0x03,S(x51)) ^ S(x41) ^ S(x39)
    x5=x4 ^ x1
    x6=x9 ^ x8
    x7=x6 ^ x4
    x10=x108 ^ S(x63) ^ Multiply(0x02,S(x53)) ^ Multiply(0x03,S(x43)) ^ S(x33)
    x12=x10 ^ S(x11)
    x13=x107 ^ S(x61) ^ Multiply(0x02,S(x51)) ^ Multiply(0x03,S(x41)) ^ S(x39)
    x14=x13 ^ x10
    x15=x17 ^ x2
    x16=x15 ^ x13
    x18=x104 ^ S(x63) ^ S(x53) ^ Multiply(0x02,S(x43)) ^ Multiply(0x03,S(x33))
    x20=x18 ^ S(x19)
    x21=x103 ^ S(x61) ^ S(x51) ^ Multiply(0x02,S(x41)) ^ Multiply(0x03,S(x39))
    x22=x21 ^ x18
    x23=x25 ^ x11
    x24=x23 ^ x21
    x26=x100 ^ Multiply(0x03,S(x63)) ^ S(x53) ^ S(x43) ^ Multiply(0x02,S(x33))
    x27=x26 ^ S(x9)
    x28=x99 ^ Multiply(0x03,S(x61)) ^ S(x51) ^ S(x41) ^ Multiply(0x02,S(x39))
    x29=x28 ^ x26
    x30=x32 ^ x19
    x31=x30 ^ x28
    x34=x33 ^ x19
    x36=x35 ^ x30 ^ x28
    x38=x37 ^ x28 ^ x26
    x40=x39 ^ x26 ^ S(x9)
    x42=x41 ^ x11
    x44=x43 ^ x23 ^ x21
    x46=x45 ^ x21 ^ x18
    x48=x47 ^ x18 ^ S(x19)
    x50=x49 ^ x2
    x52=x51 ^ x15 ^ x13
    x54=x53 ^ x13 ^ x10
    x56=x55 ^ x10 ^ S(x11)
    x58=x57 ^ x8 ^ x6
    x60=x59 ^ x6 ^ x4
    x62=x61 ^ x4 ^ x1
    x64=x63 ^ x1 ^ x0 ^ S(x2)
    x65=Multiply(0x03,S(x57)) ^ S(x55) ^ S(x45) ^ Multiply(0x02,S(x35))
    x66=Multiply(0x03,S(x59)) ^ S(x49) ^ S(x47) ^ Multiply(0x02,S(x37))
    x67=Multiply(0x03,S(x61)) ^ S(x51) ^ S(x41) ^ Multiply(0x02,S(x39))
    x68=Multiply(0x03,S(x63)) ^ S(x53) ^ S(x43) ^ Multiply(0x02,S(x33))
    x69=S(x57) ^ S(x55) ^ Multiply(0x02,S(x45)) ^ Multiply(0x03,S(x35))
    x70=S(x59) ^ S(x49) ^ Multiply(0x02,S(x47)) ^ Multiply(0x03,S(x37))
    x71=S(x61) ^ S(x51) ^ Multiply(0x02,S(x41)) ^ Multiply(0x03,S(x39))
    x72=S(x63) ^ S(x53) ^ Multiply(0x02,S(x43)) ^ Multiply(0x03,S(x33))
    x73=S(x57) ^ Multiply(0x02,S(x55)) ^ Multiply(0x03,S(x45)) ^ S(x35)
    x74=S(x59) ^ Multiply(0x02,S(x49)) ^ Multiply(0x03,S(x47)) ^ S(x37)
    x75=S(x61) ^ Multiply(0x02,S(x51)) ^ Multiply(0x03,S(x41)) ^ S(x39)
    x76=S(x63) ^ Multiply(0x02,S(x53)) ^ Multiply(0x03,S(x43)) ^ S(x33)
    x77=Multiply(0x02,S(x57)) ^ Multiply(0x03,S(x55)) ^ S(x45) ^ S(x35)
    x78=Multiply(0x02,S(x59)) ^ Multiply(0x03,S(x49)) ^ S(x47) ^ S(x37)
    x79=Multiply(0x02,S(x61)) ^ Multiply(0x03,S(x51)) ^ S(x41) ^ S(x39)
    x80=Multiply(0x02,S(x63)) ^ Multiply(0x03,S(x53)) ^ S(x43) ^ S(x33)
    x81=x1 ^ Multiply(0x02,x0) ^ S(x17)
    x82=x4 ^ x1 ^ Multiply(0x02,x0) ^ S(x17)
    x83=x6 ^ x4 ^ x1 ^ Multiply(0x02,x0) ^ S(x17)
    x84=x8 ^ x6 ^ x4 ^ x1 ^ Multiply(0x02,x0) ^ S(x17)
    x85=x10 ^ S(x25)
    x86=x13 ^ x10 ^ S(x25)
    x87=x15 ^ x13 ^ x10 ^ S(x25)
    x88=x13 ^ x10 ^ x2 ^ S(x25)
    x89=x18 ^ S(x32)
    x90=x21 ^ x18 ^ S(x32)
    x91=x23 ^ x21 ^ x18 ^ S(x32)
    x92=x21 ^ x18 ^ x11 ^ S(x32)
    x93=x26 ^ S(x8)
    x94=x28 ^ x26 ^ S(x8)
    x95=x30 ^ x28 ^ x26 ^ S(x8)
    x96=x28 ^ x26 ^ x19 ^ S(x8)
    x113=S(x98)
    x114=S(x99)
    x115=S(x100)
    x116=S(x97)
    x117=S(x103)
    x118=S(x104)
    x119=S(x101)
    x120=S(x102)
    x121=S(x108)
    x122=S(x105)
    x123=S(x106)
    x124=S(x107)
    x125=S(x109)
    x126=S(x110)
    x127=S(x111)
    x128=S(x112)
    x129=x28 ^ x26 ^ x19 ^ S(x98) ^ S(x8)
    x130=x30 ^ x28 ^ x26 ^ S(x99) ^ S(x8)
    x131=x28 ^ x26 ^ S(x100) ^ S(x8)
    x132=x26 ^ S(x97) ^ S(x8)
    x133=x21 ^ x18 ^ x11 ^ S(x103) ^ S(x32)
    x134=x23 ^ x21 ^ x18 ^ S(x104) ^ S(x32)
    x135=x21 ^ x18 ^ S(x101) ^ S(x32)
    x136=x18 ^ S(x102) ^ S(x32)
    x137=x13 ^ x10 ^ x2 ^ S(x108) ^ S(x25)
    x138=x15 ^ x13 ^ x10 ^ S(x105) ^ S(x25)
    x139=x13 ^ x10 ^ S(x106) ^ S(x25)
    x140=x10 ^ S(x107) ^ S(x25)
    x141=x8 ^ x6 ^ x4 ^ x1 ^ Multiply(0x02,x0) ^ S(x109) ^ S(x17)
    x142=x6 ^ x4 ^ x1 ^ Multiply(0x02,x0) ^ S(x110) ^ S(x17)
    x143=x4 ^ x1 ^ Multiply(0x02,x0) ^ S(x111) ^ S(x17)
    x144=x1 ^ Multiply(0x02,x0) ^ S(x112) ^ S(x17)
    x145=x19 ^ S(x98)
    x146=x30 ^ x28 ^ S(x99)
    x147=x28 ^ x26 ^ S(x100)
    x148=x26 ^ S(x97) ^ S(x9)
    x149=x11 ^ S(x103)
    x150=x23 ^ x21 ^ S(x104)
    x151=x21 ^ x18 ^ S(x101)
    x152=x18 ^ S(x102) ^ S(x19)
    x153=x2 ^ S(x108)
    x154=x15 ^ x13 ^ S(x105)
    x155=x13 ^ x10 ^ S(x106)
    x156=x10 ^ S(x107) ^ S(x11)
    x157=x8 ^ x6 ^ S(x109)
    x158=x6 ^ x4 ^ S(x110)
    x159=x4 ^ x1 ^ S(x111)
    Known[0]=x0 # 1 
    Known[1]=x129 # X_2[3,3] 
    Known[2]=x130 # X_2[3,2] 
    Known[3]=x131 # X_2[3,1] 
    Known[4]=x132 # X_2[3,0] 
    Known[5]=x133 # X_2[2,3] 
    Known[6]=x134 # X_2[2,2] 
    Known[7]=x135 # X_2[2,1] 
    Known[8]=x136 # X_2[2,0] 
    Known[9]=x137 # X_2[1,3] 
    Known[10]=x138 # X_2[1,2] 
    Known[11]=x139 # X_2[1,1] 
    Known[12]=x140 # X_2[1,0] 
    Known[13]=x141 # X_2[0,3] 
    Known[14]=x142 # X_2[0,2] 
    Known[15]=x143 # X_2[0,1] 
    Known[16]=x144 # X_2[0,0] 
    Known[17]=x34 # P[3,3] 
    Known[18]=x36 # P[3,2] 
    Known[19]=x38 # P[3,1] 
    Known[20]=x40 # P[3,0] 
    Known[21]=x42 # P[2,3] 
    Known[22]=x44 # P[2,2] 
    Known[23]=x46 # P[2,1] 
    Known[24]=x48 # P[2,0] 
    Known[25]=x50 # P[1,3] 
    Known[26]=x52 # P[1,2] 
    Known[27]=x54 # P[1,1] 
    Known[28]=x56 # P[1,0] 
    Known[29]=x58 # P[0,3] 
    Known[30]=x60 # P[0,2] 
    Known[31]=x62 # P[0,1] 
    Known[32]=x64 # P[0,0] 
    Known[33]=x145 # X'_2[3,3] 
    Known[34]=x146 # X'_2[3,2] 
    Known[35]=x147 # X'_2[3,1] 
    Known[36]=x148 # X'_2[3,0] 
    Known[37]=x149 # X'_2[2,3] 
    Known[38]=x150 # X'_2[2,2] 
    Known[39]=x151 # X'_2[2,1] 
    Known[40]=x152 # X'_2[2,0] 
    Known[41]=x153 # X'_2[1,3] 
    Known[42]=x154 # X'_2[1,2] 
    Known[43]=x155 # X'_2[1,1] 
    Known[44]=x156 # X'_2[1,0] 
    Known[45]=x157 # X'_2[0,3] 
    Known[46]=x158 # X'_2[0,2] 
    Known[47]=x159 # X'_2[0,1] 
    Known[48]=x160 # X'_2[0,0] 
    return 1

def rand():
    return random.getrandbits(8)

def main(argc, argv):
    print("Hello")
    Known = [0] * 49
    random.seed(os.getpid()) # Init PRNG 
    MakeTableMul2_8()
    # assign values 
    Generator(Known)
    print(Known)
    # Attack 
    Attack(Known)
    return 0

#main(None, None)