sudo apt update
sudo apt install -y --no-install-recommends python3-pip
pip3 install -r requirements.txt --no-cache-dir
CONFIG=`echo $CONFIG_B64 | base64 -d` python3 XMUAutoCheckIn.py