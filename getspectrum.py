import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from scipy import signal
# from scipy.fft import fftshift, fft2


def readExcelData(excel: str, nSample=1024):
    """
    menerima masukan berupa nama file dan keluaran berupa 
    numpy array 2D
    
    """
    file = pd.read_excel(excel, index_col=0) #get raw data
    df = pd.DataFrame(file) #get dataframe
    data = np.array(df[0:nSample]) #jadiin array
    
    return data

def convertDatatoDf(array: list[int]):
    """
    menerima masukan berupa numpy array 2D
    dan keluaran berupa dataframe
    
    """
    df = pd.DataFrame(array)
    df.index = [f'Nilai ke-{i+1}' for i in range(len(df))]
    
    return df 

def convertDatatoExcel(array: list[int], excel: str):
    """
    menerima masukan berupa numpy array 2D dan judul excel
    dan keluaran berupa file excel
    """
    df = convertDatatoDf(array)
    df.to_excel(f'{excel}.xlsx')

def getPeak(array: list[int], height=40, prominence=0.4, width=1):
    peaks, _ = signal.find_peaks(array, height=height, prominence=prominence, width=width)
    ignore_index = np.arange(0, 101)
    
    filtered_peaks = [peak for peak in peaks if peak not in ignore_index]
    
    return filtered_peaks

"""
if __name__ == '__main__':
    data = readExcelData('dataradar_new.xlsx')
    psd = powerSpectralDensity(data)
    #df = convertDatatoExcel(psd)
    
    s_fft, s_mag, s_phase, s_freq = fastFourierTransform(data)
    
    for i in range(len(psd)):
        x = sort_peak_from_spectrum(psd[i], s_freq)
        
        df = pd.DataFrame(x)
        print(df) #yang tertinggi selalu default signal     
"""