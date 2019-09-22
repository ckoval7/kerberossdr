Don't use the "dev" branch, it usually has untested code.

<h4>This fork adds a few GUI and Web UI improvements and convenience features:</h4>

* Selecting “Uniform Gain” will allow you to set the same gain value for all four receivers.
* The antenna spacing value (s, fraction of wavelength) is automatically calculated based on frequency and a user set antenna spacing (s’, meters). For circular arrays, just use the spacing between each antenna, the program will calculate the radius for you.
* I’ve added a button to the Web UI to enable the sync display and the noise source in one click. If the noise source or the sync display (or both) is enabled the button will disable both. This should make calibration less cumbersome on mobile devices.
* I've added CSS to the Web UI. This will allow for easy customization of the layout and adds a mobile friendly flare. Feel free to edit ./static/style.css to your liking.
* The graphs hurt less to look at.
* Fixed the backwards compass reading in JavaScript. This is just a bandaid. The reading should be fixed at the origin and the Android App updated to take the correct reading.



<h3>Please see the software tutorial at www.rtl-sdr.com/ksdr</h3>

<h2>KerberosSDR Demo Software</h2>

<h3>Installing the software</h3>

1. <h4>Install Dependencies via apt:</h4>

  `sudo apt update
sudo apt install python3-pip python3-pyqt4 build-essential gfortran libatlas3-base libatlas-base-dev python3-dev python3-setuptools libffi6 libffi-dev python3-tk pkg-config libfreetype6-dev php7.2-cli`

2. <h4>Uninstall any preinstalled numpy packages as we want to install with pip3 to get optimized BLAS.</h4>

  `sudo apt remove python3-numpy`

3. <h4>Install Dependencies via pip3:</h4>

  `pip3 install numpy
pip3 install matplotlib
pip3 install scipy
pip3 install cairocffi
pip3 install pyapril
pip3 install pyargus
pip3 install pyqtgraph
pip3 install peakutils
pip3 install bottle
pip3 install paste`

4. <h4>Install RTL-SDR-Kerberos Drivers</h4>

  Our Kerberos RTL-SDR driver branch contains code for slightly modified Osmocom RTL-SDR drivers that enable GPIO, disable dithering, and disable zerocopy buffers which seems to cause trouble on some ARM devices.

  `sudo apt-get install libusb-1.0-0-dev git cmake`

  `git clone https://github.com/rtlsdrblog/rtl-sdr-kerberos`

  `cd rtl-sdr-kerberos
mkdir build
cd build
cmake ../ -DINSTALL_UDEV_RULES=ON
make
sudo make install
sudo cp ../rtl-sdr.rules /etc/udev/rules.d/
sudo ldconfig`

  `echo 'blacklist dvb_usb_rtl28xxu' | sudo tee --append /etc/modprobe.d/blacklist-dvb_usb_rtl28xxu.conf`

5. <h4>Reboot the Pi.</h4>

6. <h4>Test 4x Tuners</h4>

  At this stage we recommend first testing your four tuners with rtl_test. Open four terminal windows, or tabs, and in each window run "rtl_test -d 0", "rtl_test -d 1", "rtl_test -d 2" and "rtl_test -d 3". Ensure that each unit connects and displays no errors.
Install KerberosSDR Demo Software

7. <h4>Clone or unzip the software</h4>

  `git clone https://github.com/rtlsdrblog/kerberossdr
sh setup_init.sh`

8. <h4>Now you can run the software by typing</h4>

  `./run.sh`

Full software tutorial at www.rtl-sdr.com/ksdr

TROUBLESHOOTING:

Edit the run.sh file and comment out the >&/dev/null parts on the last line to show any errors to the terminal.


This software was 95% developed by Tamas Peto, and makes use of his pyAPRIL and pyARGUS libraries. See his website at www.tamaspeto.com
