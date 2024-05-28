#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Created on 2023/10/19 16:09
@author: Zhen Cheng
"""

import ctypes as ct
import numpy as np

class SLM_UP(object):

    def __init__(self):
        self._SLMLib = ct.CDLL('./HDSLMFunc.dll')

    def __enter__(self):
        return self

    def __exit__(self):
        self.Close_window()

    def _checkError(self, returnValue, errorString):
        if not (returnValue == 0):
            raise Exception(f'returnValue: {returnValue}' + '\n' + errorString)

    def Open_window(self, screenNum=1):
        """
        screenNum表示指定屏幕序号, Open_window用来打开窗口, SLM_Disp_Open会有返回值returnValue=0表示成功, =1表示失败
        """
        self._checkError(self._SLMLib.SLM_Disp_Open(ct.c_ulong(screenNum)), '打开窗口失败')

    def Close_window(self, screenNum=1):
        """
        screenNum表示指定屏幕序号, Close_window用来关闭窗口, SLM_Disp_Close会有返回值returnValue=0表示成功, =1表示失败(经过
        测试有bug，成功了也会返回1，所以加了not)
        """
        self._checkError(not self._SLMLib.SLM_Disp_Close(ct.c_ulong(screenNum)), '关闭窗口失败')

    def Get_size(self, screenNum=1):
        """
        screenNum表示指定屏幕序号, Get_size用来得到窗口大小(width 1920, height 1080),
        SLM_Disp_Info会有返回值returnValue=0表示成功, =1表示失败
        Get_size返回值为(width, height)
        """
        w = ct.c_ushort(0)
        h = ct.c_ushort(0)
        self._checkError(self._SLMLib.SLM_Disp_Info(ct.c_ulong(screenNum), ct.byref(w), ct.byref(h)), '获取窗口大小失败')
        return w.value, h.value

    def Disp_Data_Int(self, phase, screenNum=1, bits=10):
        """
        screenNum表示指定屏幕序号，bits表示显示图片位数(8位(flag = 256)或10位(flag = 1024))
        phase输入(width 1920, height 1080)的整数数组(记得一般数组要转置).
        bits=8, 数组元素范围0-255, 直接以8bit灰度位图显示和存储.
        bits=10, 数组元素范围0-1023, 且存储将每个数据进行拆分，分别存储在RGB彩色图的三个通道内，并以彩色图显示和存储
        """
        flag = 2 ** bits
        sz = phase.shape
        ptr = phase.astype(np.uint16).ctypes.data_as(ct.POINTER(ct.c_int))
        self._checkError(self._SLMLib.SLM_Disp_Data(
            ct.c_ulong(screenNum), ct.c_ushort(sz[0]), ct.c_ushort(sz[1]), ct.c_ulong(flag), ptr), '显示数据失败')

    def Disp_Data_Single(self, phase, screenNum=1, bits=10):
        """
        可接受单精度浮点数的数组，会在内部对其取整，其余与Disp_Data_Int相同
        """
        flag = 2 ** bits
        sz = phase.shape
        ptr = phase.astype(np.float32).ctypes.data_as(ct.POINTER(ct.c_float))
        self._checkError(not self._SLMLib.SLM_Disp_Data_Single(
            ct.c_ulong(screenNum), ct.c_ushort(sz[0]), ct.c_ushort(sz[1]), ct.c_ulong(flag), ptr), '显示数据失败')

    def Disp_Data_Double(self, phase, screenNum=1, bits=10):
        """
        可接受双精度浮点数的数组，会在内部对其取整，其余与Disp_Data_Int相同
        """
        flag = 2 ** bits
        sz = phase.shape
        ptr = phase.astype(np.float64).ctypes.data_as(ct.POINTER(ct.c_double))
        self._checkError(self._SLMLib.SLM_Disp_Data_Double(
            ct.c_ulong(screenNum), ct.c_ushort(sz[0]), ct.c_ushort(sz[1]), ct.c_ulong(flag), ptr), '显示数据失败')

    def Disp_GrayScale(self, GrayScale, screenNum=1, bits=10):
        """
        screenNum表示指定屏幕序号，bits表示显示图片位数(8位(flag = 256)或10位(flag = 1024))
        GrayScale表示纯色灰度图灰度值，bits=8, 数值范围0-255, 0是黑，255是白，超过255的都变成黑色
        bits=10, 数组元素范围0-1023, 同bits=8(因为存储RGB所以显示彩色)
        """
        flag = 2 ** bits
        self._checkError(self._SLMLib.SLM_Disp_GrayScale(
            ct.c_ulong(screenNum), ct.c_ulong(flag), ct.c_ushort(GrayScale)), '显示数据失败')

    def Disp_BMP(self, bmp, screenNum=1, bits=10):
        """这函数用不了!!!!  bmp图片用Disp_ReadImage去显示"""
        flag = 2 ** bits
        self._checkError(self._SLMLib.SLM_Disp_BMP(ct.c_ulong(screenNum), ct.c_ulong(flag), bmp), '显示数据失败')

    def Disp_ReadImage(self, path, screenNum=1, bits=10):
        """
        path表示图片文件路径, 可接受图片格式：png, bmp
        路径格式LPCWSTR 表示 "Long Pointer to a Constant Wide String"，指以双字节字符编码
        """
        flag = 2 ** bits
        self._checkError(self._SLMLib.SLM_Disp_ReadImage(
            ct.c_ulong(screenNum), ct.c_ulong(flag), ct.c_wchar_p(path)), '显示数据失败')

    def Disp_ReadImage_A(self, path, screenNum=1, bits=10):
        """
        path表示图片文件路径, 可接受图片格式：png, bmp
        路径格式LPCSTR 表示 "Long Pointer to a Constant String"， 是一个指向以单字节字符编码
        """
        flag = 2 ** bits
        path_encoded = path.encode('utf-8')
        self._checkError(self._SLMLib.SLM_Disp_ReadImage_A(
            ct.c_ulong(screenNum), ct.c_ulong(flag), ct.c_char_p(path_encoded)), '显示数据失败')

    def Disp_ReadCSV(self, path, screenNum=1, bits=10):
        """
        path表示csv文件路径, 路径格式LPCWSTR 表示 "Long Pointer to a Constant Wide String"，指以双字节字符编码
        """
        flag = 2 ** bits
        self._checkError(self._SLMLib.SLM_Disp_ReadCSV(
            ct.c_ulong(screenNum), ct.c_ulong(flag), ct.c_wchar_p(path)), '显示数据失败')

    def Disp_ReadCSV_A(self, path, screenNum=1, bits=10):
        """
        这函数用不了！！！
        path表示csv文件路径, 路径格式LPCSTR 表示 "Long Pointer to a Constant String"， 是一个指向以单字节字符编码
        """
        flag = 2 ** bits
        path_encoded = path.encode('utf-8')
        self._checkError(self._SLMLib.SLM_Disp_ReadCSV_A(
            ct.c_ulong(screenNum), ct.c_ulong(flag), path_encoded), '显示数据失败')

    def Set_Offset(self, screenNum=1, offset_x=0, offset_y=0):
        """
        设置窗口x和y方向的偏移量, 在设置后投的图才会受影响
        """
        self._checkError(self._SLMLib.SLM_Set_Offset(
            ct.c_ulong(screenNum), ct.c_ushort(offset_x), ct.c_ushort(offset_y)), '设置偏移失败')

    def Get_Offset(self, screenNum=1):
        """
        返回窗口x和y方向的偏移量
        """
        offset_x = ct.c_ushort(0)
        offset_y = ct.c_ushort(0)
        self._checkError(self._SLMLib.SLM_Get_Offset(
            ct.c_ulong(screenNum), ct.byref(offset_x), ct.byref(offset_y)), '获取偏移失败')
        return offset_x.value, offset_y.value
