# importing libraries
from PyQt5.QtWidgets import *
from PyQt5 import QtCore, QtGui
from PyQt5.QtGui import *
from PyQt5.QtCore import *
import pyqtgraph as pg
import sys
import pandas as pd
import serial
import numpy as np
from scipy import signal
from collections import Counter
##############################################################

raw = serial.Serial(port='COM6', baudrate=20000000, timeout=1)
nSample = 1024

class Plot():
    def __init__(self):
        super().__init__()
        
        # Create the plot window
        self.app = QApplication([])
        self.windowplot = pg.GraphicsLayoutWidget()
        self.windowplot.setFixedWidth(1000)

        # Set up for raw data plot
        self.rawdata = self.windowplot.addPlot(row=0, col=0, title='Raw Data Plot') # Add subplot to window
        self.rawdata.setRange(xRange=[0, nSample]) # Set range to plot 
        self.rawdata_plot = self.rawdata.plot(pen='y')
        self.rawdata.setFixedWidth(500)
        
        #Set up for spectrum
        self.spectrum = self.windowplot.addPlot(row=0, col=1, title='Spectrum Plot') # Add subplot to window
        self.spectrum.setRange(xRange=[1, 100]) # Set range to plot 
        # self.spectrum.setRange(yRange=[1, 50]) # Set range to plot 
        self.spectrum_plot = self.spectrum.plot(pen='y')
        self.spectrum.setFixedWidth(500)
        
        # Set up for max index
        self.max_index = self.windowplot.addLabel(row=1, col=0, size='20pt', text='Max Index: -1') # Add subplot to window
        
        self.windowplot.show()
        
    def update_rawdata(self, data):
        self.rawdata_plot.setData(data)
        self.rawdata.showGrid(y=True)
    
    def update_spectrum(self, data):
        self.spectrum_plot.setData(data)
        self.spectrum.showGrid(y=True)
        
    def update_range(self, nSampleX):
        self.rawdata.setRange(xRange=[0, nSampleX]) # Set range to plot
        
    def update_max_index(self, data):
        self.max_index.setText(f'Max Index: {data}')
        
    def run(self):
        self.app.instance().exec_()
        
    def stop(self):
        self.app.exit()
            
if __name__ == '__main__':
    plot = Plot()
    
    raw_data = []
    spectrum_data = []
    temp_spect = []
    def convertDatatoDf(array: list[int]):
        df = pd.DataFrame(array)
        df.index = [f'Nilai ke-{i+1}' for i in range(len(df))]
        
        return df 
    def convertDatatoExcel(array: list[int], excel: str):
        df = convertDatatoDf(array)
        df.to_excel(f'{excel}.xlsx')
        
    def getPeak(array: list[int], height=0):
        # peaks, _ = signal.find_peaks(array, height=height)
        peak = np.argmax(array[:100])
        return peak

    def most_common_peak(array):
        # Count the occurrences of each element in the array
        count = Counter(array)
        
        # Find the most common element and its count
        most_common = count.most_common(1)
        
        return most_common[0][0] if most_common else None

    def update():
        global temp_spect
        dat1 = raw.read(nSample*2) # Read raw data from serial
        dat2 = np.frombuffer(dat1, dtype='int16', offset=0) # Convert to int16
        
        s = np.array(dat2[0:nSample]) # Make np array
        
        nSampleX = s[nSample-2]
        # fs = s[nSample-3]
        # prf = s[nSample-4]
        plot.update_range(nSampleX)
        
        s[nSampleX:nSample] = 0
        s = s - np.sum(s)/nSampleX
        s[nSampleX:nSample] = 0
        s = s*np.hamming(nSample)
        
        raw = s
        plot.update_rawdata(raw)
        spectrum = 20*np.log10(abs(np.fft.rfft(s))/(nSampleX) + 0.001) #bikin ke skala logaritma
        spectrum = spectrum*spectrum/15 #meningkatkan kontras
        
        temp_spect.append(spectrum[:100])
        plot.update_spectrum(spectrum[:100])
        process()
        # plot.update_max_index(spectrum[:100])
        
    def process():
        global temp_spect
        peaks = []
        if len(temp_spect) == 5:
            for i in range(5):
                peak = getPeak(temp_spect[i])
                print(peak)
                peaks.append(peak)
            print('#####')
            cpeak = most_common_peak(peaks)
            plot.update_max_index(cpeak)
        elif len(temp_spect) > 5: 
            temp_spect = []
            
    try:
        while True:
            raw.flushInput()
            raw.flushOutput()
            timer = QtCore.QTimer()
            timer.timeout.connect(update)
            timer.start(1)
            plot.run()   
    except KeyboardInterrupt: # masih ada masalah
        plot.stop()
        raw.close()
        convertDatatoExcel(raw_data, 'rawdata')
        convertDatatoExcel(spectrum_data, 'spectrum')
        print("Data collection stopped.")
        sys.exit()    