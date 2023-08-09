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
        
        self.main_widget = QWidget(self)
        self.setCentralWidget(self.main_widget)
        layout = QVBoxLayout(self.main_widget)

        # Create the Matplotlib figure and canvas
        self.figure = Figure(facecolor='k')
        self.canvas = FigureCanvas(self.figure)
        layout.addWidget(self.canvas)
        
        # Initiate Variables
        self.radius = 100
        self.angles = np.linspace(0, np.pi, 100)
        
        # Set up for axes
        self.ax = self.figure.add_subplot(111, projection='polar', facecolor='#006d70')
        self.ax.set_position([-0.05,-0.05,1.1,1.05])
        self.ax.set_xlim([0.0,np.pi]) # peak of angle to show
        self.ax.set_ylim([0.0,500]) # peak of distances to show
        self.ax.set_rticks([0, 100, 200, 300, 400, 500]) # show 5 different distances
        self.ax.tick_params(axis='both',colors='w')
        self.ax.grid(color='w',alpha=0.5) # grid color
        self.canvas.draw()
        
        self.show()
        
    def update_dot(self, peak):
        self.ax.clear()
        self.ax.set_position([-0.05,-0.05,1.1,1.05])
        self.ax.set_xlim([0.0,np.pi])
        self.ax.set_ylim([0.0,500]) # peak of distances to show
        self.ax.set_rticks([0, 100, 200, 300, 400, 500]) # show 5 different distances
        self.ax.tick_params(axis='both',colors='w')
        self.ax.grid(color='w',alpha=0.5) # grid color
        random_theta = [random.uniform(0, np.pi) for _ in range(len(peak))]
        self.radius = 100
        # Plot the polar data
        self.ax.scatter(random_theta, peak, c='w')
        self.canvas.draw()
    
    # def blank_plot(self):
    #     self.ax.clear()
    #     self.ax.set_position([-0.05,-0.05,1.1,1.05])
    #     self.ax.set_xlim([0.0,np.pi])
    #     self.ax.set_ylim([0.0,500]) # peak of distances to show
    #     self.ax.set_rticks([0, 100, 200, 300, 400, 500]) # show 5 different distances
    #     self.ax.tick_params(axis='both',colors='w')
    #     self.ax.grid(color='w',alpha=0.5) # grid color
    #     self.canvas.draw()
        
    def blank_plot_sweep(self):
        self.ax.clear()
        self.ax.set_position([-0.05,-0.05,1.1,1.05])
        self.ax.set_xlim([0.0,np.pi])
        self.ax.set_ylim([0.0,500]) # peak of distances to show
        self.ax.set_rticks([0, 100, 200, 300, 400, 500]) # show 5 different distances
        self.ax.tick_params(axis='both',colors='w')
        self.ax.grid(color='w',alpha=0.5) # grid color
        self.ax.plot(self.angles, np.full_like(self.angles, self.radius), c='w')
        
        if self.radius < max(self.ax.get_ylim()):
            self.radius += 100.0
        else: self.radius = 100
        
        self.canvas.draw()

if __name__ == '__main__':
    app = QApplication([])
    plot = MainWindow()
    
    timer = QtCore.QTimer()
    timer2 = QtCore.QTimer()
    def update():
        timer2.start(100)
        dat1 = raw.read(nSample*2) # Read raw data from serial
        dat2 = np.frombuffer(dat1, dtype='int16', offset=0) # Convert to int16
        
        s = np.array(dat2[0:nSample]) # Make np array
        
        # Read some variables
        nSampleX = s[nSample-2]
        #sf = s[nSample-3]
        #prf = s[nSample-4]
        ss = s
        
        s = preprocessing(s, nSampleX) # Data preprocessing
        spect = spectrum(s, nSampleX) # Calculate PSD
        peak = getPeak(spect)
        
        if len(peak) != 0 :
            plot.update_dot(peak)
            timer2.stop()
        # else: timer2.start(100)
           
    try:
        raw.flushInput()
        raw.flushOutput()
        timer.timeout.connect(update)
        timer2.timeout.connect(plot.blank_plot_sweep)
        timer.start(1000)
        
        app.instance().exec()
    except KeyboardInterrupt:
        app.quit() 
        sys.exit()

