# importing libraries
from PyQt6.QtWidgets import *
from PyQt6 import QtCore, QtGui
from PyQt6.QtGui import *
from PyQt6.QtCore import *
import pyqtgraph as pg
import sys
from getspectrum import preprocessing, spectrum, getPeak, spectrum, convertDatatoDf
import numpy as np
import random 
import matplotlib.pyplot as plt
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
import serial

#######################################################################
raw = serial.Serial(port='COM6', baudrate=20000000, timeout=1)
nSample = 1024

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        #self.setWindowTitle("PPI")
        self.main_widget = QWidget(self)
        self.setCentralWidget(self.main_widget)
        layout = QVBoxLayout(self.main_widget)

        # Create the Matplotlib figure and canvas
        self.figure = Figure(figsize=(8, 6), facecolor='k', tight_layout=True)
        self.canvas = FigureCanvas(self.figure)
        layout.addWidget(self.canvas)
        
        # Initiate Variables
        # self.radius = 0
        # self.angles = np.linspace(0, np.pi, 100)
        
        # Set up for ax
        self.ax = self.figure.add_subplot(121, projection='polar', facecolor='#006d70')
        # self.ax.set_position([-0.05,-0.05,1.1,1.05])
        self.ax.set_xlim([0.0,np.pi]) # peak of angle to show
        self.ax.set_ylim([0.0,100]) # peak of distances to show
        self.ax.set_rticks([0, 20, 40, 60, 80, 100]) # show 5 different distances
        self.ax.tick_params(axis='both',colors='w')
        self.ax.grid(color='w',alpha=0.5) # grid color
        self.ax.text(0.5, -0.01, "Jarak: 0", size=12, ha='center', c='w', transform=self.ax.transAxes)
        
        # Set up for ax2
        self.ax2 = self.figure.add_subplot(222, facecolor='#000000')
        self.ax2.set_title('Spectrum', c='w')
        self.ax2.tick_params(axis='both',colors='w')
        self.ax2.spines['bottom'].set_color('w')
        self.ax2.spines['left'].set_color('w')
        self.canvas.draw()
        
        self.ax3 = self.figure.add_subplot(224, facecolor='#000000')
        self.ax3.set_title('Raw Data', c='w')
        self.ax3.tick_params(axis='both',colors='w')
        self.ax3.spines['bottom'].set_color('w')
        self.ax3.spines['left'].set_color('w')
        
        plt.tight_layout()
        self.canvas.draw()

        self.show()
        
    def update_dot(self, peak):
        self.ax.clear()
        # self.ax.set_position([-0.05,-0.05,1.1,1.05])
        self.ax.set_xlim([0.0,np.pi])
        self.ax.set_ylim([0.0,100]) # peak of distances to show
        self.ax.set_rticks([0, 20, 40, 60, 80, 100]) # show 5 different distances
        self.ax.tick_params(axis='both',colors='w')
        self.ax.grid(color='w',alpha=0.5) # grid color
        # random_theta = random.uniform(0, np.pi)
        random_theta = np.pi/2
        # self.radius = 0
        # Plot the polar data
        self.ax.scatter(random_theta, peak, c='w')
        self.ax.text(0.5, -0.01, f"Jarak: {peak} m", size=12, ha='center', c='w', transform=self.ax.transAxes)
        self.canvas.draw()
    
    def update_rawdata(self, data):
        self.ax2.clear()
        self.ax2.set_title('Raw Data', c='w')
        self.ax2.plot(data, c='y')
        # self.ax2.set_xlim([0, 500])
    
    def update_spectrum(self, data):
        self.ax3.clear()
        self.ax3.set_title('Spektrum', c='w')
        self.ax3.plot(data, c='y')

if __name__ == '__main__':
    app = QApplication([])
    plot = MainWindow()
    
    temp_spect = []
    
    timer = QtCore.QTimer()
    def update():
        global temp_spect
        dat1 = raw.read(nSample*2) # Read raw data from serial
        dat2 = np.frombuffer(dat1, dtype='int16', offset=0) # Convert to int16
        
        s = np.array(dat2[0:nSample]) # Make np array
        nSampleX = s[nSample-2]
        fs = s[nSample-3]
        prf = s[nSample-4]
        
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
        peak = getPeak(spectrum[:100])
        plot.update_dot(peak)
           
    try:
        while True:
            raw.flushInput()
            raw.flushOutput()
            timer.timeout.connect(update)
            timer.start(1)
        
            app.instance().exec()
    except KeyboardInterrupt:
        app.quit() 
        sys.exit()

