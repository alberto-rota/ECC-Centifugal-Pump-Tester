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

import tkinter as tk
import serial.tools.list_ports
import os
import json

from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg



class GUI(tk.Frame):
    def __init__(self,width=900,height=600,borders=20,
                    timespan=200,maxy=12,buttoncb=None,config=None):

        FIGURE_TITLE = "Qura ECC Pump Tester"
        
        self.borders=borders
        self.width=width
        self.height=height
        
        self.w = tk.Tk()
        size = str(width)+"x"+str(height)
        self.w.geometry(size)
        self.w.title(FIGURE_TITLE)
        self.w.iconbitmap(os.path.join("gui","icon.ico"))
        self.buttons = []
        
        self.scomm_name = ""
        self.scomm_port = ""
        self.scomm_baud = ""
        
        self.timespan = timespan
        self.maxy = maxy
        
        self.scomm_width=250
        self.scomm_height=100
        
        self.chartwidth=self.width-2*self.borders
        self.chartheight=(self.height-2*self.borders)//2
        
        self.config = config
        self.darkmode = self.config["darkmode"]
        
        if not self.darkmode:
            self.colors = self.config["colors"]
        else:
            self.colors = self.config["colors_dark"]
        self.w.configure(background=self.colors["BACKGROUND"])
        self.update()
        
# GRAPH CANVAS
        self.fig = Figure(facecolor=self.colors["BACKGROUND"])
        self.ax = self.fig.add_subplot(111)
        self.ax.set_facecolor(self.colors["BACKGROUND"])
        self.ax.spines['bottom'].set_color(self.colors["TEXT"])
        self.ax.spines['top'].set_color(self.colors["TEXT"]) 
        self.ax.spines['right'].set_color(self.colors["TEXT"])
        self.ax.spines['left'].set_color(self.colors["TEXT"])
        self.ax.tick_params(axis='x', colors=self.colors["TEXT"])
        self.ax.tick_params(axis='y', colors=self.colors["TEXT"])
        self.ax.yaxis.label.set_color(self.colors["TEXT"])
        self.ax.xaxis.label.set_color(self.colors["TEXT"])
        # ax.set_xticklabels(["{:.2f}".format(t/self.config["DELAY"]) for t in xt])
        self.ax.set_xticklabels([])
        self.ax.grid(True)
        self.fig.tight_layout()
        self.ax.set_xlim([0,self.timespan])
        self.ax.set_ylim([0,self.maxy])

        self.lines = [self.ax.plot([],[],linewidth=1)[0] for _ in range(6)]

        self.canvas = FigureCanvasTkAgg(self.fig, master = self.w)
        self.canvas.get_tk_widget().place(
            x=self.borders,
            y=self.borders,
            width=self.chartwidth,
            height=self.chartheight,
            )
        self.canvas.draw()
        
        
# BUTTONS
        global startimg,stopimg,saveimg # Otherwise cleared by garbage collection
        
        if not self.darkmode:
            self.startimg = tk.PhotoImage(file = os.path.join("gui","startbutton.png"))
            self.stopimg = tk.PhotoImage(file = os.path.join("gui","stopbutton.png"))
            self.saveimg = tk.PhotoImage(file = os.path.join("gui","savebutton.png"))
        else:
            self.startimg = tk.PhotoImage(file = os.path.join("gui","startbutton_dark.png"))
            self.stopimg = tk.PhotoImage(file = os.path.join("gui","stopbutton_dark.png"))
            self.saveimg = tk.PhotoImage(file = os.path.join("gui","savebutton_dark.png"))
            

        position=[
            self.borders,
            self.borders+self.chartheight+self.borders,
        ]
        self.startb = tk.Button(
            self.w,
            # text = "START",
            image=self.startimg,
            borderwidth=0,  
            command=buttoncb["start"],
            background=self.colors["BACKGROUND"],
            activebackground=self.colors["BACKGROUND_CLICK"]
        )
        self.startb.place(x=position[0], y=position[1])
        self.w.update()
        

        position=[
            self.borders+self.startb.winfo_width()+self.borders,
            self.borders+self.chartheight+self.borders,
            ]
        self.stopb = tk.Button(
            self.w,
            # text="STOP",
            image=self.stopimg,
            borderwidth=0,  
            command=buttoncb["stop"],
            background=self.colors["BACKGROUND"],
            activebackground=self.colors["BACKGROUND_CLICK"]
        )
        self.stopb.place(x=position[0], y=position[1])
        self.w.update()

        position=[
            self.borders+self.startb.winfo_width()+self.borders+self.stopb.winfo_width()+self.borders,
            self.borders+self.chartheight+self.borders,
            ],
        self.saveb = tk.Button(
            self.w,
            # text="SAVE",
            image=self.saveimg,
            borderwidth=0,  
            command=buttoncb["save"],
            background=self.colors["BACKGROUND"],
            activebackground=self.colors["BACKGROUND_CLICK"]
        )
        self.saveb.place(x=position[0][0], y=position[0][1])
        self.w.update()

# SERIAL COMM
        self.commframe = tk.Frame(
            self.w,
            highlightbackground=self.colors["RED"],
            highlightcolor=self.colors["RED"],
            highlightthickness=2,
            bd=2,
            background=self.colors["BACKGROUND"]
        )
        self.commlabel = tk.Label(
            self.w,
            text = "DEVICE\nNOT\nCONNECTED",
            font=('Verdana',16),
            fg = self.colors["RED"],
            background=self.colors["BACKGROUND"]
        )
        self.commlabel.place(
            x=self.borders*4+self.startb.winfo_width()+self.stopb.winfo_width()+self.saveb.winfo_width()+0.01*self.width,
            y=self.borders+self.chartheight+self.borders+0.01*self.height,
            width=self.width-self.startb.winfo_width()-self.stopb.winfo_width()-self.saveb.winfo_width()-5*self.borders-0.02*self.width,
            height=self.scomm_height-0.02*self.height,
        )
        self.commframe.place(
            x=self.borders*4+self.startb.winfo_width()+self.stopb.winfo_width()+self.saveb.winfo_width(),
            y=self.borders+self.chartheight+self.borders,
            width=self.width-self.startb.winfo_width()-self.stopb.winfo_width()-self.saveb.winfo_width()-5*self.borders,
            height=self.scomm_height,
            bordermode="inside"
        )
# CLASSIFICATION LABEL
        self.classframe = tk.Frame(
            self.w,
            highlightbackground=self.colors["BLUE"],
            highlightcolor=self.colors["BLUE"],
            highlightthickness=2,
            bd=2,
            background=self.colors["BACKGROUND"]
        )
        self.classlabel = tk.Label(
            self.w,
            text =  "\n\nClassification\nUNKNOWN\n\n",
            font=('Verdana',16),
            fg = self.colors["BLUE"],
            background=self.colors["BACKGROUND"]
        )
        self.classlabel.place(
            x=self.borders+0.01*self.width,
            y=self.borders+self.chartheight+self.borders+self.startb.winfo_height()+self.borders+0.01*self.height,
            width=self.startb.winfo_width()*2+self.borders-0.02*self.width,
            height=self.height-self.chartheight-self.startb.winfo_height()-4*self.borders-0.02*self.height,
        )
        self.classframe.place(
            x=self.borders,
            y=self.borders+self.chartheight+self.borders+self.startb.winfo_height()+self.borders,
            width=self.startb.winfo_width()*2+self.borders,
            height=self.height-self.chartheight-self.startb.winfo_height()-4*self.borders,
            bordermode="inside"
        )
        
# SAVE TEXTBOXES
        self.savepath_label = tk.Label(
            self.w,
            text = "Save To:",
            fg=self.colors["TEXT"],
            font=('Verdana',10),
            justify="center",
            background=self.colors["BACKGROUND"]
        )
        self.savepath_label.place(
            x = self.borders+self.startb.winfo_width()+self.borders+self.stopb.winfo_width()+self.borders,
            y = self.borders+self.chartheight+self.borders+self.saveb.winfo_height()+self.borders,
            width=self.saveb.winfo_width(),
        )
        self.savepath = tk.Entry(
            self.w,
            relief = "solid",
            bg = self.colors["TEXT_BACKGROUND"]
        )
        self.savepath.insert(0,self.config["savepath"])
        self.savepath.place(
            x = self.borders+self.startb.winfo_width()+self.borders+self.stopb.winfo_width()+self.borders,
            y = self.borders+self.chartheight+self.borders+self.saveb.winfo_height()+self.borders*2,
            width=self.saveb.winfo_width(),
        )
        
        self.appendtopath_label = tk.Label(
            self.w,
            text = "Append:",
            fg=self.colors["TEXT"],
            font=('Verdana',10),
            justify="center",
            background=self.colors["BACKGROUND"]
        )
        self.appendtopath_label.place(
            x = self.borders+self.startb.winfo_width()+self.borders+self.stopb.winfo_width()+self.borders,
            y = self.borders+self.chartheight+self.borders+self.saveb.winfo_height()+self.borders*3,
            width=self.saveb.winfo_width(),
        )
        self.appendtopath = tk.Entry(
            self.w,
            relief = "solid",
            bg = self.colors["TEXT_BACKGROUND"]
        )
        self.appendtopath.insert(0,self.config["append"])
        self.appendtopath.place(
            x = self.borders+self.startb.winfo_width()+self.borders+self.stopb.winfo_width()+self.borders,
            y = self.borders+self.chartheight+self.borders+self.saveb.winfo_height()+self.borders*4,
            width=self.saveb.winfo_width(),
        )
        
# SAVESTATE LABEL
        self.savedframe = tk.Frame(
            self.w,
            highlightbackground=self.colors["ORANGE"],
            highlightcolor=self.colors["ORANGE"],
            highlightthickness=2,
            bd=2,
            background=self.colors["BACKGROUND"]
        )
        self.savedlabel = tk.Label(
            self.w,
            text = "",
            font=('Verdana',9),
            fg = self.colors["ORANGE"],
            wraplength=self.saveb.winfo_width()*0.95,
            justify="center",
            background=self.colors["BACKGROUND"]
        )
        self.savedlabel.place(
            x = self.borders+self.startb.winfo_width()+self.borders+self.stopb.winfo_width()+self.borders+0.01*self.height,
            y = self.borders+self.chartheight+self.borders+self.saveb.winfo_height()+self.borders*6+0.01*self.width,
            width=self.saveb.winfo_width()-0.02*self.height,
            height=self.height-(self.borders+self.chartheight+self.borders+self.saveb.winfo_height()+self.borders*7)-0.02*self.height,
        )
        self.savedframe.place(
            x = self.borders+self.startb.winfo_width()+self.borders+self.stopb.winfo_width()+self.borders,
            y = self.borders+self.chartheight+self.borders+self.saveb.winfo_height()+self.borders*6,
            width=self.saveb.winfo_width(),
            height=self.height-(self.borders+self.chartheight+self.borders+self.saveb.winfo_height()+self.borders*7),
            bordermode="inside"
        )
    
# INITIALIZE INFO LABEL
        self.infoframe = tk.Frame(
        self.w,
            highlightbackground=self.colors["GRAY"],
            highlightcolor=self.colors["GRAY"],
            highlightthickness=2,
            bd=2,
            background=self.colors["BACKGROUND"]
        )
        self.infolabel = tk.Label(
            self.w,
            text = "",
            font=('Verdana',9),
            fg = self.colors["GRAY"],
            wraplength=self.saveb.winfo_width()*0.95,
            justify="center",
            background=self.colors["BACKGROUND"]
        )
        self.infolabel.place(
            x=self.borders*4+self.startb.winfo_width()+self.stopb.winfo_width()+self.saveb.winfo_width()+0.01*self.width,
            y=self.borders+self.chartheight+self.borders+self.scomm_height+self.borders+0.01*self.height,
            height=self.height-self.chartheight-self.commlabel.winfo_height()-9*self.borders-0.02*self.width,
            width=self.width-self.startb.winfo_width()-self.stopb.winfo_width()-self.saveb.winfo_width()-5*self.borders-0.02*self.height,
        )
        self.infoframe.place(
            x=self.borders*4+self.startb.winfo_width()+self.stopb.winfo_width()+self.saveb.winfo_width(),
            y=self.borders+self.chartheight+self.borders+self.scomm_height+self.borders,
            height=self.height-self.chartheight-self.commlabel.winfo_height()-9*self.borders,
            width=self.width-self.startb.winfo_width()-self.stopb.winfo_width()-self.saveb.winfo_width()-5*self.borders,
            bordermode="outside"
        )
        
            
        def quit_app(event):
            self.w.destroy()
            
        def dark(event):
            self.config["darkmode"] = not self.config["darkmode"]
            with open(os.path.join("config","config.json"), 'w') as configfile:
                json.dump(self.config, configfile,indent=4)
                
            with open(os.path.join("config","config.json")) as configfile:
                self.config=json.load(configfile)
                
            self.darkmode = self.config["darkmode"]
            
            if not self.darkmode:
                self.colors = self.config["colors"]
                self.startimg = tk.PhotoImage(file = os.path.join("gui","startbutton.png"))
                self.stopimg = tk.PhotoImage(file = os.path.join("gui","stopbutton.png"))
                self.saveimg = tk.PhotoImage(file = os.path.join("gui","savebutton.png"))
            else:
                self.colors = self.config["colors_dark"]
                self.startimg = tk.PhotoImage(file = os.path.join("gui","startbutton_dark.png"))
                self.stopimg = tk.PhotoImage(file = os.path.join("gui","stopbutton_dark.png"))
                self.saveimg = tk.PhotoImage(file = os.path.join("gui","savebutton_dark.png"))
            self.startb.config(image=self.startimg)
            self.stopb.config(image=self.stopimg)
            self.saveb.config(image=self.saveimg)
            self.w.configure(background=self.colors["BACKGROUND"])
            
            for widget in self.w.winfo_children():
                widget.config(
                    background=self.colors["BACKGROUND"]
                )
            self.fig.set_facecolor(self.colors["BACKGROUND"])
            self.ax.set_facecolor(self.colors["BACKGROUND"])
            self.ax.spines['bottom'].set_color(self.colors["TEXT"])
            self.ax.spines['top'].set_color(self.colors["TEXT"]) 
            self.ax.spines['right'].set_color(self.colors["TEXT"])
            self.ax.spines['left'].set_color(self.colors["TEXT"])
            self.ax.tick_params(axis='x', colors=self.colors["TEXT"])
            self.ax.tick_params(axis='y', colors=self.colors["TEXT"])
            self.ax.yaxis.label.set_color(self.colors["TEXT"])
            self.ax.xaxis.label.set_color(self.colors["TEXT"])
            self.canvas.draw()
            self.savepath.config(bg=self.colors["TEXT_BACKGROUND"])
            self.appendtopath.config(bg=self.colors["TEXT_BACKGROUND"])
            self.savepath_label.config(fg=self.colors["TEXT"])
            self.appendtopath_label.config(fg=self.colors["TEXT"])
            self.startb.config(activebackground=self.colors["BACKGROUND_CLICK"])
            self.stopb.config(activebackground=self.colors["BACKGROUND_CLICK"])
            self.saveb.config(activebackground=self.colors["BACKGROUND_CLICK"])
        self.w.bind("<Control-d>", dark)
        self.w.bind("<Control-k>", quit_app)

# GUI LOOPING      
    def run(self):
        self.w.mainloop()
    def update(self):
        self.w.update()

# SERIAL COMMUNICATION
    def check_serialcomm(self,s,DEVICE,BAUD):
        ports = serial.tools.list_ports.comports(include_links=False)
        for p in ports: 
            if p.description == DEVICE and s is not None:
                self.scomm_name = p.description.split("(")[0]
                self.scomm_port = p.device
                self.scomm_baud = BAUD
                self.update_serialcomm_label()
                return True
        self.scomm_name = ""
        self.scomm_port = ""
        self.scomm_baud = ""
        self.no_serialcomm_label();
        return False
    
    def update_serialcomm_label(self):
        self.commframe.config(
            highlightbackground=self.colors["GREEN"],
            highlightcolor=self.colors["GREEN"],
        )
        self.commlabel.config(
            text = self.scomm_name+"\n"+" Port: "+self.scomm_port+"  "+"\nBaudRate: "+str(self.scomm_baud),
            fg = self.colors["GREEN"],
        )
        
    def no_serialcomm_label(self):
        self.commframe.config(
            highlightbackground=self.colors["RED"],
            highlightcolor=self.colors["RED"],
        )
        self.commlabel.config(
            text = "DEVICE\nNOT\nCONNECTED",
            fg = self.colors["RED"],
        )
    
    
    def update_classification_label(self,classification=None, confidence=None):
        
        if classification == "C": 
            color = self.colors["GREEN"]
            text = f"Classification\nCOMPLIANT\n\nConfidence\n{confidence*100}%\n"

        elif classification == "NC": 
            color = self.colors["RED"]
            text = f"Classification\nNON COMPLIANT\n\nConfidence\n{confidence*100}%\n"
            
        else: 
            color = self.colors["BLUE"]
            text = "\n\nClassification\nUNKNOWN\n\n"

        self.classframe.config(highlightbackground=color,highlightcolor=color)
        self.classlabel.config(text = text, fg = color)
        
        
    def give_saved_alert(self,restarting=False,lines=0,path=""):
        if not restarting:
            self.savedlabel.config(
                text = f"Wrote {lines} lines on\n"+path,
            )
        else:
            self.savedlabel.config(
                text = "",
            )
            
    def update_info_label(self,newtext):
        self.infolabel.config(
            text = newtext
        )
        
    def update_config(self):
        self.config["savepath"] = self.savepath.get()
        self.config["append"] = self.appendtopath.get()
        return self.config