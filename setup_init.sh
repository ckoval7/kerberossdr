#/bin/bash!

echo "Compile C files"
(cd _receiver/C && make)

echo "[ INFO ] Set file executation rights"
chmod a+x _receiver/C/rtl_daq
chmod a+x _receiver/C/sim
chmod a+x _receiver/C/sync
chmod a+x _receiver/C/gate

sudo chmod +x run.sh
sudo chmod +x kill.sh

sudo mkdir -p /ram

sudo ln -sf /ram/pr.jpg _webDisplay/pr.jpg
sudo ln -sf /ram/DOA_value.html _webDisplay/DOA_value.html
sudo ln -sf /ram/spectrum.jpg _webDisplay/spectrum.jpg
sudo ln -sf /ram/sync.jpg _webDisplay/sync.jpg
sudo ln -sf /ram/doa.jpg _webDisplay/doa.jpg
sudo ln -sf /ram/pr.jpg _webDisplay/pr.jpg
