#！/bin/bash
#source /home/sigurd/miniconda3/bin/activate
Xvfb :99 -ac -screen 0 1280x1024x24 & 
export DISPLAY=:99
python3 /home/sigurd/Scripts/XMUAutoCheckIn/XMUAutoCheckIn.py
