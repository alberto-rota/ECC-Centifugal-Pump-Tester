# Qura ECC Centrifugal pump compliancy tester
An IR-based device for testing the compliance of ECC centrifugal pumps in terms of the hemolitic/thrombogenic effects of the magnetic impeller unstable rotations. 
***
*Active Contributors: Alberto Rota, Nicolò Pasini, Silvia Bonomi, Gaia Albani, Elisabetta Criseo, Elia Pederzani*
***
## Interface Installation
* Windows: *Link not yet Available*
* Linux: *Link not yet Available*

**NOTE:** The interface embeds the ML kodel for the compliancy classification, hence at the moment it includes the whole TensorFlow framework. The size of the download is close to 1GB, but will be optimized in the future

**Requirements:** No requirement is necessary. The program runs as a standalone application.

After downloading, copy the folder in the directory of your choice. To run the interface excecute the file `qura_pump_tester`, which opens the following window

![snap](https://github.com/alberto-rota/Qura-ECC-Centifugal-Pump-Tester/blob/main/media/snapshot.png)

***
## How to use this Interface
After being plugged in, the device should be detected automatically in the top-right frame, which becomes green and displays the device name, COM-Port and Baudrate. If the Serial Communication is not initialized correctly, the bottom-right gray frame shows `SERIAL COMMUNICATION: INACTIVE`: check that the device name in the `config` file is correct.
With serial communication estabilished, the workflow to be followed is:
* Press the green **START** button to start recording the signals. Ideally, the **START** button should be pressed when the pump is steadily rotating at 500 rpm. The recordings will be displayed in the cart area in real time
* Press the red **STOP** button to stop the recording. Ideally, the **STOP** button should be pressed when the pump is still rotating at 500 rpm and before stopping the driver motion. After this button is pressed, the AI model performs the classification and displays the output in the bottom-left frame
* Press the orange **SAVE** button to save the recording for the last pump tested on a *.csv* file. The file will be saved in the folder specified in the "Save to:" textbox; if any text is specified in the "Append:" textbox, that same text will be appended to the filename. For example, with:
  - *Save to:* C:\Users\qura\tests
  - *Append:* appended

The file will be saved as:
`C:\Users\qura\tests\DDMMYY_HHMMSS_appended.csv` [DayMonthYear_HourMinutesSeconds]

***
***


## Project Overview
The device is placed on top of the pump while it is mounted and rotating on the driver. The entity of the fluttering is measured as the distance from the 6 IR phototransistors (OPB730F) placed on the pump roof facing downward. The bell-shaped sensitivity curve of the OPB730F ([see datasheet](https://github.com/alberto-rota/Qura-ECC-Centifugal-Pump-Tester/tree/main/media/OPB730F%20Datasheet.pdf)) suggest an inverse relationship between distance and output voltage. The signals are then aquired by an ESP32 and sent to a computer in serial communication

The acquisition circuit is reported below:

![circuit](https://github.com/alberto-rota/Qura-ECC-Centifugal-Pump-Tester/tree/main/media/circuit.png)

and it has been embedded in a custom-made PCB, which connects to the ESP32 via JST connectors.
![pcb](https://github.com/alberto-rota/Qura-ECC-Centifugal-Pump-Tester/tree/main/media/pcb.png)

## Compliancy assessment
Since no evitent distinction critheria emerge from the acquired signals, an AI-based classifier has been trained by recording the signals from 51 pumps at low (100 rpm) and high (500 rpm) speed.
The model is based on a LSTM architecture. The signal is divided in 75-samples-long windows, sliced from the signals (which may have different length) with a padding of 25. No data-augmentation is performed. After an 8-fold cross validation, the model from the best fold classified a test set with an **accuracy of 88%**. 

*The LSTM model is being developed further, no additonal details on the results are therefore provided*

## Design (W.I.P)
![design](https://github.com/alberto-rota/Qura-ECC-Centifugal-Pump-Tester/tree/main/media/design.png)
