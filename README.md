<h3>Note:</h3>
You'll need to set your Station ID, Latitude, and Longitude in the `run.sh` file or set the software to use gpsd.

<h4>Change Log</h4>

* Added gpsd integration. Gets location directly from the pi if a GPS receiver is plugged in. USB GPS receivers are surprisingly cheap.
    * [Set up gpsd per your OS's Instructions](https://gpsd.gitlab.io/gpsd/installation.html)
    * You'll need the gpsd-py3 library. Run `pip3 install gpsd-py3`
    * edit the `LAT` and `LON` values in `run.sh` to say `"gpsd"`
    * If you are configuring a stationary receiver `HEADING` should reflect the orientation of your array.
    * If you are configuring a mobile receiver `HEADING` should say `"gpsd"`

* Added expanded XML format which can transmit location and heading data if supplied by the user. Added location and heading to run.sh.
    * This new format does not break app compatibility.

* The purpose of this branch is to get ksdr working in the latest kubuntu (and Ubuntu) based linux, which use different libraries (PyQt5 and libffi7). This branch is currently in testing status, but I have successfully gotten it working in both Ubuntu 20.04 LTS and kubuntu 20.04 LTS.
* This branch is meant for, and only works in, Ubuntu + kubunu versions 20.04 LTS. It does not work on older linux versions.
* ***Note for smaller display areas: There seems to be an issue on machines that do not support higher display resolutions. The Kerberossdr window will not resize properly if the display doesn't support a resolution with a height above around 960 (e.g 1280x960 was the minimum I could get the whole window visible with). This shouldn't be a problem on most newer desktops and higher end laptops but since a lot of laptops only support 1366x768 this is an issue for those. While this issue is present in the original kerberossdr software on Ubuntu 18.04/PyQt4, the level of screen clipping is, it seems, more pronounced on 20.04/PyQt5 and you cant get to the "Start Processing button" where you could at least get to that on 18.04/PyQt4.***
* The installation instructions below have been updated for installing PyQt5 and libffi7, which are compatable with the new Linux releases instead of PyQt4 and libffi6.
* A little background in case you run into problems so you will know what I did to get this working (if you want to go to the original rtl-sdr blog github repository and make the changes manually). Basically, the only changes needed in the Python code were to import PyQt5 where ever PyQt4 was imported  (using slightly different syntax than PyQt4, you cant just change PyQt4 to PyQt5, see  _GUI/hydra_main_window.py for an example). The files that needed the PyQt5 import changes were: _GUI/hydra_main_window.py, _signalProcessing/hydra_signal_processor.py and in _GUI/hydra_main_window_layout.py. Then, find/replaced all the instances of .setMargin(0) to .setContentsMargins(0,0,0,0) in the _GUI/hydra_main_window_layout.py file. Finally, I updated the install instructions to get rid of Pyqt4 and use PyQt5, and then changed libffi6 to libffi7.


The Qt5 Expanded XML version is available here: https://github.com/ckoval7/kerberossdr/tree/PyQt5_Extended_XML
* `git clone https://github.com/ckoval7/kerberossdr.git`
* `cd kerberossdr`
* `git checkout PyQt5_Extended_XML`

<h3>Please see the software tutorial at www.rtl-sdr.com/ksdr</h3>

<h2>KerberosSDR Demo Software</h2>

<h3>Installing the software</h3>

1. <h4>Install Dependencies via apt:</h4>

  `sudo apt update`<br>
  `sudo apt install python3-pip build-essential gfortran libatlas3-base libatlas-base-dev python3-dev python3-setuptools libffi-dev python3-tk pkg-config libfreetype6-dev php-cli wondershaper python3-pyqt5 libffi7`

2. <h4>Uninstall any preinstalled numpy packages as we want to install with pip3 to get optimized BLAS.</h4>

  `sudo apt remove python3-numpy`

3. <h4>Install Dependencies via pip3:</h4>

  `pip3 install gpsd-py3 numpy matplotlib scipy cairocffi pyapril pyargus pyqtgraph peakutils bottle paste`

4. <h4>Install RTL-SDR-Kerberos Drivers</h4>

  Our Kerberos RTL-SDR driver branch contains code for slightly modified Osmocom RTL-SDR drivers that enable GPIO, disable dithering, and disable zerocopy buffers which seems to cause trouble on some ARM devices.

  `sudo apt-get install libusb-1.0-0-dev git cmake`<br>

  `git clone https://github.com/rtlsdrblog/rtl-sdr-kerberos`<br>

  `cd rtl-sdr-kerberos`<br>
  `mkdir build`<br>
  `cd build`<br>
  `cmake ../ -DINSTALL_UDEV_RULES=ON`<br>
  `make`<br>
  `sudo make install`<br>
  `sudo cp ../rtl-sdr.rules /etc/udev/rules.d/`<br>
  `sudo ldconfig`<br>

  `echo 'blacklist dvb_usb_rtl28xxu' | sudo tee --append /etc/modprobe.d/blacklist-dvb_usb_rtl28xxu.conf`

5. <h4>Reboot the Pi.</h4>

6. <h4>Test 4x Tuners</h4>

  At this stage we recommend first testing your four tuners with rtl_test. Open four terminal windows, or tabs, and in each window run "rtl_test -d 0", "rtl_test -d 1", "rtl_test -d 2" and "rtl_test -d 3". Ensure that each unit connects and displays no errors.
Install KerberosSDR Demo Software

7. <h4>Clone or unzip the software</h4>

  `git clone https://github.com/rfjohnso/kerberossdr`<br>
  `cd kerberossdr`<br>
  `sh setup_init.sh`

8. <h4>Now you can run the software by typing</h4>

  `./run.sh`

Full software tutorial at www.rtl-sdr.com/ksdr

TROUBLESHOOTING:

Edit the run.sh file and comment out the >&/dev/null parts on the last line to show any errors to the terminal.


This software was 95% developed by Tamas Peto, and makes use of his pyAPRIL and pyARGUS libraries. See his website at www.tamaspeto.com
