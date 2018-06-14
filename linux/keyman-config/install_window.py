#!/usr/bin/python3

# Install confirmation with details window

import os.path
import pathlib
import subprocess
import webbrowser
import tempfile
import gi
gi.require_version('Gtk', '3.0')
gi.require_version('WebKit', '3.0')
from gi.repository import Gtk, WebKit
from distutils.version import StrictVersion
from install_kmp import install_kmp, extract_kmp, get_metadata
from list_installed_kmp import get_kmp_version
from kmpmetadata import get_fonts
from welcome import WelcomeView
from uninstall_kmp import uninstall_kmp
from get_kmp import get_download_folder
from check_mime_type import check_mime_type

class InstallKmpWindow(Gtk.Window):

    def __init__(self, kmpfile):
        print("kmpfile:", kmpfile)
        self.kmpfile = kmpfile
        keyboardid = os.path.basename(os.path.splitext(kmpfile)[0])
        installed_kmp_ver = get_kmp_version(keyboardid)
        if installed_kmp_ver:
            print("installed kmp version", installed_kmp_ver)

        windowtitle = "Installing keyboard/package " + keyboardid
        Gtk.Window.__init__(self, title=windowtitle)

        self.set_border_width(3)

        vbox = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=6)

        mainhbox = Gtk.Box()

        with tempfile.TemporaryDirectory() as tmpdirname:
            extract_kmp(kmpfile, tmpdirname)
            info, system, options, keyboards, files = get_metadata(tmpdirname)
            self.kbname = keyboards[0]['name']
            self.checkcontinue = True

            if installed_kmp_ver:
                if info['version']['description'] == installed_kmp_ver:
                    dialog = Gtk.MessageDialog(self, 0, Gtk.MessageType.QUESTION,
                        Gtk.ButtonsType.YES_NO, "Keyboard is installed already")
                    dialog.format_secondary_text(
                        "The " + self.kbname + " keyboard is already installed at version " + installed_kmp_ver +
                            ". Do you want to uninstall then reinstall it?")
                    response = dialog.run()
                    dialog.destroy()
                    if response == Gtk.ResponseType.YES:
                        print("QUESTION dialog closed by clicking YES button")
                        uninstall_kmp(keyboardid)
                    elif response == Gtk.ResponseType.NO:
                        print("QUESTION dialog closed by clicking NO button")
                        self.checkcontinue = False
                else:
                    try:
                        print("package version", info['version']['description'])
                        print("installed kmp version", installed_kmp_ver)
                        if StrictVersion(info['version']['description']) <= StrictVersion(installed_kmp_ver):
                            dialog = Gtk.MessageDialog(self, 0, Gtk.MessageType.QUESTION,
                                Gtk.ButtonsType.YES_NO, "Keyboard is installed already")
                            dialog.format_secondary_text(
                                "The " + self.kbname + " keyboard is already installed with a newer version " + installed_kmp_ver +
                                    ". Do you want to uninstall it and install the older version" + info['version']['description'] + "?")
                            response = dialog.run()
                            dialog.destroy()
                            if response == Gtk.ResponseType.YES:
                                print("QUESTION dialog closed by clicking YES button")
                                uninstall_kmp(keyboardid)
                            elif response == Gtk.ResponseType.NO:
                                print("QUESTION dialog closed by clicking NO button")
                                self.checkcontinue = False
                    except:
                        print("exception")
                        pass

            image = Gtk.Image()
            if options and "graphicFile" in options:
                image.set_from_file(os.path.join(tmpdirname, options['graphicFile']))
            else:
                image.set_from_file("defaultpackage.gif")

            mainhbox.pack_start(image, False, False, 0)

            self.page1 = Gtk.Box()
            self.page1.set_border_width(10)

            grid = Gtk.Grid()
            self.page1.add(grid)

            label1 = Gtk.Label()
            label1.set_text("Keyboard layouts:   ")
            label1.set_halign(Gtk.Align.END)
            grid.add(label1)
            prevlabel = label1
            label = Gtk.Label()
            keyboardlayout = ""
            for kb in keyboards:
                if keyboardlayout != "":
                    keyboardlayout = keyboardlayout + "\n"
                keyboardlayout = keyboardlayout + kb['name']
            label.set_text(keyboardlayout)
            label.set_halign(Gtk.Align.START)
            label.set_selectable(True)
            grid.attach_next_to(label, label1, Gtk.PositionType.RIGHT, 1, 1)

            fonts = get_fonts(files)
            if fonts:
                label2 = Gtk.Label()
                # Fonts are optional
                label2.set_text("Fonts:   ")
                label2.set_halign(Gtk.Align.END)
                grid.attach_next_to(label2, prevlabel, Gtk.PositionType.BOTTOM, 1, 1)
                prevlabel = label2
                label = Gtk.Label()
                fontlist = ""
                for font in fonts:
                    if fontlist != "":
                        fontlist = fontlist + "\n"
                    if font['description'][:5] == "Font ":
                        fontdesc = font['description'][5:]
                    else:
                        fontdesc = font['description']
                    fontlist = fontlist + fontdesc
                label.set_text(fontlist)
                label.set_halign(Gtk.Align.START)
                label.set_selectable()
                grid.attach_next_to(label, label2, Gtk.PositionType.RIGHT, 1, 1)

            label3 = Gtk.Label()
            label3.set_text("Package version:   ")
            label3.set_halign(Gtk.Align.END)
            grid.attach_next_to(label3, prevlabel, Gtk.PositionType.BOTTOM, 1, 1)
            prevlabel = label3
            label = Gtk.Label()
            label.set_text(info['version']['description'])
            label.set_halign(Gtk.Align.START)
            label.set_selectable()
            grid.attach_next_to(label, label3, Gtk.PositionType.RIGHT, 1, 1)

            if info and 'author' in info:
                label4 = Gtk.Label()
                label4.set_text("Author:   ")
                label4.set_halign(Gtk.Align.END)
                grid.attach_next_to(label4, prevlabel, Gtk.PositionType.BOTTOM, 1, 1)
                prevlabel = label4
                label = Gtk.Label()
                label.set_markup("<a href=\"" + info['author']['url'] + "\">" + info['author']['description'] + "</a>")
                label.set_halign(Gtk.Align.START)
                label.set_selectable()
                grid.attach_next_to(label, label4, Gtk.PositionType.RIGHT, 1, 1)


            if info and 'website' in info:
                label5 = Gtk.Label()
                # Website is optional and may be a mailto for the author
                label5.set_text("Website:   ")
                label5.set_halign(Gtk.Align.END)
                grid.attach_next_to(label5, prevlabel, Gtk.PositionType.BOTTOM, 1, 1)
                prevlabel = label5
                label = Gtk.Label()
                label.set_markup("<a href=\"" + info['website']['description'] + "\">" + info['website']['description'] + "</a>")
                label.set_halign(Gtk.Align.START)
                label.set_selectable()
                grid.attach_next_to(label, label5, Gtk.PositionType.RIGHT, 1, 1)

            if info and 'copyright' in info:
                label6 = Gtk.Label()
                label6.set_text("Copyright:   ")
                label6.set_halign(Gtk.Align.END)
                grid.attach_next_to(label6, prevlabel, Gtk.PositionType.BOTTOM, 1, 1)
                label = Gtk.Label()
                label.set_text(info['copyright']['description'])
                label.set_halign(Gtk.Align.START)
                label.set_selectable()
                grid.attach_next_to(label, label6, Gtk.PositionType.RIGHT, 1, 1)

            self.page2 = Gtk.Box()
            #self.page2.set_border_width(10)
            s = Gtk.ScrolledWindow()
            webview = WebKit.WebView()
            webview.connect("mime-type-policy-decision-requested", check_mime_type)

            if options and "readmeFile" in options:
                readme_file = os.path.join(tmpdirname, options['readmeFile'])
            else:
                readme_file = os.path.join(tmpdirname, "readme.htm")
            if os.path.isfile(readme_file):
                readme_uri = pathlib.Path(readme_file).as_uri()
                webview.load_uri(readme_uri)
                s.add(webview)
                self.page2.pack_start(s, True, True, 0)

                self.notebook = Gtk.Notebook()
                self.notebook.set_tab_pos(Gtk.PositionType.BOTTOM)
                mainhbox.pack_start(self.notebook, True, True, 0)
                self.notebook.append_page(
                    self.page1,
                    Gtk.Label('Details'))
                self.notebook.append_page(
                    self.page2,
                    Gtk.Label('README')
        )
            else:
                mainhbox.pack_start(self.page1, True, True, 0)
        vbox.pack_start(mainhbox, True, True, 0)

        hbox = Gtk.Box(spacing=6)
        #hbox.set_halign(Gtk.Align.FILL)
        vbox.pack_start(hbox, False, False, 0)

        button = Gtk.Button.new_with_mnemonic("_Install")
        button.connect("clicked", self.on_install_clicked)
        hbox.pack_start(button, False, False, 0)

        button = Gtk.Button.new_with_mnemonic("_Cancel")
        button.connect("clicked", self.on_cancel_clicked)
        hbox.pack_end(button, False, False, 0)

        self.add(vbox)
        self.resize(635, 270)

    def on_install_clicked(self, button):
        print("Installing keyboard")
        install_kmp(self.kmpfile, True)
        keyboardid = os.path.basename(os.path.splitext(self.kmpfile)[0])
        welcome_file = os.path.join("/usr/local/share/doc/keyman", keyboardid, "welcome.htm")
        if os.path.isfile(welcome_file):
            uri_path = pathlib.Path(welcome_file).as_uri()
            print(uri_path)
            w = WelcomeView(uri_path, self.kbname)
            w.resize(800, 600)
            w.show_all()
        #    view.load_uri(uri_path)
        else:
            dialog = Gtk.MessageDialog(self, 0, Gtk.MessageType.INFO,
                Gtk.ButtonsType.OK, "Keyboard " + self.kbname + " installed")
            #dialog.format_secondary_text(
            #    "And this is the secondary text that explains things.")
            dialog.run()
            print("INFO dialog closed")
            dialog.destroy()
        self.close()

    def on_cancel_clicked(self, button):
        print("Cancel install keyboard")
        self.close()
