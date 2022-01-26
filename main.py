#
from serial import Serial
from rich import print
from rich.console import Console
import datetime as dt
import sys
import keyboard
import time
import numpy as np
from GUI import GUI
import os
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '3'
import tensorflow as tf
tfk = tf.keras

def flush_input():
    try:
        import msvcrt
        while msvcrt.kbhit():
            msvcrt.getch()
    except ImportError:
        import sys, termios
        termios.tcflush(sys.stdin, termios.TCIOFLUSH)

def printme():
    print("Pressed!")
            
def main(args):
    recording = False
    console = Console()
    
    # ARGV reading 
    if args[1] != None:  port=args[1].upper() 
    else: port='COM9'
    
    if args[2] != None: baudrate = args[2] 
    else: baudrate = 115200
    
    # INITIALIZE SERIAL COMMUNICATION
    try:
        global s
        s = Serial(port, baudrate,timeout=0.005)
        print(f"[green]OPENED: '{port}' on baudrate [cyan]{baudrate}")
    except:
        print(f"[red]ERROR: Can't open serial port '{port}' on baudrate [cyan]{baudrate}")
        return 0
    s.reset_input_buffer();
    print();
    time.sleep(0.2);
    print("[italic]Press [bold]r[/bold] to start")
    
    # LOAD THE CLASSIFIER
    try:
        model = tfk.models.load_model('models/qurapumpclassifier_.h5')
        modelloaded = True
    except:
        modelloaded = False
        
    tbuff = -1
    
    # RECORDING LOOP [exits when Q key is pressed]
    with console.status("") as status:
        status.stop()
        while True:  
            time.sleep(0);
            
            # R is pressed: enters recording mode
            if keyboard.is_pressed('r') and not recording:
                time.sleep(0.2);
                s.reset_input_buffer();
                fname = dt.datetime.now().strftime("%d%m%Y_%H%M%S")
                print("[italic]Press [bold]s[/bold] to stop")
                f = open(fname+".csv","w")
                # time.sleep(0.5)
                recording = True
                tbuff = 0;
                status.update(f"Writing on [green]"+fname+".csv"+"[white]...")
                status.start()
                
            # S is pressed: exits recording mode and performs classification if a model is loaded
            if keyboard.is_pressed('s') and recording:
                status.stop()
                time.sleep(0.5)
                s.reset_input_buffer();
                print(f"[italic]Wrote {tbuff-101} lines")
                recording = False
                f.close()
                flush_input()
                strappend = input("Append to filename: ");
                if len(strappend)>0: 
                    fnamenew=fname+"_"+strappend
                    os.rename(fname+".csv",fnamenew+".csv")
                else: fnamenew=fname
                fname = fnamenew
                print("[orange3]--> Saved: [italic]"+fname+'.csv')
                tbuff = -1
                if modelloaded:
                    WINDOW_SIZE = 75
                    STRIDE = 25
                    WORKING_SENSORS = [1,2,4,5,6]
                    WORKING_SENSORS = [ws-1 for ws in WORKING_SENSORS]
                    
                    x = np.genfromtxt(fname+".csv", delimiter=',')
                    windows = [x[i:i+WINDOW_SIZE,WORKING_SENSORS] for i in range(0,x.shape[0]-WINDOW_SIZE,STRIDE)]
                    windows = np.stack(windows)/3300
                    # for w in windows: print(w)
                    
                    outs = model.predict(windows)
                    # preds = np.zeros(outs.shape)
                    # preds[outs>=0.5]=1
                    pred = np.mean(outs.T)
                    # print(outs)
                    for i,w in enumerate(outs): 
                        if w>0.5:
                            print(outs[i],"[green]C") 
                        else:
                            print(outs[i], "[red]NC")
                    if pred>0.5:
                        print("Classification: [green]COMPLIANT",end=" - ")
                    else:
                        print("Classification: [red]NON COMPLIANT",end=" - ")
                    print(f"Confidence: {100*(2*abs(pred-0.5))}%")
                print()
                print("[italic]Press [bold]r[/bold] to start")
                
            # Q is pressed: exits recording mode and performs classification if a model is loaded
            if keyboard.is_pressed('q'):
                #s.close()
                print(f"[red]Exiting. Serial port [cyan]{port} [red]closed")
                time.sleep(0.5)
                flush_input()
                break
            
            if recording:
                # print(tbuff)
                r = s.readline().decode().split("\r")[0]
                # r = "1,2,3,4,5,6"
                if tbuff>100 and r!="":
                    f.write(str(r)+"\n")                    
            if tbuff >=0: 
                tbuff = tbuff+1
                
            
# Main funciton call
if __name__ == '__main__':
    main(sys.argv)

