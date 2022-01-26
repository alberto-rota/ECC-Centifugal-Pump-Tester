# Copyright (c) 2022 Alberto Rota
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>.

from gui.GUI import *
from serial import Serial
import numpy as np
#import tensorflow as tf
import json
import datetime as dt
import os, sys
#tfk = tf.keras

import tensorflow.keras.models
###################################################################
# CONFIG
###################################################################
with open(os.path.join("config","config.json")) as configfile:
    config=json.load(configfile)
    
FIG_WIDTH =config["FIG_WIDTH"]
FIG_HEIGHT = config["FIG_HEIGHT"]
BORDERS = config["BORDERS"]

TIMESPAN = config["TIMESPAN"]
MAXY = config["MAXY"]

DEVICE_NAME = config["DEVICE_NAME"]
BAUDRATE=config["BAUDRATE"]
DELAY=config["DELAY"]
###################################################################


###################################################################
# INITIALIZATIONS
###################################################################
serialok = False
recording = False
data = np.empty((1,6))  # Holds the plotted data
model = tensorflow.keras.models.load_model(config["model_path"])
###################################################################


def start_plot():
    global recording
    recording = True
    if s is not None: s.reset_input_buffer()
    gui.update_classification_label()
    global x
    x = np.empty((1,6)) # Holds the recorded data
    gui.give_saved_alert(restarting = True)
    
def stop_plot():
    if s is not None: s.reset_input_buffer()
    
    global recording
    WINDOW_SIZE = 125
    STRIDE = 25
    WORKING_SENSORS = [1,2,3,4,5,6]
    WORKING_SENSORS = [ws-1 for ws in WORKING_SENSORS]
    if recording:
        if x.shape[0]>WINDOW_SIZE:
            
            windows = [x[i:i+WINDOW_SIZE,WORKING_SENSORS] for i in range(0,x.shape[0]-WINDOW_SIZE,STRIDE)]
            windows=(windows-np.expand_dims(np.mean(windows,axis=1),axis=1))/np.expand_dims(np.std(windows,axis=1),axis=1)
            # windows = np.stack(windows)/3300
            
            print(windows)
            
            outs = model.predict(windows)

            pred = np.mean(outs.T)

            if pred>0.5:
                gui.update_classification_label("NC",2*abs(pred-0.5))
            else:
                gui.update_classification_label("NC",2*abs(pred-0.5))
                
    recording = False
    updatedconfig = gui.update_config()
    with open(os.path.join("config","config.json"), 'w') as configfile:
        json.dump(updatedconfig, configfile,indent=4)
    # gui.clear_chart()
    # global data
    # data = np.empty((1,6))
    
    
def save_data():
    global x
    if x.shape[0]>50 and not recording:
        with open(os.path.join("config","config.json")) as configfile:
            config=json.load(configfile)
        fname = os.path.join(
            config["savepath"],
            dt.datetime.now().strftime("%d%m%Y_%H%M%S")+config["append"],
            )
        np.savetxt(fname+".csv", data, delimiter=",")
        gui.give_saved_alert(restarting = False,lines=data.shape[0],path=fname+".csv")
    
buttons_callbacks = {
    "start": start_plot,
    "stop": stop_plot,
    "save": save_data,
}

def plot_signals():
    global recording
    global data
    global s
    global timestamp
    global serialok
    global x
        
    # Tries to reconnect if no serial device is attached
    if not serialok:
        # Checks if a device is found among the ports and, if so, saves the PORT
        ports = serial.tools.list_ports.comports(include_links=False)
        for p in ports: 
            if p.description == DEVICE_NAME:
                PORT = p.device
                
        # Tries to connect to detected port
        try:
            s = Serial(PORT, BAUDRATE,timeout=0.01)
            s.reset_input_buffer();
        except:
            s = None
            
    # Checks if connection happened
    serialok = gui.check_serialcomm(s,DEVICE_NAME,BAUDRATE)
        
    # If serial is connected and user pressed start
    if recording and serialok:
        # Tries to read from serial buffer
        try:
            r = s.readline().decode().split("\r")[0].split(",")
            print(r)
            r = np.expand_dims(np.array([float(s) for s in r]),axis=0)
        except: 
            r = np.zeros((1,3))
            
        # Concatenates to recorded data
        if r.shape[1]==6:
            if len(data) < TIMESPAN :
                data = np.concatenate((data,r))
            else:
                data[0:TIMESPAN,:] = np.concatenate((data[1:,:],r),axis=0)
            global x
            x = np.concatenate((x,r))
            
        # Updates plot
        for i,_ in enumerate(gui.lines):
            gui.lines[i].set_xdata(np.arange(0,len(data)))
            gui.lines[i].set_ydata(data[:,i])
            gui.lines[i].set_color(list(gui.colors.values())[i])
        gui.canvas.draw()
        
    # Updates Info label
    gui.update_info_label(
        "DEVICE: "+DEVICE_NAME+"\n"+
        "READING EVERY: "+str(DELAY)+" ms\n"+
        "SERIAL COMMUNCATION: "+("ACTIVE" if s is not None else "INACTIVE")+"\n"+
        "\n"+
        "USING CLASSIFIER MODEL: "+model.name+"\n"+
        "\n"+
        f"VERSION 1.1, Python {sys.version[:5]}, TF {tensorflow.__version__}"
        
    )   
    gui.afterloop = gui.w.after(DELAY,plot_signals)

def main():
    global gui
    gui = GUI(
        width=FIG_WIDTH,
        height=FIG_HEIGHT,
        borders=BORDERS,
        timespan=TIMESPAN,
        maxy=MAXY,
        buttoncb = buttons_callbacks,
        config=config
    )
    gui.update()

    gui.afterloop = gui.w.after(DELAY,plot_signals)
    gui.run()

if __name__ == '__main__':
    main()