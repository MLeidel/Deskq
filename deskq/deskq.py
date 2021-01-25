"""
deskq is a desktop utility for Linux
Author: Michael Leidel (2020)
Jan 21, changed 'eval:' to '?'
"""
import webbrowser
import os
import sys
import subprocess
import urllib.parse
import time
from time import strftime
import gi

gi.require_version("Gtk", "3.0")
from gi.repository import Gtk, Gdk

try:
    from googlesearch import search
except ImportError:
    print("No module named 'google' found")


class Mainclass:
    """
        All the logic to process the GUI
    """

    def __init__(self):
        """
        Engage "builder", connect signals, display GUI -- Glade file
        """
        self.gladefile = "deskq.glade"
        self.builder = Gtk.Builder()
        self.builder.add_from_file(self.gladefile)
        self.builder.connect_signals(self)
        self.window = self.builder.get_object("window1")
        self.clipboard = Gtk.Clipboard.get(Gdk.SELECTION_CLIPBOARD)
        self.deco = False
        self.last_command = ""

        # read winmet.txt for window position, size, and decoration status
        if not os.path.exists("winmet.txt"):
            print("Missing winmet.txt")
            sys.exit(1)
        with open("winmet.txt", "r") as f_handle:
            pos = f_handle.readline().strip().split()
            dim = f_handle.readline().strip().split()
            dec = f_handle.readline().strip()
        self.window.move(int(pos[0]), int(pos[1]))  # xy
        self.window.set_default_size(int(dim[0]), int(dim[1]))
        if int(dec) == 0:
            self.deco = False
            self.window.set_decorated(False)
        else:
            self.deco = True
            self.window.set_decorated(True)

        with open("seaq.txt", "r") as f_handle:
            self.searchquery = f_handle.readline().strip()

        self.window.show()

    #### handler functions ####

    def on_window1_destroy(self, obj, data=None):
        """ program exit point """
        Gtk.main_quit()

    def on_btn_dlg_close_clicked(self, widget):
        """
        Close button on dialog box was clicked
        """
        dlg = self.builder.get_object("dialog_list")
        dlg.hide()

    def on_dlg_listbox_row_activated(self, widget, row):
        """
        Handle user click on row in listbox (urls or hist)
        """
        lbl = row.get_child()  # each listboxrow has a child label
        txt = lbl.get_text()
        if txt.startswith("http"):
            webbrowser.open(txt)  # open the URL
        else:
            stext = txt[0 : txt.find(", ")].rstrip()  # remove the date
            webbrowser.open(self.searchquery + urllib.parse.quote_plus(stext))

    def on_btn_action_clicked(self, widget):
        """
        Clicking the ■ button right side
        of entry field has two actions:
        1. Do whatever is in the entry field
        If nothing in entry field then:
            2. Do whatever is in the clipboard
                a. Save to urls.txt if its a URL
                b. Otherwise, save to clip.txt
        """
        obj = self.builder.get_object("searchtext")
        stext = obj.get_text()
        if stext != "":
            # then just run for whatever is in stext
            self.on_searchtext_activate(obj)
        else:
            # something was placed in clipboard?
            stext = self.clipboard.wait_for_text()
            if stext == "":
                return
            # assume it is either a URL or some text to save
            if stext.startswith("http"):
                # write to top of urls.txt
                self.writeurl(stext)
            else:
                with open("clip.txt", "a") as f_handle:
                    f_handle.write(stext + "\n\n")
        self.clipboard.set_text("", -1)

    def on_window1_key_press_event(self, widget, event):
        """ detect an arrow up/down keypress
            will put last_command into Entry field
        """
        if event.keyval == 65362 or event.keyval == 65364:
            oentry = self.builder.get_object("searchtext")
            oentry.set_text(self.last_command)

    def on_searchtext_activate(self, oentry):
        """
        This is the main program logic
        Parses Entry text, routes & executes different tasks
        """
        stext = oentry.get_text()
        self.last_command = stext  # save off this command

        if stext == "":  # nothing entered
            return

        if stext.lower() == "list":
            self.display_list_dlg("urls")

        elif stext.lower() == "hist":
            self.display_list_dlg("hist")

        elif stext.lower().startswith("http"):
            # write to top of urls.txt
            self.writeurl(stext)

        elif stext.lower().startswith("go:"):  # launch the URL
            stext = stext[3:]
            if stext.startswith("http"):
                self.writehist(stext)  # save to history (hist.txt)
                webbrowser.open(stext)
            else:
                return  # leave text in Entry

        elif stext[0] in ";.$":  # is it tag to open a URL or run a command?
            with open("serv.txt", "r") as f_handle:
                for srv in f_handle:
                    if srv[1:].startswith(stext[1:]):  # skip the "$;." tag
                        ary = srv.split(",")
                        cmd = ary[1].strip()
                        if cmd.startswith("http"):
                            webbrowser.open(cmd)  #  URL
                            # obj.set_text("")
                        else:
                            if " " in cmd:  # process with arguments
                                cmd = cmd.split(" ")
                                subprocess.Popen(cmd)
                            else:
                                subprocess.Popen([cmd])

        elif len(stext) > 1 and stext[1] == ":":  # launching a service request
            with open("serv.txt", "r") as f_handle:
                for srv in f_handle:
                    if srv.startswith(stext[:1]):  # starting letter a..z...
                        ary = srv.split(",")
                        webbrowser.open(ary[2] + stext[2:])
                        # obj.set_text("")

        elif stext.lower() == "sc":
            h = self.clipboard.wait_for_text()
            # info("Clipboard Saved","Use ec to view saved clipboards")
            with open("clip.txt", "a") as f_handle:
                f_handle.write(h + "\n\n")

        elif stext.lower() == "es":
            self.open_editor("serv.txt")

        elif stext.lower() == "ec":  # edit clips file
            self.open_editor("clip.txt")

        elif stext.lower() == "eh":  # edit history file
            self.open_editor("hist.txt")

        elif stext.lower() == "eu":  # edit saved urls urls.txt
            self.open_editor("urls.txt")

        elif stext.lower() == "ee":  # edit name of text editor
            self.open_editor("edit.txt")

        elif stext.lower() == "help":  # edit / view help file
            self.open_editor("help.txt")

        elif stext.lower().startswith("ex:"):
            stext = stext[3:]
            lcmd = stext.split(" ")  # convert the command line into a python List
            subprocess.Popen(lcmd)

        elif stext[0] == '?':
            stext = stext[1:]
            stext = eval(stext)
            stext = str(stext)
            self.clipboard.set_text(stext, -1)
            print(stext)
            oentry.set_text('?' + stext)
            return

        elif stext.startswith(">"):   # google search
            stext = stext[1:]
            self.writehist(stext)  # save to history (hist.txt)
            for j in search(stext, tld="com", num=5, stop=5, pause=3):
                # print(j)
                webbrowser.open(j)
                time.sleep(1)

        elif stext.lower() == "cap":
            if self.deco:
                self.deco = False
                self.window.set_decorated(False)
            else:
                self.deco = True
                self.window.set_decorated(True)

        elif stext.lower() == "winset":  # Exit Program
            # save window metrics into "winmet.txt" file
            try:
                pos = self.window.get_position()
                siz = self.window.get_size()
            except Exception as exep:
                raise exep
            try:
                with open("winmet.txt", "w") as f_handle:
                    f_handle.write(str(pos[0]) + " " + str(pos[1]) + "\n")
                    f_handle.write(str(siz[0]) + " " + str(siz[1]) + "\n")
                    f_handle.write(str(int(self.deco)) + "\n")
            except Exception as e:
                raise e

        elif stext.lower() == "x":  # Exit Program
            Gtk.main_quit()

        else:
            # Default => do a Google Search
            self.writehist(stext)  # save to history (hist.txt)
            webbrowser.open(self.searchquery + urllib.parse.quote_plus(stext))

        oentry.set_text("")

        # end of on_searchtext_activate

    ####    OTHER FUNCTIONS    ####

    def display_list_dlg(self, smode):
        """ ListBox in a Dialog content added here """
        dlg = self.builder.get_object("dialog_list")
        obj = self.builder.get_object("dlg_listbox")
        row = obj.get_row_at_index(0)
        while row is not None:
            obj.remove(row)
            row = obj.get_row_at_index(0)
        if smode == "urls":
            savedfile = "urls.txt"
            dlg.set_title("Saved URLs")
        else:
            savedfile = "hist.txt"
            dlg.set_title("Saved Searches")
        f_handle = open(savedfile, "r")
        items = f_handle.readlines()
        f_handle.close()
        if smode == "urls":
            items.reverse()
        for item in items:
            lble = Gtk.Label(item.strip(), xalign=0)
            obj.insert(lble, 0)

        dlg.show_all()
        dlg.run()
        dlg.hide()

    def writehist(self, sline):
        """ writes a line to the history file """
        f_handle = open("hist.txt", "a")
        f_handle.write(sline + ", " + strftime("%x") + "\n")
        f_handle.close()

    def writeurl(self, sline):
        """ writes a line to the top of urls.txt file """
        f_handle = open("urls.txt", "r")
        hold = f_handle.readlines()
        f_handle.close()
        with open("urls.txt", "w") as f_handle:
            f_handle.write(sline + "\n")
            for item in hold:
                f_handle.write(str(item))

    def open_editor(self, fin):
        """
        Open one of the apps text files for editing or viewing.
        fin is the name of the file
        """
        with open("edit.txt", "r") as f_handle:
            editp = f_handle.readline().strip()
        subprocess.Popen([editp, fin])


if __name__ == "__main__":
    main = Mainclass()
    Gtk.main()
