# KerberosSDR Python GUI

# Copyright (C) 2018-2019  Carl Laufer, Tamás Pető
#
#   This program is free software: you can redistribute it and/or modify
#   it under the terms of the GNU General Public License as published by
#   the Free Software Foundation, either version 3 of the License, or
#   any later version.
#
#   This program is distributed in the hope that it will be useful,
#   but WITHOUT ANY WARRANTY; without even the implied warranty of
#   MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#   GNU General Public License for more details.
#
#   You should have received a copy of the GNU General Public License
#   along with this program.  If not, see <https://www.gnu.org/licenses/>.
#

# -*- coding: utf-8 -*

import sys
import os
import time
import math
import pyqtgraph as pg
import pyqtgraph.exporters
import numpy as np
import scipy
from bottle import route, run, request, get, post, redirect, template, static_file
import threading
import subprocess
import save_settings as settings

np.seterr(divide='ignore')

# Import Kerberos modules
currentPath = os.path.dirname(os.path.realpath(__file__))
rootPath = os.path.dirname(currentPath)

receiverPath        = os.path.join(rootPath, "_receiver")
signalProcessorPath = os.path.join(rootPath, "_signalProcessing")

sys.path.insert(0, receiverPath)
sys.path.insert(0, signalProcessorPath)

from hydra_receiver import ReceiverRTLSDR

# Import graphical user interface packages
from PyQt4.QtGui import *
from PyQt4 import QtCore
from PyQt4 import QtGui

try:
    _fromUtf8 = QtCore.QString.fromUtf8
except AttributeError:
    _fromUtf8 = lambda s: s

# Import packages for plotting
import matplotlib
matplotlib.use('Agg') # For Raspberry Pi compatiblity
from matplotlib import cm
#from matplotlib.backends.backend_qt4agg import FigureCanvasQTAgg as FigureCanvas
#from matplotlib.backends.backend_qt4 import NavigationToolbar2QT as NavigationToolbar
#import matplotlib.pyplot as plt
#import matplotlib.patches as patches


from hydra_main_window_layout import Ui_MainWindow
from hydra_signal_processor import SignalProcessor

# Import the pyArgus module
#root_path = os.getcwd()
#pyargus_path = os.path.join(os.path.join(root_path, "pyArgus"), "pyArgus")
#sys.path.insert(0, pyargus_path)
#import directionEstimation as de

from pyargus import directionEstimation as de

class MainWindow(QMainWindow, Ui_MainWindow):

    def __init__ (self,parent = None):
        super(MainWindow, self).__init__(parent)
        self.setupUi(self)

        #f = open('/dev/null', 'w')
        #sys.stdout = f

        self.tabWidget.setCurrentIndex(0)

        # Set pyqtgraph to use white background, black foreground
        pg.setConfigOption('background', (61, 61, 61))
        pg.setConfigOption('foreground', 'w')
        pg.setConfigOption('imageAxisOrder', 'row-major')
        #pg.setConfigOption('useOpenGL', True)
        #pg.setConfigOption('useWeave', True)

        # Spectrum display

        self.win_spectrum = pg.GraphicsWindow(title="Quad Channel Spectrum")

        self.export_spectrum = pg.exporters.ImageExporter(self.win_spectrum.scene())

        self.plotWidget_spectrum_ch1 = self.win_spectrum.addPlot(title="Channel 1")
        self.plotWidget_spectrum_ch2 = self.win_spectrum.addPlot(title="Channel 2")
        self.win_spectrum.nextRow()
        self.plotWidget_spectrum_ch3 = self.win_spectrum.addPlot(title="Channel 3")
        self.plotWidget_spectrum_ch4 = self.win_spectrum.addPlot(title="Channel 4")

        self.gridLayout_spectrum.addWidget(self.win_spectrum, 1, 1, 1, 1)

        x = np.arange(1000)
        y = np.random.normal(size=(4,1000))

        self.spectrum_ch1_curve = self.plotWidget_spectrum_ch1.plot(x, y[0], clear=True, pen=(255, 199, 15))
        self.spectrum_ch2_curve = self.plotWidget_spectrum_ch2.plot(x, y[1], clear=True, pen='r')
        self.spectrum_ch3_curve = self.plotWidget_spectrum_ch3.plot(x, y[2], clear=True, pen='g')
        self.spectrum_ch4_curve = self.plotWidget_spectrum_ch4.plot(x, y[3], clear=True, pen=(9, 237, 237))


        self.plotWidget_spectrum_ch1.setLabel("bottom", "Frequency [MHz]")
        self.plotWidget_spectrum_ch1.setLabel("left", "Amplitude [dBm]")
        self.plotWidget_spectrum_ch2.setLabel("bottom", "Frequency [MHz]")
        self.plotWidget_spectrum_ch2.setLabel("left", "Amplitude [dBm]")
        self.plotWidget_spectrum_ch3.setLabel("bottom", "Frequency [MHz]")
        self.plotWidget_spectrum_ch3.setLabel("left", "Amplitude [dBm]")
        self.plotWidget_spectrum_ch4.setLabel("bottom", "Frequency [MHz]")
        self.plotWidget_spectrum_ch4.setLabel("left", "Amplitude [dBm]")

        #---> Sync display <---
        # --> Delay

        self.win_sync = pg.GraphicsWindow(title="Receiver Sync")

        self.export_sync = pg.exporters.ImageExporter(self.win_sync.scene())

        self.plotWidget_sync_absx = self.win_sync.addPlot(title="ABS X Corr")
        #self.plotWidget_sync_absx.setDownsampling(ds=4, mode='subsample')
        #self.plotWidget_sync_normph = self.win_sync.addPlot(title="Normalized Phasors")
        self.win_sync.nextRow()
        self.plotWidget_sync_sampd = self.win_sync.addPlot(title="Sample Delay History")
        self.plotWidget_sync_phasediff = self.win_sync.addPlot(title="Phase Diff History")

        self.gridLayout_sync.addWidget(self.win_sync, 1, 1, 1, 1)

        x = np.arange(1000)
        y = np.random.normal(size=(4,1000))

        #---> DOA results display <---

        self.win_DOA = pg.GraphicsWindow(title="DOA Plot")
        #Set up image exporter for web display
        self.export_DOA = pg.exporters.ImageExporter(self.win_DOA.scene())

        self.plotWidget_DOA = self.win_DOA.addPlot(title="Direction of Arrival Estimation")
        self.plotWidget_DOA.setLabel("bottom", "Incident Angle [deg]")
        self.plotWidget_DOA.setLabel("left", "Amplitude [dB]")
        self.plotWidget_DOA.showGrid(x=True, alpha=0.25)
        self.gridLayout_DOA.addWidget(self.win_DOA, 1, 1, 1, 1)

        self.DOA_res_fd = open("/ram/DOA_value.html","w") # DOA estimation result file descriptor

        # Junk data to just init plot legends
        x = np.arange(1000)
        y = np.random.normal(size=(4,1000))

        self.plotWidget_DOA.addLegend()

        self.plotWidget_DOA.plot(x, y[0], pen=pg.mkPen((255, 199, 15), width=2), name="Bartlett")
        self.plotWidget_DOA.plot(x, y[1], pen=pg.mkPen('g', width=2), name="Capon")
        self.plotWidget_DOA.plot(x, y[2], pen=pg.mkPen('r', width=2), name="MEM")
        self.plotWidget_DOA.plot(x, y[3], pen=pg.mkPen((9, 237, 237), width=2), name="MUSIC")

        #---> Passive radar results display <---

        self.win_PR = pg.GraphicsWindow(title="Passive Radar")

        self.export_PR = pg.exporters.ImageExporter(self.win_PR.scene())

        self.plt_PR = self.win_PR.addPlot(Title="Range-Doppler Matrix")
        self.plt_PR.setLabel("bottom", "Range")
        self.plt_PR.setLabel("left", "Doppler (Speed)")

        self.PR_interp_factor = 8

        self.plt_PR.getAxis("bottom").setScale(1.0/self.PR_interp_factor)
        self.plt_PR.getAxis("left").setScale(1.0/self.PR_interp_factor)

        rand_mat = np.random.rand(50,50)
        self.CAFMatrixOld = 0 #np.random.rand(50,50)
        self.img_PR = pg.ImageView()

        self.plt_PR.addItem(self.img_PR.imageItem)

        self.img_PR.setImage(rand_mat)
        self.img_PR.autoLevels()
        self.img_PR.autoRange()

        # Take the color map from matplotlib because it's nicer than pyqtgraph's
        colormap = cm.get_cmap("jet")
        colormap._init()
        lut = (colormap._lut * 255).view(np.ndarray)
        self.img_PR.imageItem.setLookupTable(lut)

        #self.img_PR.setPredefinedGradient('spectrum')

        self.gridLayout_RD.addWidget(self.win_PR, 1, 1, 1, 1)

        # Connect pushbutton signals
        self.pushButton_close.clicked.connect(self.pb_close_clicked)
        self.pushButton_proc_control.clicked.connect(self.pb_proc_control_clicked)
        self.pushButton_sync.clicked.connect(self.pb_sync_clicked)
        self.pushButton_iq_calib.clicked.connect(self.pb_calibrate_iq_clicked)
        self.pushButton_del_sync_history.clicked.connect(self.pb_del_sync_history_clicked)
        self.pushButton_DOA_cal_90.clicked.connect(self.pb_calibrate_DOA_90_clicked)
        self.pushButton_set_receiver_config.clicked.connect(self.pb_rec_reconfig_clicked)
        self.stream_state = False

        # Status and configuration tab control
        self.tabWidget.currentChanged.connect(self.tab_changed)

        # Connect checkbox signals
        self.checkBox_en_uniform_gain.stateChanged.connect(self.pb_rec_reconfig_clicked)
        self.checkBox_en_sync_display.stateChanged.connect(self.set_sync_params)
        self.checkBox_en_spectrum.stateChanged.connect(self.set_spectrum_params)
        self.checkBox_en_DOA.stateChanged.connect(self.set_DOA_params)
        self.checkBox_en_DOA_Bartlett.stateChanged.connect(self.set_DOA_params)
        self.checkBox_en_DOA_Capon.stateChanged.connect(self.set_DOA_params)
        self.checkBox_en_DOA_MEM.stateChanged.connect(self.set_DOA_params)
        self.checkBox_en_DOA_MUSIC.stateChanged.connect(self.set_DOA_params)
        self.checkBox_en_DOA_FB_avg.stateChanged.connect(self.set_DOA_params)
        self.checkBox_en_dc_compensation.stateChanged.connect(self.set_iq_preprocessing_params)
        self.checkBox_en_passive_radar.stateChanged.connect(self.set_PR_params)
        self.checkBox_en_td_filter.stateChanged.connect(self.set_PR_params)
        self.checkBox_en_autodet.stateChanged.connect(self.set_PR_params)
        self.checkBox_en_noise_source.stateChanged.connect(self.switch_noise_source)
        self.checkBox_en_peakhold.stateChanged.connect(self.set_PR_params) 


        # Connect spinbox signals
        self.doubleSpinBox_filterbw.valueChanged.connect(self.set_iq_preprocessing_params)
        self.spinBox_fir_tap_size.valueChanged.connect(self.set_iq_preprocessing_params)
        self.spinBox_decimation.valueChanged.connect(self.set_iq_preprocessing_params)

        self.doubleSpinBox_DOA_d.valueChanged.connect(self.set_DOA_params)
        self.spinBox_DOA_sample_size.valueChanged.connect(self.set_DOA_params)

        self.doubleSpinBox_center_freq.valueChanged.connect(self.set_DOA_params)

        self.spinBox_td_filter_dimension.valueChanged.connect(self.set_PR_params)
        self.doubleSpinBox_cc_det_max_range.valueChanged.connect(self.set_PR_params)
        self.doubleSpinBox_cc_det_max_Doppler.valueChanged.connect(self.set_PR_params)
        self.spinBox_ref_ch_select.valueChanged.connect(self.set_PR_params)
        self.spinBox_surv_ch_select.valueChanged.connect(self.set_PR_params)
        self.spinBox_cfar_est_win.valueChanged.connect(self.set_PR_params)
        self.spinBox_cfar_guard_win.valueChanged.connect(self.set_PR_params)
        self.doubleSpinBox_cfar_threshold.valueChanged.connect(self.set_PR_params)

        self.spinBox_resync_time.valueChanged.connect(self.set_resync_time)

        # Connect combobox signals
        self.comboBox_antenna_alignment.currentIndexChanged.connect(self.set_DOA_params)
        self.comboBox_cc_det_windowing.currentIndexChanged.connect(self.set_windowing_mode)

        # Instantiate and configura Hydra modules
        self.module_receiver = ReceiverRTLSDR()

        self.module_receiver.block_size = int(sys.argv[1]) * 1024

        self.module_signal_processor = SignalProcessor(module_receiver=self.module_receiver)

        self.module_signal_processor.signal_overdrive.connect(self.power_level_update)
        self.module_signal_processor.signal_period.connect(self.period_time_update)
        self.module_signal_processor.signal_spectrum_ready.connect(self.spectrum_plot)
        self.module_signal_processor.signal_sync_ready.connect(self.delay_plot)
        self.module_signal_processor.signal_DOA_ready.connect(self.DOA_plot)
        self.module_signal_processor.signal_PR_ready.connect(self.RD_plot)
        # -> Set default confiration for the signal processing module
        self.set_spectrum_params()
        self.set_sync_params()
        self.set_DOA_params()
        self.set_windowing_mode()


        self.DOA_time = time.time()
        self.PR_time = time.time()
        self.sync_time = time.time()
        self.spectrum_time = time.time()

        # Init peak hold GUI setting
        self.en_peakhold = False



        #self.spectrum_plot()
        #self.delay_plot()
        #self.DOA_plot()
        #self.RD_plot()


        # Set default confiuration for the GUI components
        self.set_default_configuration()

        self.ip_addr = sys.argv[2]
        threading.Thread(target=run, kwargs=dict(host=self.ip_addr, port=8080, quiet=True, debug=False, server='paste')).start()

    #-----------------------------------------------------------------
    #
    #-----------------------------------------------------------------




    def set_default_configuration(self):

        self.power_level_update(0)
        self.checkBox_en_spectrum.setChecked(False)
        self.checkBox_en_DOA.setChecked(False)

    def calculate_spacing(self):
        ant_arrangement_index = self.comboBox_antenna_alignment.currentText()
        ant_meters = self.doubleSpinBox_DOA_d.value()
        freq = self.doubleSpinBox_center_freq.value()
        wave_length = (299.79/freq)
        if ant_arrangement_index == "ULA":
            ant_spacing = (ant_meters/wave_length)

        elif ant_arrangement_index == "UCA":
            ant_spacing = ((ant_meters/wave_length)/math.sqrt(2))

        return ant_spacing

    def tab_changed(self):
        tab_index = self.tabWidget.currentIndex()

        if tab_index == 0:  # Spectrum tab
            self.stackedWidget_config.setCurrentIndex(0)
        elif tab_index == 1:  # Sync tab
            self.stackedWidget_config.setCurrentIndex(1)
        elif tab_index == 2:  # DOA tab
            self.stackedWidget_config.setCurrentIndex(2)
        elif tab_index == 3:  # PR tab
            self.stackedWidget_config.setCurrentIndex(3)

    def set_sync_params(self):
        if self.checkBox_en_sync_display.checkState():
            self.module_signal_processor.en_sync = True
        else:
            self.module_signal_processor.en_sync = False
    def set_spectrum_params(self):
        if self.checkBox_en_spectrum.checkState():
            self.module_signal_processor.en_spectrum = True
        else:
            self.module_signal_processor.en_spectrum = False


    def pb_rec_reconfig_clicked(self):
        center_freq = self.doubleSpinBox_center_freq.value() *10**6
        sample_rate = float(self.comboBox_sampling_freq.currentText()) *10**6 #self.doubleSpinBox_sampling_freq.value()*10**6
        gain = [0,0,0,0]
        if self.checkBox_en_uniform_gain.checkState():
            gain[0] = 10*float(self.comboBox_gain.currentText())
            gain[1] = 10*float(self.comboBox_gain.currentText())
            gain[2] = 10*float(self.comboBox_gain.currentText())
            gain[3] = 10*float(self.comboBox_gain.currentText())
            gain_index = self.comboBox_gain.currentIndex()
            self.module_receiver.receiver_gain = 10*float(self.comboBox_gain.currentText())
            form.comboBox_gain_2.setCurrentIndex(int(gain_index))
            form.comboBox_gain_2.setEnabled(False)
            self.module_receiver.receiver_gain_2 = 10*float(self.comboBox_gain.currentText())
            form.comboBox_gain_3.setCurrentIndex(int(gain_index))
            form.comboBox_gain_3.setEnabled(False)
            self.module_receiver.receiver_gain_3 = 10*float(self.comboBox_gain.currentText())
            form.comboBox_gain_4.setCurrentIndex(int(gain_index))
            form.comboBox_gain_4.setEnabled(False)
            self.module_receiver.receiver_gain_4 = 10*float(self.comboBox_gain.currentText())
        else:
            gain[0] = 10*float(self.comboBox_gain.currentText())
            gain[1] = 10*float(self.comboBox_gain_2.currentText())
            gain[2] = 10*float(self.comboBox_gain_3.currentText())
            gain[3] = 10*float(self.comboBox_gain_4.currentText())
            self.module_receiver.receiver_gain = 10*float(self.comboBox_gain.currentText())
            form.comboBox_gain_2.setEnabled(True)
            self.module_receiver.receiver_gain_2 = 10*float(self.comboBox_gain_2.currentText())
            form.comboBox_gain_3.setEnabled(True)
            self.module_receiver.receiver_gain_3 = 10*float(self.comboBox_gain_3.currentText())
            form.comboBox_gain_4.setEnabled(True)
            self.module_receiver.receiver_gain_4 = 10*float(self.comboBox_gain_4.currentText())

        self.module_receiver.fs = float(self.comboBox_sampling_freq.currentText())*10**6 #self.doubleSpinBox_sampling_freq.value()*10**6
        self.module_signal_processor.fs = self.module_receiver.fs/self.module_receiver.decimation_ratio

        self.module_signal_processor.center_freq=self.doubleSpinBox_center_freq.value() *10**6
        self.module_receiver.reconfigure_tuner(center_freq, sample_rate, gain)

    def switch_noise_source(self):
        if self.checkBox_en_noise_source.checkState():
            self.module_signal_processor.noise_checked = True
            self.module_receiver.switch_noise_source(1)
        else:
            self.module_signal_processor.noise_checked = False
            self.module_receiver.switch_noise_source(0)
    def set_iq_preprocessing_params(self):
        """
            Update IQ preprocessing parameters
            Callback function of:
                -
        """
        # Set DC compensations
        if self.checkBox_en_dc_compensation.checkState():
            self.module_receiver.en_dc_compensation = True
        else:
            self.module_receiver.en_dc_compensation = False

        # Set FIR filter parameters
        tap_size = self.spinBox_fir_tap_size.value()
        bw = self.doubleSpinBox_filterbw.value() * 10**3  # ->[kHz]
        self.module_receiver.set_fir_coeffs(tap_size, bw)

        # Set Decimation
        self.module_receiver.decimation_ratio = self.spinBox_decimation.value()
        self.module_signal_processor.fs = self.module_receiver.fs/self.module_receiver.decimation_ratio

    def set_windowing_mode(self):
        self.module_signal_processor.windowing_mode = int(self.comboBox_cc_det_windowing.currentIndex())


    def set_DOA_params(self):
        """
            Update DOA processing parameters
            Callback function of:
                -
        """
        #  Set DOA processing option
        if self.checkBox_en_DOA.checkState():
            self.module_signal_processor.en_DOA_estimation = True
        else:
            self.module_signal_processor.en_DOA_estimation = False


        if self.checkBox_en_DOA_Bartlett.checkState():
            self.module_signal_processor.en_DOA_Bartlett = True
        else:
            self.module_signal_processor.en_DOA_Bartlett = False

        if self.checkBox_en_DOA_Capon.checkState():
            self.module_signal_processor.en_DOA_Capon = True
        else:
            self.module_signal_processor.en_DOA_Capon = False

        if self.checkBox_en_DOA_MEM.checkState():
            self.module_signal_processor.en_DOA_MEM = True
        else:
            self.module_signal_processor.en_DOA_MEM = False

        if self.checkBox_en_DOA_MUSIC.checkState():
            self.module_signal_processor.en_DOA_MUSIC = True
        else:
            self.module_signal_processor.en_DOA_MUSIC = False

        if self.checkBox_en_DOA_FB_avg.checkState():
            self.module_signal_processor.en_DOA_FB_avg = True
        else:
            self.module_signal_processor.en_DOA_FB_avg = False

        #self.module_signal_processor.DOA_inter_elem_space = self.doubleSpinBox_DOA_d.value()
        self.module_signal_processor.DOA_inter_elem_space = self.calculate_spacing()
        self.module_signal_processor.DOA_ant_alignment = self.comboBox_antenna_alignment.currentText()

        #print(str(self.module_signal_processor.DOA_inter_elem_space) + "\n")

        if self.module_signal_processor.DOA_ant_alignment == "UCA":
            self.checkBox_en_DOA_FB_avg.setEnabled(False)
            self.checkBox_en_DOA_FB_avg.setCheckState(False)
        else:
            self.checkBox_en_DOA_FB_avg.setEnabled(True)

        self.module_signal_processor.DOA_sample_size = 2**self.spinBox_DOA_sample_size.value()


    def set_PR_params(self):
        if self.checkBox_en_passive_radar.checkState():
            self.module_signal_processor.en_PR_processing = True
        else:
            self.module_signal_processor.en_PR_processing = False

        if self.checkBox_en_td_filter.checkState():
            self.module_signal_processor.en_td_filtering = True
        else:
            self.module_signal_processor.en_td_filtering = False

        if self.checkBox_en_autodet.checkState():
            self.module_signal_processor.en_PR_autodet = True
        else:
            self.module_signal_processor.en_PR_autodet = False

        # Set CFAR parameters
        self.module_signal_processor.cfar_win_params=[self.spinBox_cfar_est_win.value(), self.spinBox_cfar_est_win.value(), self.spinBox_cfar_guard_win.value(), self.spinBox_cfar_guard_win.value()]

        self.module_signal_processor.cfar_threshold = self.doubleSpinBox_cfar_threshold.value()

        # Set Time-domain clutter fitler parameters
        self.module_signal_processor.td_filter_dimension = self.spinBox_td_filter_dimension.value()

        # Set Cross-Correlation detector parameters
        self.module_signal_processor.max_range = int(self.doubleSpinBox_cc_det_max_range.value())
        self.module_signal_processor.max_Doppler = int(self.doubleSpinBox_cc_det_max_Doppler.value())

        # General channel settings
        self.module_signal_processor.ref_ch_id = self.spinBox_ref_ch_select.value()
        self.module_signal_processor.surv_ch_id = self.spinBox_surv_ch_select.value()

        # Peak hold setting
        if self.checkBox_en_peakhold.checkState():
            self.en_peakhold = True
        else:
            self.en_peakhold = False

    def set_resync_time(self):
        self.module_signal_processor.resync_time = self.spinBox_resync_time.value()


    def pb_close_clicked(self):
        #self.stop_streaming()
        #self.module_receiver.module_state = "EXIT"
        self.module_receiver.close()
        self.DOA_res_fd.close()
        self.close()


    def pb_proc_control_clicked(self):
        if self.pushButton_proc_control.text() == "Start processing":
            self.pushButton_proc_control.setText("Stop processing")


            self.module_signal_processor.start()

        elif self.pushButton_proc_control.text() == "Stop processing":
            self.pushButton_proc_control.setText("Start processing")

            self.module_signal_processor.stop()

    def pb_sync_clicked(self):
        #print("[ INFO ] Sync requested")
        self.module_signal_processor.en_sample_offset_sync=True

    def pb_calibrate_iq_clicked(self):
        #print("[ INFO ] IQ calibration requested")
        self.module_signal_processor.en_calib_iq=True
    def pb_calibrate_DOA_90_clicked(self):
        #print("[ INFO ] DOA IQ calibration requested")
        self.module_signal_processor.en_calib_DOA_90=True

    def pb_del_sync_history_clicked(self):
        self.module_signal_processor.delete_sync_history()

    def power_level_update(self, over_drive_flag):
        if over_drive_flag:
            red_text = "<span style=\" font-size:8pt; font-weight:600; color:#ff0000;\" >"
            red_text += "OVERDRIVE"
            red_text += ("</span>")
            self.label_power_level.setText(red_text)
        else:
            green_text = "<span style=\" font-size:8pt; font-weight:600; color:#01df01;\" >"
            green_text += "OK"
            green_text += ("</span>")
            self.label_power_level.setText(green_text)
    def period_time_update(self, update_period):
        if update_period > 1:
            self.label_update_rate.setText("%.1f s" %update_period)
        else:
            self.label_update_rate.setText("%.1f ms" %(update_period*1000))
    def spectrum_plot(self):
        xw1 = self.module_signal_processor.spectrum[1,:]
        xw2 = self.module_signal_processor.spectrum[2,:]
        xw3 = self.module_signal_processor.spectrum[3,:]
        xw4 = self.module_signal_processor.spectrum[4,:]
        freqs = self.module_signal_processor.spectrum[0,:]
        spectrum_dynamic_range = 10

        self.spectrum_ch1_curve.setData(freqs, xw1)
        self.spectrum_ch2_curve.setData(freqs, xw2)
        self.spectrum_ch3_curve.setData(freqs, xw3)
        self.spectrum_ch4_curve.setData(freqs, xw4)

        currentTime = time.time()
        if((currentTime - self.spectrum_time) > 0.5):
            self.spectrum_time = currentTime
            self.export_spectrum.export('/ram/spectrum.jpg')

    def delay_plot(self):

        xcorr12 = 10*np.log10(np.abs(self.module_signal_processor.xcorr[0,:]))
        xcorr13 = 10*np.log10(np.abs(self.module_signal_processor.xcorr[1,:]))
        xcorr14 = 10*np.log10(np.abs(self.module_signal_processor.xcorr[2,:]))

        phasor12 =self.module_signal_processor.phasors[0,:]
        phasor13 =self.module_signal_processor.phasors[1,:]
        phasor14 =self.module_signal_processor.phasors[2,:]

        N = np.size(xcorr12)//2

        xcorr12 -= np.max(xcorr12)
        xcorr13 -= np.max(xcorr13)
        xcorr14 -= np.max(xcorr14)

        #phasor12 /= np.max(np.abs(phasor12))
        #phasor13 /= np.max(np.abs(phasor13))
        #phasor14 /= np.max(np.abs(phasor14))

        M = 500
        max_delay = np.max(np.abs(self.module_signal_processor.delay_log[:,-1]))
        if max_delay+50 > M:
            M=max_delay+50

        delay_label = np.arange(-M,M+1,1)

#        if(xcorr12[0] != 0 and xcorr13[0] != 0 and xcorr14[0] != 0):
        self.plotWidget_sync_absx.clear()

        self.plotWidget_sync_absx.plot(delay_label, xcorr12[N-M:N+M+1], pen=(255, 199, 15))
        self.plotWidget_sync_absx.plot(delay_label, xcorr13[N-M:N+M+1], pen='r')
        self.plotWidget_sync_absx.plot(delay_label, xcorr14[N-M:N+M+1], pen='g')

        # Plot delay history

        self.plotWidget_sync_sampd.clear()

        self.plotWidget_sync_sampd.plot(self.module_signal_processor.delay_log[0,:], pen=(255, 199, 15))
        self.plotWidget_sync_sampd.plot(self.module_signal_processor.delay_log[1,:], pen='r')
        self.plotWidget_sync_sampd.plot(self.module_signal_processor.delay_log[2,:], pen='g')


        # Plot phasors
        # For averaged phasors
        #self.plotWidget_sync_normph.clear()
        #self.plotWidget_sync_normph.plot(np.cos(np.deg2rad(self.module_signal_processor.phase_log[0,:])), np.sin(np.deg2rad(self.module_signal_processor.phase_log[0,:])), pen=None, symbol='o', symbolBrush=(100,100,255,50))
        #self.plotWidget_sync_normph.plot(np.cos(np.deg2rad(self.module_signal_processor.phase_log[0,:])), np.sin(np.deg2rad(self.module_signal_processor.phase_log[0,:])), pen=None, symbol='o', symbolBrush=(150,150,150,50))
        #self.plotWidget_sync_normph.plot(np.cos(np.deg2rad(self.module_signal_processor.phase_log[0,:])), np.sin(np.deg2rad(self.module_signal_processor.phase_log[0,:])), pen=None, symbol='o', symbolBrush=(50,50,50,50))

        # Plot phase history

        self.plotWidget_sync_phasediff.clear()

        self.plotWidget_sync_phasediff.plot(self.module_signal_processor.phase_log[0,:], pen=(255, 199, 15))
        self.plotWidget_sync_phasediff.plot(self.module_signal_processor.phase_log[1,:], pen='r')
        self.plotWidget_sync_phasediff.plot(self.module_signal_processor.phase_log[2,:], pen='g')

        currentTime = time.time()
        if((currentTime - self.sync_time) > 0.5):
            self.sync_time = currentTime
            self.export_sync.export('/ram/sync.jpg')


    def DOA_plot_helper(self, DOA_data, incident_angles, log_scale_min=None, color=(255, 199, 15), legend=None):

        DOA_data = np.divide(np.abs(DOA_data), np.max(np.abs(DOA_data))) # normalization
        if(log_scale_min != None):
            DOA_data = 10*np.log10(DOA_data)
            theta_index = 0
            for theta in incident_angles:
                if DOA_data[theta_index] < log_scale_min:
                    DOA_data[theta_index] = log_scale_min
                theta_index += 1

        plot = self.plotWidget_DOA.plot(incident_angles, DOA_data, pen=pg.mkPen(color, width=2))
        return DOA_data


    def DOA_plot(self):

        thetas =  self.module_signal_processor.DOA_theta
        Bartlett  = self.module_signal_processor.DOA_Bartlett_res
        Capon  = self.module_signal_processor.DOA_Capon_res
        MEM  = self.module_signal_processor.DOA_MEM_res
        MUSIC  = self.module_signal_processor.DOA_MUSIC_res

        DOA = 0
        DOA_results = []
        COMBINED = np.zeros_like(thetas, dtype=np.complex)

        self.plotWidget_DOA.clear()

        if self.module_signal_processor.en_DOA_Bartlett:

            plt = self.DOA_plot_helper(Bartlett, thetas, log_scale_min = -50, color=(255, 199, 15))
            COMBINED += np.divide(np.abs(Bartlett),np.max(np.abs(Bartlett)))
            #de.DOA_plot(Bartlett, thetas, log_scale_min = -50, axes=self.axes_DOA)
            DOA_results.append(thetas[np.argmax(Bartlett)])

        if self.module_signal_processor.en_DOA_Capon:

            self.DOA_plot_helper(Capon, thetas, log_scale_min = -50, color='g')
            COMBINED += np.divide(np.abs(Capon),np.max(np.abs(Capon)))
            #de.DOA_plot(Capon, thetas, log_scale_min = -50, axes=self.axes_DOA)
            DOA_results.append(thetas[np.argmax(Capon)])

        if self.module_signal_processor.en_DOA_MEM:

            self.DOA_plot_helper(MEM, thetas, log_scale_min = -50, color='r')
            COMBINED += np.divide(np.abs(MEM),np.max(np.abs(MEM)))
            #de.DOA_plot(MEM, thetas, log_scale_min = -50, axes=self.axes_DOA)
            DOA_results.append(thetas[np.argmax(MEM)])

        if self.module_signal_processor.en_DOA_MUSIC:

            self.DOA_plot_helper(MUSIC, thetas, log_scale_min = -50, color=(9, 237, 237))
            COMBINED += np.divide(np.abs(MUSIC),np.max(np.abs(MUSIC)))
            #de.DOA_plot(MUSIC, thetas, log_scale_min = -50, axes=self.axes_DOA)
            DOA_results.append(thetas[np.argmax(MUSIC)])


        #COMBINED_LOG = 10*np.log10(COMBINED)

        if len(DOA_results) != 0:

            # Combined Graph (beta)
            COMBINED_LOG = self.DOA_plot_helper(COMBINED, thetas, log_scale_min = -50, color=(163, 64, 245))

            confidence = scipy.signal.find_peaks_cwt(COMBINED_LOG, np.arange(10,30), min_snr=1) #np.max(DOA_combined**2) / np.average(DOA_combined**2)
            maxIndex = confidence[np.argmax(COMBINED_LOG[confidence])]
            confidence_sum = 0;

            #print("Peaks: " + str(confidence))
            for val in confidence:
               if(val != maxIndex and np.abs(COMBINED_LOG[val] - min(COMBINED_LOG)) > np.abs(min(COMBINED_LOG))*0.25):
                  #print("Doing other peaks: " + str(val) + "combined value: " + str(COMBINED_LOG[val]))
                  confidence_sum += 1/(np.abs(COMBINED_LOG[val]))
               elif val == maxIndex:
                  #print("Doing maxIndex peak: " + str(maxIndex) + "min combined: " + str(min(COMBINED_LOG)))
                  confidence_sum += 1/np.abs(min(COMBINED_LOG))
            # Get avg power level
            max_power_level = np.max(self.module_signal_processor.spectrum[1,:])
            #rms_power_level = np.sqrt(np.mean(self.module_signal_processor.spectrum[1,:]**2))

            confidence_sum = 10/confidence_sum

            #print("Max Power Level" + str(max_power_level))
            #print("Confidence Sum: " + str(confidence_sum))

            DOA_results = np.array(DOA_results)
            # Convert measured DOAs to complex numbers
            DOA_results_c = np.exp(1j*np.deg2rad(DOA_results))
            # Average measured DOA angles
            DOA_avg_c = np.average(DOA_results_c)
            # Convert back to degree
            DOA = np.rad2deg(np.angle(DOA_avg_c))

            # Update DOA results on the compass display
            #print("[ INFO ] Python GUI: DOA results :",DOA_results)
            if DOA < 0:
                DOA += 360
            #DOA = 360 - DOA
            DOA_str = str(int(DOA))
            html_str = "<DATA>\n<DOA>"+DOA_str+"</DOA>\n<CONF>"+str(int(confidence_sum))+"</CONF>\n<PWR>"+str(np.maximum(0, max_power_level))+"</PWR>\n</DATA>"
            self.DOA_res_fd.seek(0)
            self.DOA_res_fd.write(html_str)
            self.DOA_res_fd.truncate()
            #print("[ INFO ] Python GUI: DOA results writen:",html_str)

        #self.DOA_res_fd.close()

        currentTime = time.time()
        if((currentTime - self.DOA_time) > 0.5):
            self.DOA_time = currentTime
            self.export_DOA.export('/ram/doa.jpg')



    def RD_plot(self):
        """
        Event type: Surveillance processor module has calculated the new range-Doppler matrix
        callback description:
        ------------------
            Plot the previously obtained range-Doppler matrix
        """
        # If Automatic detection is disabled the range-Doppler matrix is plotted otherwise the matrix
        if not self.checkBox_en_autodet.checkState():

            # Set colormap TODO: Implement this properly
            colormap = cm.get_cmap("jet")
            colormap._init()
            lut = (colormap._lut * 255).view(np.ndarray)
            self.img_PR.imageItem.setLookupTable(lut)

            CAFMatrix = self.module_signal_processor.RD_matrix
            CAFMatrix = np.abs(CAFMatrix)
            CAFDynRange = self.spinBox_rd_dyn_range.value()

            #print("Max Val" + str(np.amax(CAFMatrix)))
            #print("X-Size" + str(np.shape(CAFMatrix)[0]))
            #print("Y-Size" + str(np.shape(CAFMatrix)[1]))

            #try:
            #except:
            #    print("first time")


            CAFMatrix = CAFMatrix  /  np.amax(CAFMatrix)  # Noramlize with the maximum value

            # Peak hold for PR
            if self.en_peakhold:
                CAFMatrixNew = np.maximum(self.CAFMatrixOld, CAFMatrix) #1 * self.CAFMatrixOld + 1 * CAFMatrix
                self.CAFMatrixOld = CAFMatrixNew
                CAFMatrix = CAFMatrixNew
            else:
                self.CAFMatrixOld = CAFMatrix                

            CAFMatrixLog = 20 * np.log10(CAFMatrix)  # Change to logscale




            CAFMatrixLog[CAFMatrixLog < -CAFDynRange] = -CAFDynRange

#            for i in range(np.shape(CAFMatrix)[0]):  # Remove extreme low values
#                for j in range(np.shape(CAFMatrix)[1]):
#                    if CAFMatrixLog[i, j] < -CAFDynRange:
#                        CAFMatrixLog[i, j] = -CAFDynRange

            # plot
            #CAFPlot = self.axes_RD.imshow(CAFMatrixLog, interpolation='sinc', cmap='jet', origin='lower', aspect='auto')
            plotPRImage = scipy.ndimage.zoom(CAFMatrixLog, self.PR_interp_factor, order=3)
            self.img_PR.clear()
            self.img_PR.setImage(plotPRImage)


        else:
            # Set colormap TODO: Implement this properly
            colormap = cm.get_cmap("gray")
            colormap._init()
            lut = (colormap._lut * 255).view(np.ndarray)
            self.img_PR.imageItem.setLookupTable(lut)
            CAFMatrix = self.module_signal_processor.hit_matrix
            plotPRImage = scipy.ndimage.zoom(CAFMatrix, self.PR_interp_factor, order=3)
            self.img_PR.clear()
            self.img_PR.setImage(plotPRImage)

        currentTime = time.time()
        if((currentTime - self.PR_time) > 0.5):
            self.PR_time = currentTime
            self.export_PR.export(toBytes=True).save('/ram/pr.jpg', quality=30)

        # Set doppler speed Y-AXIS
        max_Doppler = int(self.doubleSpinBox_cc_det_max_Doppler.value())
        ay = self.plt_PR.getAxis('left')
        matrix_ySize = np.shape(plotPRImage)[0]
        ay.setTicks([[(0, -max_Doppler), (matrix_ySize * 0.25, -max_Doppler * 0.5), (matrix_ySize/2, 0), (matrix_ySize * 0.75, max_Doppler * 0.5), (matrix_ySize, max_Doppler)], []])


app = QApplication(sys.argv)
form = MainWindow()
form.show()

def init_settings():

    # Receiver Configuration
    center_freq = settings.center_freq
    samp_index = settings.samp_index
    uniform_gain = settings.uniform_gain
    gain_index = settings.gain_index
    gain_index_2 = settings.gain_index_2
    gain_index_3 = settings.gain_index_3
    gain_index_4 = settings.gain_index_4

    form.doubleSpinBox_center_freq.setProperty("value", center_freq)
    form.comboBox_sampling_freq.setCurrentIndex(int(samp_index))
    form.checkBox_en_uniform_gain.setChecked(True if uniform_gain=="on" else False)
    form.comboBox_gain.setCurrentIndex(int(gain_index))
    form.comboBox_gain_2.setCurrentIndex(int(gain_index))
    form.comboBox_gain_3.setCurrentIndex(int(gain_index))
    form.comboBox_gain_4.setCurrentIndex(int(gain_index))


    # IQ Preprocessing
    dc_comp = settings.dc_comp
    filt_bw = settings.filt_bw
    fir_size = settings.fir_size
    decimation = settings.decimation

    form.checkBox_en_dc_compensation.setChecked(True if dc_comp=="on" else False)
    form.doubleSpinBox_filterbw.setProperty("value", filt_bw)
    form.spinBox_fir_tap_size.setProperty("value", fir_size)
    form.spinBox_decimation.setProperty("value", decimation)


    # Sync
    en_sync = "off" #settings.en_sync
    en_noise = "off" #settings.en_noise

    form.checkBox_en_sync_display.setChecked(True if en_sync=="on" else False)
    form.checkBox_en_noise_source.setChecked(True if en_noise=="on" else False)


    # DOA Estimation
    ant_arrangement_index = settings.ant_arrangement_index
    ant_spacing = settings.ant_spacing
    en_doa = "off" #settings.en_doa
    en_bartlett = settings.en_bartlett
    en_capon = settings.en_capon
    en_MEM = settings.en_MEM
    en_MUSIC = settings.en_MUSIC
    en_fbavg = settings.en_fbavg

    form.comboBox_antenna_alignment.setCurrentIndex(int(ant_arrangement_index))
    form.doubleSpinBox_DOA_d.setProperty("value", ant_spacing)
    form.checkBox_en_DOA.setChecked(True if en_doa=="on" else False)
    form.checkBox_en_DOA_Bartlett.setChecked(True if en_bartlett=="on" else False)
    form.checkBox_en_DOA_Capon.setChecked(True if en_capon=="on" else False)
    form.checkBox_en_DOA_MEM.setChecked(True if en_MEM=="on" else False)
    form.checkBox_en_DOA_MUSIC.setChecked(True if en_MUSIC=="on" else False)
    form.checkBox_en_DOA_FB_avg.setChecked(True if en_fbavg=="on" else False)


    # Passive Radar
    en_pr = "off" #settings.en_pr
    ref_ch = settings.ref_ch
    surv_ch = settings.surv_ch
    en_clutter = settings.en_clutter
    filt_dim = settings.filt_dim
    max_range = settings.max_range
    max_doppler = settings.max_doppler
    windowing_mode = settings.windowing_mode
    dyn_range = settings.dyn_range
    en_det = settings.en_det
    est_win = settings.est_win
    guard_win = settings.guard_win
    thresh_det = settings.thresh_det
    en_peakhold = settings.en_peakhold

    form.checkBox_en_passive_radar.setChecked(True if en_pr=="on" else False)
    form.spinBox_ref_ch_select.setProperty("value", ref_ch)
    form.spinBox_surv_ch_select.setProperty("value", surv_ch)
    form.checkBox_en_td_filter.setChecked(True if en_clutter=="on" else False)
    form.spinBox_td_filter_dimension.setProperty("value", filt_dim)
    form.doubleSpinBox_cc_det_max_range.setProperty("value", max_range)
    form.doubleSpinBox_cc_det_max_Doppler.setProperty("value", max_doppler)
    form.comboBox_cc_det_windowing.setCurrentIndex(int(windowing_mode))
    form.spinBox_rd_dyn_range.setProperty("value", dyn_range)
    form.checkBox_en_autodet.setChecked(True if en_det=="on" else False)
    form.spinBox_cfar_est_win.setProperty("value", est_win)
    form.spinBox_cfar_guard_win.setProperty("value", guard_win)
    form.doubleSpinBox_cfar_threshold.setProperty("value", thresh_det)
    form.checkBox_en_peakhold.setChecked(True if en_peakhold=="on" else False)


def reboot_program():
    form.module_receiver.close()
    form.DOA_res_fd.close()
    subprocess.call(['./run.sh'])

#@route('/static/:path#.+#', name='static')
#def static(path):
    #return static_file(path, root='static')

@route('/static/<filepath:path>', name='static')
def server_static(filepath):
    return static_file(filepath, root='./static')


@get('/pr')
def pr():
    en_pr = form.checkBox_en_passive_radar.checkState()

    ref_ch = form.spinBox_ref_ch_select.value()
    surv_ch = form.spinBox_surv_ch_select.value()

    en_clutter = form.checkBox_en_td_filter.checkState()
    filt_dim = form.spinBox_td_filter_dimension.value()
    max_range = form.doubleSpinBox_cc_det_max_range.value()
    max_doppler = form.doubleSpinBox_cc_det_max_Doppler.value()

    windowing_mode = int(form.comboBox_cc_det_windowing.currentIndex())

    dyn_range = form.spinBox_rd_dyn_range.value()


    en_det = form.checkBox_en_autodet.checkState()

    est_win = form.spinBox_cfar_est_win.value()
    guard_win = form.spinBox_cfar_guard_win.value()
    thresh_det = form.doubleSpinBox_cfar_threshold.value()
    
    en_peakhold = form.checkBox_en_peakhold.checkState()

    ip_addr = form.ip_addr

    return template ('pr.tpl', {'en_pr':en_pr,
				'ref_ch':ref_ch,
				'surv_ch':surv_ch,
				'en_clutter':en_clutter,
				'filt_dim':filt_dim,
				'max_range':max_range,
				'max_doppler':max_doppler,
				'windowing_mode':windowing_mode,
				'dyn_range':dyn_range,
				'en_det':en_det,
				'est_win':est_win,
				'guard_win':guard_win,
				'thresh_det':thresh_det,
                                'en_peakhold':en_peakhold,
				'ip_addr':ip_addr})

@post('/pr')
def do_pr():
    en_pr = request.forms.get('en_pr')
    form.checkBox_en_passive_radar.setChecked(True if en_pr=="on" else False)

    ref_ch = request.forms.get('ref_ch')
    form.spinBox_ref_ch_select.setProperty("value", ref_ch)

    surv_ch = request.forms.get('surv_ch')
    form.spinBox_surv_ch_select.setProperty("value", surv_ch)

    en_clutter = request.forms.get('en_clutter')
    form.checkBox_en_td_filter.setChecked(True if en_clutter=="on" else False)

    filt_dim = request.forms.get('filt_dim')
    form.spinBox_td_filter_dimension.setProperty("value", filt_dim)

    max_range = request.forms.get('max_range')
    form.doubleSpinBox_cc_det_max_range.setProperty("value", max_range)

    max_doppler = request.forms.get('max_doppler')
    form.doubleSpinBox_cc_det_max_Doppler.setProperty("value", max_doppler)

    windowing_mode = request.forms.get('windowing_mode')
    form.comboBox_cc_det_windowing.setCurrentIndex(int(windowing_mode))

    dyn_range = request.forms.get('dyn_range')
    form.spinBox_rd_dyn_range.setProperty("value", dyn_range)

    en_det = request.forms.get('en_det')
    form.checkBox_en_autodet.setChecked(True if en_det=="on" else False)

    est_win = request.forms.get('est_win')
    form.spinBox_cfar_est_win.setProperty("value", est_win)

    guard_win = request.forms.get('guard_win')
    form.spinBox_cfar_guard_win.setProperty("value", guard_win)

    thresh_det = request.forms.get('thresh_det')
    form.doubleSpinBox_cfar_threshold.setProperty("value", thresh_det)
    
    en_peakhold = request.forms.get('en_peakhold')
    form.checkBox_en_peakhold.setChecked(True if en_peakhold=="on" else False)

    settings.en_pr = en_pr
    settings.ref_ch = ref_ch
    settings.surv_ch = surv_ch
    settings.en_clutter = en_clutter
    settings.filt_dim = filt_dim
    settings.max_range = max_range
    settings.max_doppler = max_doppler
    settings.windowing_mode = windowing_mode
    settings.dyn_range = dyn_range
    settings.en_det = en_det
    settings.est_win = est_win
    settings.guard_win = guard_win
    settings.thresh_det = thresh_det
    settings.en_peakhold = en_peakhold

    form.set_PR_params()

    settings.write()
    return redirect('pr')

@get('/doa')
def doa():
    ant_arrangement_index = int(form.comboBox_antenna_alignment.currentIndex())
    ant_meters = form.doubleSpinBox_DOA_d.value()
    en_doa = form.checkBox_en_DOA.checkState()
    en_bartlett = form.checkBox_en_DOA_Bartlett.checkState()
    en_capon = form.checkBox_en_DOA_Capon.checkState()
    en_MEM = form.checkBox_en_DOA_MEM.checkState()
    en_MUSIC = form.checkBox_en_DOA_MUSIC.checkState()
    en_fbavg = form.checkBox_en_DOA_FB_avg.checkState()
    ip_addr = form.ip_addr

    return template ('doa.tpl', {'ant_arrangement_index':ant_arrangement_index,
#				'ant_spacing':ant_spacing,
                'ant_meters' :ant_meters,
				'en_doa':en_doa,
				'en_bartlett':en_bartlett,
				'en_capon':en_capon,
				'en_MEM':en_MEM,
				'en_MUSIC':en_MUSIC,
				'en_fbavg':en_fbavg,
				'ip_addr':ip_addr})


@post('/doa')
def do_doa():
    ant_arrangement_index = request.forms.get('ant_arrangement')
    form.comboBox_antenna_alignment.setCurrentIndex(int(ant_arrangement_index))

    ant_spacing = request.forms.get('ant_spacing')
    form.doubleSpinBox_DOA_d.setProperty("value", ant_spacing)

    en_doa = request.forms.get('en_doa')
    form.checkBox_en_DOA.setChecked(True if en_doa=="on" else False)

    en_bartlett = request.forms.get('en_bartlett')
    form.checkBox_en_DOA_Bartlett.setChecked(True if en_bartlett=="on" else False)

    en_capon = request.forms.get('en_capon')
    form.checkBox_en_DOA_Capon.setChecked(True if en_capon=="on" else False)

    en_MEM = request.forms.get('en_MEM')
    form.checkBox_en_DOA_MEM.setChecked(True if en_MEM=="on" else False)

    en_MUSIC = request.forms.get('en_MUSIC')
    form.checkBox_en_DOA_MUSIC.setChecked(True if en_MUSIC=="on" else False)

    en_fbavg = request.forms.get('en_fbavg')
    form.checkBox_en_DOA_FB_avg.setChecked(True if en_fbavg=="on" else False)

    settings.ant_arrangement_index = ant_arrangement_index
    settings.ant_spacing = ant_spacing
    settings.en_doa = en_doa
    settings.en_bartlett = en_bartlett
    settings.en_capon = en_capon
    settings.en_MEM = en_MEM
    settings.en_MUSIC = en_MUSIC
    settings.en_fbavg = en_fbavg
    form.set_DOA_params()

    settings.write()
    return redirect('doa')


@get('/sync')
def sync():
    en_sync = form.checkBox_en_sync_display.checkState()
    en_noise = form.checkBox_en_noise_source.checkState()
    ip_addr = form.ip_addr
    return template ('sync.tpl', {'en_sync':en_sync,
				'en_noise':en_noise,
				'ip_addr':ip_addr})


@post('/sync')
def do_sync():

    if (request.POST.get('enable_all_sync') == 'enable_all_sync'):
        current_sync = form.checkBox_en_sync_display.checkState()
        current_noise = form.checkBox_en_noise_source.checkState()
        if (current_sync == False) and (current_noise == False):
            form.checkBox_en_sync_display.setChecked(True)
            form.checkBox_en_noise_source.setChecked(True)
        else:
            form.checkBox_en_sync_display.setChecked(False)
            form.checkBox_en_noise_source.setChecked(False)

        form.switch_noise_source()
        form.set_sync_params()

    if (request.POST.get('update_sync') == 'update_sync'):
        en_sync = request.forms.get('en_sync')
        form.checkBox_en_sync_display.setChecked(True if en_sync=="on" else False)

        en_noise = request.forms.get('en_noise')
        form.checkBox_en_noise_source.setChecked(True if en_noise=="on" else False)

        settings.en_sync = en_sync
        settings.en_noise = en_noise
        form.switch_noise_source()
        form.set_sync_params()

    if (request.POST.get('del_hist') == 'del_hist'):
        form.pb_del_sync_history_clicked()

    if (request.POST.get('samp_sync') == 'samp_sync'):
        form.pb_sync_clicked()

    if (request.POST.get('cal_iq') == 'cal_iq'):
        form.pb_calibrate_iq_clicked()

    settings.write()
    return redirect('sync')

@get('/')
@get('/init')
def init():
    center_freq = form.doubleSpinBox_center_freq.value()
    samp_index = int(form.comboBox_sampling_freq.currentIndex())
    uniform_gain = form.checkBox_en_uniform_gain.checkState()
    gain_index = int(form.comboBox_gain.currentIndex())
    gain_index_2 = int(form.comboBox_gain_2.currentIndex())
    gain_index_3 = int(form.comboBox_gain_3.currentIndex())
    gain_index_4 = int(form.comboBox_gain_4.currentIndex())
    dc_comp = form.checkBox_en_dc_compensation.checkState()
    filt_bw = form.doubleSpinBox_filterbw.value()
    fir_size = form.spinBox_fir_tap_size.value()
    decimation = form.spinBox_decimation.value()
    ip_addr = form.ip_addr

    return template ('init.tpl', {'center_freq':center_freq,
				'samp_index':samp_index,
                'uniform_gain':uniform_gain,
				'gain_index':gain_index,
				'gain_index_2':gain_index_2,
				'gain_index_3':gain_index_3,
				'gain_index_4':gain_index_4,
				'dc_comp':dc_comp,
				'filt_bw':filt_bw,
				'fir_size':fir_size,
				'decimation':decimation,
				'ip_addr':ip_addr})

@post('/init') # or @route('/login', method='POST')
def do_init():
    if (request.POST.get('rcv_params') == 'rcv_params'):
        center_freq = request.forms.get('center_freq')
        form.doubleSpinBox_center_freq.setProperty("value", center_freq)

        samp_index = request.forms.get('samp_freq')
        form.comboBox_sampling_freq.setCurrentIndex(int(samp_index))

        uniform_gain = request.forms.get('uniform_gain')
        form.checkBox_en_uniform_gain.setChecked(True if uniform_gain=="on" else False)

        if uniform_gain == "on":
            gain_index = request.forms.get('gain')
            form.comboBox_gain.setCurrentIndex(int(gain_index))
            gain_index_2 = request.forms.get('gain')
            form.comboBox_gain_2.setCurrentIndex(int(gain_index))
            gain_index_3 = request.forms.get('gain')
            form.comboBox_gain_3.setCurrentIndex(int(gain_index))
            gain_index_4 = request.forms.get('gain')
            form.comboBox_gain_4.setCurrentIndex(int(gain_index))
        else:
            gain_index = request.forms.get('gain')
            form.comboBox_gain.setCurrentIndex(int(gain_index))
            gain_index_2 = request.forms.get('gain_2')
            form.comboBox_gain_2.setCurrentIndex(int(gain_index_2))
            gain_index_3 = request.forms.get('gain_3')
            form.comboBox_gain_3.setCurrentIndex(int(gain_index_3))
            gain_index_4 = request.forms.get('gain_4')
            form.comboBox_gain_4.setCurrentIndex(int(gain_index_4))

        settings.center_freq = center_freq
        settings.samp_index = samp_index
        settings.uniform_gain = uniform_gain
        settings.gain_index = gain_index
        settings.gain_index_2 = gain_index_2
        settings.gain_index_3 = gain_index_3
        settings.gain_index_4 = gain_index_4
        form.pb_rec_reconfig_clicked()


    if (request.POST.get('iq_params') == 'iq_params'):
        dc_comp = request.forms.get('dc_comp')
        form.checkBox_en_dc_compensation.setChecked(True if dc_comp=="on" else False)

        filt_bw = request.forms.get('filt_bw')
        form.doubleSpinBox_filterbw.setProperty("value", filt_bw)

        fir_size = request.forms.get('fir_size')
        form.spinBox_fir_tap_size.setProperty("value", fir_size)

        decimation = request.forms.get('decimation')
        form.spinBox_decimation.setProperty("value", decimation)

        settings.dc_comp = dc_comp
        settings.filt_bw = filt_bw
        settings.fir_size = fir_size
        settings.decimation = decimation
        form.set_iq_preprocessing_params()

    if (request.POST.get('start') == 'start'):
        form.module_signal_processor.start()
        form.pushButton_proc_control.setText("Stop processing")

    if (request.POST.get('stop') == 'stop'):
        form.module_signal_processor.stop()
        form.pushButton_proc_control.setText("Start processing")

    if (request.POST.get('start_spec') == 'start_spec'):
        form.checkBox_en_spectrum.setChecked(True)
        form.set_spectrum_params()

    if (request.POST.get('stop_spec') == 'stop_spec'):
        form.checkBox_en_spectrum.setChecked(False)
        form.set_spectrum_params()

    if (request.POST.get('reboot') == 'reboot'):
        reboot_program()

    settings.write()

    return redirect('init')

@get('/stats')
def stats():

    upd_rate = form.label_update_rate.text()

    if(form.module_receiver.overdrive_detect_flag):
       ovr_drv = "YES"
    else:
       ovr_drv = "NO"

    return template ('stats.tpl', {'upd_rate':upd_rate,
				'ovr_drv':ovr_drv})

init_settings()
app.exec_()
