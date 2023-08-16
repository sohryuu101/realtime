# importing libraries
from PyQt6.QtWidgets import *
from PyQt6 import QtCore, QtGui
from PyQt6.QtGui import *
from PyQt6.QtCore import *
import pyqtgraph as pg
import sys
import numpy as np
import random 
import matplotlib.pyplot as plt
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
import serial
from collections import Counter
from scipy import signal
#######################################################################
ser = serial.Serial(port='COM6', baudrate=20000000, timeout=1)
nSample = 1024

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.main_widget = QWidget(self)
        self.setCentralWidget(self.main_widget)
        layout = QHBoxLayout(self.main_widget)

        # Create the Matplotlib figure and canvas
        self.figure = Figure(figsize=(8, 6), facecolor='k', tight_layout=True)
        self.figurex = Figure(figsize=(8, 6), facecolor='k', tight_layout=True)
        self.canvas = FigureCanvas(self.figure)
        self.canvasx = FigureCanvas(self.figurex)
        layout.addWidget(self.canvas)
        layout.addWidget(self.canvasx)
        
        # Set up for ax
        self.ax = self.figure.add_subplot(111, projection='polar', facecolor='#006d70') # add figure
        self.ax.set_xlim([0.0,np.pi]) # peak of angle to show
        self.ax.set_ylim([0.0,10]) # peak of distances to show
        self.ax.set_rticks([0, 2, 4, 6, 8, 10]) # show 5 different distances
        self.ax.tick_params(axis='both',colors='w') # set tick's color to white
        self.ax.grid(color='w',alpha=0.5) # grid color
        
        # Set up for ax2
        self.ax2 = self.figurex.add_subplot(211, facecolor='#000000') # add figure
        self.ax2.set_title('Spectrum', c='w') # set title
        self.ax2.tick_params(axis='both',colors='w') # set tick's color to white
        self.ax2.spines['bottom'].set_color('w') # set bottom spine's color to white
        self.ax2.spines['left'].set_color('w') # set left spine's color to white
        self.canvas.draw()
        
        # Set up for ax3
        self.ax3 = self.figurex.add_subplot(212, facecolor='#000000') # add figure
        self.ax3.set_title('Raw Data', c='w') # set title
        self.ax3.tick_params(axis='both',colors='w') # set tick's color to white
        self.ax3.spines['bottom'].set_color('w') # set bottom spine's color to white
        self.ax3.spines['left'].set_color('w') # set left spine's color to white
        
        self.canvas.draw()
        self.canvasx.draw()
        
        self.show()
        
    def update_dot(self, peak):
        self.ax.clear() # clear the figure
        self.ax.set_xlim([0.0,np.pi]) # set x limit
        self.ax.set_ylim([0.0,10]) # set distances limit
        self.ax.set_rticks([0, 2, 4, 6, 8, 10]) # show 5 different distances
        self.ax.tick_params(axis='both',colors='w') # set tick's color to white
        self.ax.grid(color='w',alpha=0.5) # grid color
        random_theta = random.uniform(0, np.pi) # random theta 
        # random_theta = np.pi/2

        # Plot the polar data
        self.ax.scatter(random_theta, peak, c='w') # scatter plot
        self.ax.annotate(f"{peak: .2f} m", (random_theta, peak), textcoords="offset points", xytext=(0,10), ha='center', c='w') # add range label to dot
        self.canvas.draw()
    
    def update_rawdata(self, data):
        self.ax2.clear() # clear the figure
        self.ax2.set_title('Raw Data', c='w') # set title
        self.ax2.plot(data, c='y') # plot
        self.ax2.set_xlim([0, 200]) # set x limit
        self.canvasx.draw()
    
    def update_spectrum(self, data):
        self.ax3.clear() # clear the figure
        self.ax3.set_title('Spektrum', c='w') # set title
        self.ax3.plot(data, c='y') # plot
        self.canvasx.draw() 

if __name__ == '__main__':
    app = QApplication([])
    plot = MainWindow()
    
    temp_spect = [] # to store 5 spectrum instances
    
    timer = QtCore.QTimer()
    
    def getPeak(array: list[int], height=0):
        # peaks, _ = signal.find_peaks(array, height=height)
        peak = np.argmax(array[:100]) # max value of array
        return peak

    def most_common_peak(array):
        # Count the occurrences of each element in the array
        count = Counter(array)
        
        # Find the most common element and its count
        most_common = count.most_common(1)
        
        return most_common[0][0] if most_common else None
    
    def to_range(peak):
        # insert operation here
        ra = peak*0.0576 + 0.7288
        
        return ra
    
    def update():
        global temp_spect
        dat1 = ser.read(nSample*2) # Read ser data from serial
        dat2 = np.frombuffer(dat1, dtype='int16', offset=0) # Convert to int16
        
        s = np.array(dat2[0:nSample]) # Make np array
        nSampleX = s[nSample-2] # number of x sample
        fs = s[nSample-3] # sampling frequency
        prf = s[nSample-4] # pulse repetition frequency
        
        s[nSampleX:nSample] = 0 # remove noise
        s = s - np.sum(s)/nSampleX # substract value with average
        s[nSampleX:nSample] = 0 # remove noise
        s = s*np.hamming(nSample) # windowing 
        
        raw = s # raw data
        plot.update_rawdata(raw) # plot the raw data
        spectrum = 20*np.log10(abs(np.fft.rfft(s))/(nSampleX) + 0.001) # make it to logaritmic scale
        spectrum = spectrum*spectrum/15 # increase contrast
        
        temp_spect.append(spectrum[50:150]) # store every 5 spectrum
        plot.update_spectrum(spectrum[50:150]) # update spectrum
        
        process() # process every 5 spectrum to find peak
        
    def process():
        global temp_spect
        peaks = [] # to store peaks
        if len(temp_spect) == 5:
            for i in range(5):
                peak = getPeak(temp_spect[i]) # get peak
                peaks.append(peak) # add peak to peaks list
            cpeak = most_common_peak(peaks) # get most common peak from 5 peaks
            ra = to_range(cpeak) # convert to range
            plot.update_dot(ra) # update ppi plot
        elif len(temp_spect) > 5: 
            temp_spect = [] # reset temp_spect every 5 spectrum
           
    try:
        while True:
            ser.flushInput()
            ser.flushOutput()
            timer.timeout.connect(update)
            timer.start(1)
        
            app.instance().exec()
    except KeyboardInterrupt:
        app.quit() 
        sys.exit()

