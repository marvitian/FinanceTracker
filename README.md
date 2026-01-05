# Environment setup #

after checkout, create a virtual environment and install tk calendar. 
Note: python version shouldn't matter
```
python3 -m venv venv
source venv/bin/activate
pip install tkcalendar
```

tkinter comes with python, so if moduleNotFoundException is thrown, it is indicative that your environment is not configured correctly. 
This issue was found with WSL Ubuntu. 

Fix: 
```
sudo apt update
sudo apt install python3-tk
```

check:
```
python3 -m tkinter
```
if a window opens, it's fixed
