"""
deskq.pyw
Windows version of deskq.py
Uses tkinter instead of Gtk
"""
import webbrowser
import subprocess
import os
import time
from tkinter import *
from time import strftime
import pyperclip
try:
    from googlesearch import search
except ImportError:
    print("No module named 'google' found")

# PATH FOR APP FILES
# ##################
dq_path = ".\\"  # may not need this for subprocess open
b_deco = False
b_topm = False
leng = 25

class Application(Frame):
    """
    This application has a very small GUI
    consisting of a grid layout with one entry widget.
    Some functionality is performed with secondary windows
    consisting of a pack layout with one list widget.
    """
    def __init__(self, parent):
        Frame.__init__(self, parent)
        self.pack(fill=BOTH, expand=True, padx=0, pady=0)
        self.config(bg='#333333')
        global leng
        self.last_command = ""
        self.create_widgets()
        self.entry1.focus()

    def create_widgets(self):
        """ ENTIRE INTERFACE IS ONE ENTRY FIELD """
        self.entry1 = Entry(self,  relief=FLAT,
                    bg='#666', fg='black', font='Helvetica 9 bold')
        self.entry1.grid(row=1, column=1, padx=4)
        self.entry1.bind('<Return>', self.eventHandler)
        # blank the entry box with Esc key
        self.entry1.bind('<Escape>',
                        lambda event, _b='':
                            self.set_text(_b))
        self.entry1.config(highlightbackground='#333333')
        self.entry1.configure( width=leng )
        self.entry1.bind("<Key>", self.check_key)
        self.btnsave = Button( self, text='■', command=self.saveFromClip,
                bg='#333', fg='#999', relief=FLAT,
                font = ('Sans','12','bold'),
                width=2 )
        self.btnsave.grid(row=1, column=2)
        self.btnsave.config(highlightbackground='#222')


        # read the text editor name
        # with open("edit.txt", "r") as f_hand:
        #     self.editor = f_hand.readline().strip()
        with open("seaq.txt", "r") as f_hand:
            self.searchquery = f_hand.readline()

    def eventHandler(self, event):
        """ HANDLES COMMAND OR SEARCH FROM THE ENTRY FIELD """
        global b_deco  # bool for window decoration
        global b_topm  # bool for window topmost
        global leng  # integer for Entry widget length

        stext = self.entry1.get()
        if stext == "":
            return

        self.last_command = stext

        if stext[0] in "$;.":  # is it tag to open a URL or run a command?
            with open("serv.txt", "r") as fi:
                for srv in fi:
                    if srv[1:].startswith(stext[1:]):  # tag
                        ary = srv.split(",")
                        if "http" in srv:
                            webbrowser.open(ary[1].rstrip())  #  URL
                            self.set_text("")
                        else:
                            if " " in ary[1]:  # process with arguments
                                cmd = ary[1].rstrip().split(" ")
                                subprocess.Popen(cmd)
                            else:
                                os.system(ary[1].rstrip()) # process w/o args
                                # obj.set_text("")

        elif stext.lower() == "x":
            root.destroy()
            quit()  # Note: must use "winset" to save geometry

        elif stext.lower().startswith("u:"):
            stext = stext[2:]
            self.writehist(stext)  # save to history (hist.txt)
            if stext.startswith("http"):
                webbrowser.open(stext)
            else:
                return

        elif len(stext) > 1 and stext[1] == ':':
            # try to locate the service from the serv.txt file
            with open("serv.txt", "r") as fi:
                for srv in fi:
                    if srv.startswith(stext[:1]):
                        ary = srv.split(",")
                        webbrowser.open(ary[2] + stext[2:])

        elif stext.startswith("http"):
            self.writeurl(stext)  # write to top of urls.txt

        elif stext.lower() == "hist":
            self.onHistView()

        elif stext.lower() == "list":
            self.onListView()

        elif stext.lower() == "sc":
            with open("clip.txt", "a") as f_hand:
                f_hand.write(pyperclip.paste() + "\n\n")

        elif stext.lower() == "ec":
            self.open_editor("clip.txt")

        elif stext.lower() == "es":
            self.open_editor("serv.txt")

        elif stext.lower() == "eh":
            self.open_editor("hist.txt")

        elif stext.lower() == "eu":
            self.open_editor("urls.txt")

        # elif stext.lower() == "ee":
        #     self.open_editor("edit.txt")

        elif stext.lower().startswith("ex:"):
            stext = stext[3:]
            lcmd = stext.split(" ")  # convert the command line into a python List
            subprocess.Popen(lcmd)

        elif stext.lower() == "help":
            self.open_editor("help.txt")

        elif stext[0] == '?':
            stext = stext[1:]
            ans = eval(stext)
            pyperclip.copy(ans)
            self.set_text('?' + str(ans)) # set_text is a user function
            return

        elif stext.startswith(">"):   # google search
            stext = stext[1:]
            self.writehist(stext)
            for j in search(stext, tld="com", num=5, stop=5, pause=3):
                # print(j)
                webbrowser.open(j)
                time.sleep(1)

        elif stext.lower() == "cap":
            if b_deco:
                b_deco = False
                root.overrideredirect(False) # no caption
            else:
                b_deco = True
                root.overrideredirect(True) # yes caption

        elif stext.lower() == "top":
            if b_topm:
                b_topm = False
                root.attributes("-topmost", False)  # Not on top
            else:
                b_topm = True
                root.attributes("-topmost", True)  # on top

        elif stext.lower() == "winset":
            p = root.geometry().split("+")  # 213x39+500+500 WxH+left+top
            t = self.entry1.configure('width')  # ('width','width','Width',20,25)
            leng = t[4]  # WIDTH of ENTRY leng
            with open("coor.txt", "w") as f_hand:
                f_hand.write(p[1] + "\n" + p[2] + "\n")  # left and top (p[1], p[2])
                f_hand.write(str(int(b_deco)) + "\n")
                f_hand.write(str(int(b_topm)) + "\n")
                f_hand.write(str(leng) + "\n")

        else:
            webbrowser.open(self.searchquery + stext)
            self.writehist(stext)  # save to history (hist.txt)

        self.set_text("")

    #  OTHER FUNCTIONS

    def saveFromClip(self):
        """ handle saving of clipboard contents """
        stext = self.entry1.get()
        if stext != "":
            # then just run for whatever is in stext
            self.eventHandler(self)
            return
        # assume something was placed in clipboard
        stext = pyperclip.paste()
        if stext == "":
            return
        # assume it is either a URL or some text to save
        if stext.startswith("http"):
            self.writeurl(str(stext))
        else:
            with open("clip.txt", "a") as f_hand:
                f_hand.write(stext + "\n\n")
        pyperclip.copy("")  # clear the clipboard

    def set_text(self, text):
        """ helper function to set text into Entry field """
        self.entry1.delete(0, END)
        self.entry1.insert(0, text.strip())

    def writeurl(self, sline):
        """ writes a line to the top of urls.txt file """
        f_hand = open("urls.txt", "r")
        hold = f_hand.readlines()
        f_hand.close()
        with open("urls.txt", "w") as f_hand:
            f_hand.write(sline + "\n")
            for item in hold:
                f_hand.write(str(item))

    def writehist(self, sline):
        """ writes a line to the history file """
        with open("hist.txt", "a") as f_hand:
            f_hand.write(sline + ", " + strftime('%x') + "\n")

    def onHistView(self):
        """ Launch new window with listbox and hist.txt contents """
        t = Toplevel(self)
        t.wm_title("Search History")
        t.geometry("400x300") # WxH+left+top
        # l = Label(t, text="This is hist window")
        t.config(bg='#333333')

        def onHistClose(self):
            t.destroy()
            t.update()

        t.bind("<Escape>", onHistClose)
        sbar = Scrollbar(t)
        sbar.pack(side = RIGHT , fill=Y)
        l = Listbox(t, yscrollcommand = sbar.set, bg='#444', fg='white')
        f_hand = open("hist.txt", "r")
        items = f_hand.readlines()
        items.reverse()
        f_hand.close()
        for inx, item in enumerate(items):
            item = item[0:item.find(", ")].rstrip()
            l.insert(inx, " " + item)
        l.bind("<<ListboxSelect>>", self.onHistSelect)
        l.pack(side="top", fill="both", expand=True, padx=10, pady=10)
        sbar.config(command = l.yview)

    def onHistSelect(self, val):
        """ Handle row clicked in history listbox """
        sender = val.widget
        idx = sender.curselection ()
        print(idx)
        value = sender.get(idx)
        print(value)
        webbrowser.open(self.searchquery + value)

    def onListView(self):
        """ Launch new window with listbox of saved URLs """
        t = Toplevel(self)
        t.wm_title("DeskQ Saved URLs")
        t.geometry("400x300") # WxH+left+top
        t.config(bg='#333333')

        def onListClose(self):
            t.destroy()
            t.update()

        t.bind("<Escape>", onListClose)
        sbar = Scrollbar(t)
        sbar.pack(side = RIGHT , fill=Y)
        l = Listbox(t, yscrollcommand = sbar.set, bg='#444', fg='white')
        f_hand = open("urls.txt", "r")
        items = f_hand.readlines()
        f_hand.close()
        for inx, item in enumerate(items):
            l.insert(inx, item.rstrip())
        l.bind("<<ListboxSelect>>", self.onListSelect)
        l.pack(side="top", fill="both", expand=True, padx=10, pady=10)
        sbar.config(command = l.yview)

    def onListSelect(self, val):
        """ Handle row clicked in URL listbox """
        sender = val.widget
        idx = sender.curselection()
        value = sender.get(idx)
        webbrowser.open(value)

    def open_editor(self, fin):
        """ Launch text editor with 'fin' file """
        #subprocess.Popen(["pythonw", "coedit.pyw", fin])
        subprocess.Popen(["notepad.exe", fin])

    def check_key(self, event):
        if event.keysym == "Up" or event.keysym == "Down":
            self.set_text(self.last_command)

# END OF Application class


root = Tk()
# SET POSITION FROM LAST SAVE POSITION
lcoor = tuple(open("coor.txt", 'r'))  # no relative path for this
leng = int(lcoor[4])
root.geometry('+%d+%d'%(int(lcoor[0].strip()), int(lcoor[1].strip())))
root.title("dq")
root.iconphoto(False, PhotoImage(file='icon.png'))
#root.resizable(0, 0)  # no resize & removes maximize button
if int(lcoor[2]) == 0:
    b_deco = False
    root.overrideredirect(False)  # no caption
else:
    b_deco = True
    root.overrideredirect(True) # yes caption
if int(lcoor[3]) == 0:
    b_topm = False
    root.attributes("-topmost", False)  # Not on top
else:
    b_topm = True
    root.attributes("-topmost", True)  # on top

app = Application(root)
app.mainloop()
