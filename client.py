#!/usr/local/bin/python
# coding: utf-8

from tkinter import *
import socket
from threading import Thread
import sys
import time
import ast
import os
import platform
from textwrap import dedent

def senBlirAlltSvart(): # Clears the screen on Linux, Mac & Win.
    if (os.name == "posix"): os.system("clear")
    elif (platform.system() == "Windows"): os.system("cls")
    else: pass

#----/ Debugging /--------------------------------------------------------------------#
def c(col): return "\33[0m" if col==0 else ("\33[3"+str(col)[0]+";4"+str(col)[1]+"m")
class ContextManager:
    ''' This is my debugger/context manager. I'm getting a lot of exceptions from both
    Tcl and socket, and hate how messy the code looks with try/except clauses everywhere.
    With this class I can simply add "with calm:" before any line I suspect might misbehave.
    Or that's how it's meant to be, at least. This project is entirely tkinter based, so
    since I don't use the terminal, I print all exceptions there, without them being in the
    way, but it could just as easy be written out to a log file. An instance of this class
    can be called with "dangerLevel" (1: Critical, 2: Trivial) and/or "contextComment".
    The self.debugLevel setting takes a value between 0-2:
    0: Silent, 1: Critical exceptions, 2: All exceptions '''
    def __init__(self, dLev=1, comm="N/A"):
        self.debugLevel = 2
        self.contextComment,self.dangerLevel,self.ct,self.ex=comm, dLev, 0, False
        self.levels = [f"{c('00')} Schrödingers Exception             {c('34')}",
                       f"{c('10')} Potentially Troublesome Exception  {c('34')}",
                       f"{c('20')} Probably Mostly Harmless Exception {c('34')}"]
    def __call__(self,dangerLevel,contextComment):
        self.dangerLevel,self.contextComment = dangerLevel,contextComment
        return self
    def __enter__(self): self.ct += 1
    def __exit__(self, exc_type, exc_val, exc_tb):
        self.ex = True if (exc_type != None) else False
        if (exc_type == None): self.ct -= 1
        if (exc_type != None) and (self.debugLevel >= self.dangerLevel):
            fileName = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
            print(f"{c(0)}  {'_'*31}{'_'*(len(str(self.ct)))}")
            print(f"_/{c(34)} Context Manager - Exception #{self.ct} ",end='')
            print(f"{c(0)}\\{'_'*(46-(len(str(self.ct))))}",end='')
            print(f"{c(34)}\n\n {self.levels[self.dangerLevel]}")
            print(f"\n  Type: \"{exc_type.__name__}\"\n\n  Value: \"{exc_val}\"")
            print(f"\n  Doc string: \"{exc_val.__doc__}\"")
            print(f"\n  Context Comment: {self.contextComment}")
            print(f"\n\33[33m  File Name: {fileName}")
            print(f"\n\33[33m  Line Number {exc_tb.tb_lineno}:\n\33[36m")
            with open(__file__,"r") as src:
                print("  "+dedent(src.readlines()[exc_tb.tb_lineno-1].rstrip()))
            print(f"\33[33m{'~'*80}\33[0m\n")
        return True


class GameScreen:
    def __init__(self, playerName, servPort, servIP):

        # SETTINGS:
        self.debugLevel = 2 # 0: Silent, 1: Critical exceptions, 2: All exceptions
        self.paintColor = "black"
        self.defaultColor = "black"
        self.playerName = playerName
        self.paintModeOn = False
        self.old_x = None
        self.old_y = None

        # SOCKET STUFF:
        self.servIP = servIP
        print(f"servIP from startScr: {self.servIP}\n")
        self.servPort = int(servPort)
        print(f"servPort from startScr: {self.servPort}\n")
        try:
            self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            print(f"Socket created: {self.sock}\n")
        except:
            if calm.ex: print("Failed to create socket...\n")
        try:
            self.sock.connect((self.servIP, self.servPort))
            print(f"Connected to {self.servIP} on port {self.servPort}!\n")
            try:
                self.sendMsg = "SN//"+playerName
                self.sendMsgNow()
            except:
                print("Failed to send playerName...\n")
        except:
            print("Connection to server failed...\n")

        # MSG STUFF:
        self.msg = None
        self.msgParts = None
        self.msgType = None
        self.msgName = None
        self.msgValue = None

        # TKINTER STUFF:
        self.window = Tk()

        # Menu bar:
        self.menubar = Menu(self.window)
        self.window.config(menu = self.menubar)
        self.gamemenu = Menu(self.menubar)
        self.currentMenu = Menu(self.menubar)
        self.menubar.add_cascade(label = "Game", menu = self.gamemenu)
        self.gamemenu.add_cascade(label = "Current game", menu = self.currentMenu)
        self.currentMenu.add_command(label = "New word - You paint!", command = self.newWord)
        self.currentMenu.add_command(label = "Change name", command = self.changeName)
        self.currentMenu.add_command(label = "Cheat", command = self.cheat)
        self.gamemenu.add_command(label = "Quit", command = self.onExit)

        # Main window:
        self.window.title('Skrippl.py')
        self.window.geometry('{}x{}'.format(810, 617))
        self.top_frame = Frame(self.window, bg='grey', width=800, height=50, pady=3)
        self.center = Frame(self.window, bg='black', width=800, height=40, padx=0, pady=3)
        self.btm_frame = Frame(self.window, bg='black', width=800, height=45, pady=0)
        self.window.grid_rowconfigure(1, weight=1)
        self.window.grid_columnconfigure(0, weight=1)
        self.top_frame.grid(row=0, sticky="ew")
        self.center.grid(row=1, sticky="nsew")
        self.btm_frame.grid(row=3, sticky="ew")
        self.center.grid_rowconfigure(0, weight=0)
        self.center.grid_columnconfigure(1, weight=0)
        self.ctr_left = Frame(self.center, bg='grey', width=500, height=500, padx=0, pady=0)
        self.ctr_right = Frame(self.center, bg='black', width=300, height=300, padx=3, pady=0)
        self.ctr_left.grid(row=0, column=0, sticky="ns")
        self.ctr_right.grid(row=0, column=2, sticky="ns")
        self.ctr_r_top = Frame(self.ctr_right, bg='grey', width=300, height=188, padx=0, pady=0, borderwidth=2, relief="groove")
        self.ctr_r_btm = Frame(self.ctr_right, bg='grey', width=300, height=318, padx=0, pady=0, borderwidth=2, relief="groove")
        self.ctr_r_top.grid_propagate(False)
        self.ctr_r_btm.grid_propagate(False)
        self.ctr_r_top.grid(row=0, column=0, sticky="ns")
        self.ctr_r_btm.grid(row=1, column=0, sticky="ns")
        self.btm_left = Frame(self.btm_frame, bg='grey', width=508, height=50, padx=0, pady=0)
        self.btm_right = Frame(self.btm_frame, bg='black', width=306, height=50, padx=0, pady=0)
        self.btm_left.grid_propagate(False)
        self.btm_left.grid(row=0, column=0, sticky="ns")
        self.btm_right.grid(row=0, column=1, sticky="ne")
        self.c = Canvas(self.ctr_left, bg='white', width=500, height=500)
        self.c.grid(row=0, rowspan=5, column=0, columnspan=5)
        self.c.bind('<B1-Motion>', self.paint)
        self.c.bind('<ButtonRelease-1>', self.reset)
        self.upperBox = Text(self.ctr_r_top, bg='white', width=41, height=12)
        self.textbox = Text(self.ctr_r_btm, bg='white', width=41, height=21)
        self.upperBox.grid(row=0, column=0)
        self.textbox.grid(row=0, column=0)
        self.entrybox = Text(self.btm_right, bg='white', width=41, height=3, borderwidth=1, relief="sunken")
        self.entrybox.grid(row=2, column=0)
        self.entrybox.bind("<Return>", self.pressedEnter)
        self.clearButton = Button(self.btm_left, text='Clear', command=self.eraseCanvas)
        self.clearButton.grid(row=0, column=0)

        ######## Just for dev testing #########
        self.paintModeToggle = IntVar()
        self.paintModeBtn = Checkbutton(self.btm_left, text="Debug Paint mode", variable=self.paintModeToggle)
        self.paintModeBtn.grid(row=0, column=1)
        #######################################

        # Start receiving data from server:
        self.receivethread = Thread(target=self.receive)
        self.receivethread.start()
        self.window.mainloop()

    def onExit(self):
        self.window.destroy()
        sys.exit("Bye.")

    def changeName(self):
        self.inTheBox = "SN//YOUR-NAME-HERE"
        self.entrybox.insert(END, self.inTheBox)
        self.entrybox.see("end")

    def cheat(self):
        self.inTheBox = "//Ooooooh! I can see it now!"
        self.entrybox.insert(END, self.inTheBox)
        self.entrybox.see("end")

    def newWord(self):
        self.inTheBox = "NW//futureSettingsHere"
        self.entrybox.insert(END, self.inTheBox)
        self.entrybox.see("end")

    def debugInfo(self, dangerLevel, exceptContext="Nope"):
        # Setting for debug level can be found under __init__() above.
        levels = ["Schrödingers Exception",\
                  "Potentially Somewhat Troublesome Exception",\
                  "Probably Mostly Harmless Exception"]
        if self.debugLevel >= dangerLevel:
            senBlirAlltSvart() # Clear the screen
            print(f"{'~'*18}[DEBUG]{'~'*18}\n{levels[dangerLevel]}")
            print(f"\n{sys.exc_info()[0].__name__}: {getattr(sys.exc_info()[1], '__doc__')}")
            print(f"\nLine Number: {sys.exc_info()[2].tb_lineno}")
            print(f"\nContext: {exceptContext}")
            print(f"\nmsg(decoded): {self.msg.decode('utf8')}")
            print(f"\nmsgType: {self.msgType}")
            print(f"\nmsgName: {self.msgName}")
            print(f"\nmsgValue: {self.msgValue}\n{'~'*43}")

    def receive(self):
        while True:
            try:
                self.msg = self.sock.recv(1024)
                self.msgParts = self.msg.decode('utf8').split(":")
                if len(self.msgParts) == 3:
                    self.msgType = self.msgParts[0]
                    self.msgName = self.msgParts[1]
                    self.msgValue = self.msgParts[2]
                    self.msgRouter()
                else:
                    continue
            except:
                print("Receive error")

    def pressedEnter(self, event):
        self.sendMsg = self.entrybox.get("1.0",END).strip()
        if self.sendMsg:
            self.sendMsgNow()
        self.entrybox.delete(1.0, END)

    def sendMsgNow(self):
        self.sock.send(str(self.sendMsg).encode('utf8'))

    def msgRouter(self):
        if self.msgType == "CO":
            # msgValue: Paint Coordinates
            with calm:
                if not self.paintModeOn:
                    with calm:
                        self.recreatePaint()

        if self.msgType == "GS":
            # msgValue: Word Guess
            self.inTheBox = f"{self.msgName} made a guess: {self.msgValue}\n"
            self.textbox.insert(END, self.inTheBox)
            self.textbox.see("end")

        if self.msgType == "//":
            # msgValue: Chat Comment
            self.inTheBox = f"// {self.msgName}: {self.msgValue}\n"
            self.textbox.insert(END, self.inTheBox)
            self.textbox.see("end")

        if self.msgType == "RG":
            # msgValue: Right Word Guess
            self.inTheBox = f"{self.msgName} NAILED IT!\n"
            self.textbox.insert(END, self.inTheBox)
            self.textbox.see("end")

        if self.msgType == "PT":
            # msgValue: Points
            pass # Not implemented yet.

        if self.msgType == "MS":
            # msgValue: Misc. Server Notice
            self.inTheBox = f"Server: {self.msgValue}\n"
            self.textbox.insert(END, self.inTheBox)
            self.textbox.see("end")

        if self.msgType == "CH":
            # msgValue: Cheat!
            with calm:
                if self.msgName == self.playerName:
                    with calm: self.sendMsg = "SN//"+self.playerName+"(cheater)"
                    with calm: self.sendMsgNow()
                    with calm: self.inTheBox = self.msgValue
                    with calm: self.entrybox.insert(END, self.inTheBox)
                    with calm: self.entrybox.see("end")

        if self.msgType == "NW":
            # msgValue: New Word!
            # Turns of paintMode for everyone and enables it for the named player.
            if self.msgName == self.playerName:
                with calm: self.paintModeBtn.select()
                with calm: self.inTheBox = str(self.msgName + ", it's your time to paint!\nThe word is:\n" + self.msgValue)
                with calm: self.textbox.insert(END, self.inTheBox)
                with calm: self.textbox.see("end")
            else:
                with calm: self.paintModeBtn.deselect()

    def paint(self, event):
        if self.paintModeToggle.get() == 1:
            self.paintModeOn = True
        else:
            self.paintModeOn = False
        if self.paintModeOn:
            if self.old_x and self.old_y:
                self.c.create_line(self.old_x, self.old_y, event.x, event.y, width=4, fill=self.paintColor)
            self.sendMsgValue = [self.old_x, self.old_y, event.x, event.y, self.paintColor]
            self.old_x = event.x
            self.old_y = event.y
            self.sendMsg = ("CO//"+str(self.sendMsgValue))
            self.sendMsgNow()

    def reset(self, event):
    # Stop painting when mouse butten is no longer pressed
        self.old_x, self.old_y = None, None

    def recreatePaint(self):
        try:
            self.coords = ast.literal_eval(self.msgValue)
        except:
            self.debugInfo(dangerLevel=2, exceptContext="recreatePaint, ast.literal_eval(self.coords)")
        try:
            self.x1, self.y1, self.x2, self.y2, self.paintColor = self.coords[0], self.coords[1], self.coords[2], self.coords[3], self.coords[4]
        except:
            self.debugInfo(dangerLevel=2, exceptContext="recreatePaint, self.x1... = coords[0]...")
        if self.paintColor != "clear":
            try:
                self.c.create_line(self.x1, self.y1, self.x2, self.y2, width=4, fill=self.paintColor) #, tags="drawing"
            except TclError:
                pass
                #self.debugInfo(dangerLevel=2, exceptContext="recreatePaint, self.c.create_line")
        else:
            self.eraseCanvas()

    def eraseCanvas(self):
        if self.paintModeOn: # If the player is currently painting, this clears everyone else's canvas.
            self.c.delete("all") # Clear the canvas
            self.sendMsgValue = [0,0,0,0,"clear"] # I didn't want to over-complicate things, so the
                                                  # screen-clearing command pretends to be a color.
            self.sendMsg = ("CO//"+str(self.sendMsgValue)) # Telling the server it's drawing stuff with "CO"
            self.sendMsgNow()
            self.paintColor = self.defaultColor
        else:
            self.c.delete("all") # Clear the canvas

class ShowStartScreen():
    def __init__(self):
        senBlirAlltSvart()
        self.startScreen = Tk()
        self.label1 = Label(self.startScreen, text="Welcome to skrippl.py!\n\n To connect to a game server, "
                                                   "fill in the fields and press [Join Game]:\n\nServer IP:")
        self.label1.grid(row=1, column=1)
        self.defaultIP = StringVar(self.startScreen, value='127.0.0.1')
        self.entryIP = Entry(self.startScreen, textvariable=self.defaultIP)
        self.entryIP.grid(row=2, column=1)

        self.label2 = Label(self.startScreen, text="Server Port:")
        self.label2.grid(row=3, column=1)
        self.entryPort = Entry(self.startScreen)
        self.entryPort.grid(row=4, column=1)

        self.label3 = Label(self.startScreen, text="Your Name:")
        self.label3.grid(row=5, column=1)
        self.entryName = Entry(self.startScreen)
        self.entryName.grid(row=6, column=1)

        self.joinBtn = Button(self.startScreen, text='Join Game', command=self.onJoin)
        self.joinBtn.grid(row=7, column=1)

        self.startScreen.mainloop()

    def onJoin(self): # Reminder to implement a config file system!
        self.servIP = self.entryIP.get()
        self.servPort = self.entryPort.get()
        self.playerName = self.entryName.get()
        self.startScreen.destroy()
        newGameScr = GameScreen(servIP=self.servIP, servPort=self.servPort, playerName=self.playerName)

calm = ContextManager()
startScr = ShowStartScreen()
