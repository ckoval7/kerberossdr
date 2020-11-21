<h3>Note:</h3>
You'll need to set your Station ID, Latitude, and Longitude in the `run.sh` file
or set the software to use gpsd.

<h4>Change Log</h4>

* Added gpsd integration. Gets location directly from the pi if a GPS receiver is plugged in. USB GPS receivers are surprisingly cheap.
    * You'll need the gpsd-py3 library. Run `pip3 install gpsd-py3`
    * edit the `LAT` and `LON` values in `run.sh` to say `"gpsd"`
    * If you are configuring a stationary receiver `HEADING` should reflect the orientation of your array.
    * If you are configuring a mobile receiver `HEADING` should say `"gpsd"`

* Added expanded XML format which can transmit location and heading data if supplied by the user. Added location and heading to run.sh.
    * This new format does not break app compatibility.

<h4>Ubuntu 20.04 Users NOTE:</h4>

The Qt5 Expanded XML version is available here: https://github.com/ckoval7/kerberossdr/tree/PyQt5_Extended_XML
* `git clone https://github.com/ckoval7/kerberossdr.git`
* `cd kerberossdr`
* `git checkout PyQt5_Extended_XML`

<h3>Please see the software tutorial at www.rtl-sdr.com/ksdr</h3>

<h2>KerberosSDR Demo Software</h2>

<h3>Installing the software</h3>

1. <h4>Install Dependencies via apt:</h4>

  `sudo apt update`<br>
  `sudo apt install python3-pip python3-pyqt4 pyqt4-dev-tools build-essential gfortran libatlas3-base libatlas-base-dev python3-dev python3-setuptools libffi6 libffi-dev python3-tk pkg-config libfreetype6-dev php7.2-cli`

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

  `git clone https://github.com/rtlsdrblog/kerberossdr`<br>
  `cd kerberossdr`<br>
  `sh setup_init.sh`

8. <h4>Now you can run the software by typing</h4>

  `./run.sh`

Full software tutorial at www.rtl-sdr.com/ksdr

TROUBLESHOOTING:

Edit the run.sh file and comment out the >&/dev/null parts on the last line to show any errors to the terminal.


This software was 95% developed by Tamas Peto, and makes use of his pyAPRIL and pyARGUS libraries. See his website at www.tamaspeto.com
