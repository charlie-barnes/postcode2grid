#!/usr/bin/env python
#-*- coding: utf-8 -*-

#grid2mif - 
#This application is free software; you can redistribute
#it and/or modify it under the terms of the GNU General Public License
#defined in the COPYING file

#2008-2010 Charlie Barnes.

import sys
import os
import gtk
import gobject
import time
import sys
from optparse import OptionParser
import sqlite3

class grid2mifActions():
    def __init__(self):
    
        self.cancel = False
        
        connection = sqlite3.connect('postcodes.sqlite')
        self.cursor = connection.cursor()
        
        if len(sys.argv) > 1:
        
            parser = OptionParser()
            parser.add_option("--postcode", dest="postcode",
                              help="Postcode to convert", metavar="CHAR")
            parser.add_option("--accuracy", dest="accuracy",
                              help="Accuracy of the grid reference in metres", metavar="CHAR")

            (options, args) = parser.parse_args()
            
            print self.process_postcode(postcode=options.postcode,
                                        accuracy=options.accuracy,
                                       )
            exit()

        #Load the widget tree
        builder = ""
        self.builder = gtk.Builder()
        self.builder.add_from_string(builder, len(builder))
        self.builder.add_from_file("ui.xml")

        signals = {
                   "mainQuit":self.main_quit,
                   "showAboutDialog":self.show_about_dialog,
                   "convertPostcodes":self.convert_postcodes,
                   "cancelConvert":self.cancel_convert,
                  }
        self.builder.connect_signals(signals)

        self.cancel_convert = False

        combo = gtk.combo_box_new_text()
        combo.append_text("1m")
        combo.append_text("10m")
        combo.append_text("100m")
        combo.append_text("1km")
        combo.append_text("10km")
        combo.append_text("100km")
        combo.set_active(0)
        self.builder.get_object("eventbox1").add(combo)
        combo.show()

        #Setup the main window
        self.main_window = self.builder.get_object("window1")
        self.main_window.show()
        
    def convert_postcodes(self, widget, var=None):
        self.builder.get_object("button1").hide()
        self.builder.get_object("button6").show()
        self.builder.get_object("button2").hide()
        self.builder.get_object("hbox1").hide()
    
        input_text_buffer = self.builder.get_object("textview1").get_buffer()
        input_start_iter = input_text_buffer.get_start_iter()
        input_end_iter = input_text_buffer.get_end_iter()
        
        input_text = input_text_buffer.get_text(input_start_iter, input_end_iter)
        total_count = len(input_text.split('\n'))

        output_text_buffer = self.builder.get_object("textview2").get_buffer()
        output_text = ""
        
        self.builder.get_object("progressbar1").show()
        
        count = 0
        
        for postcode in input_text.split('\n'):

            if self.cancel_convert:
                self.cancel_convert = False
                self.builder.get_object("progressbar1").hide()
                self.builder.get_object("progressbar1").set_fraction(0.0)
                self.builder.get_object("progressbar1").set_text("")
                self.builder.get_object("button1").show()
                self.builder.get_object("button6").hide()
                self.builder.get_object("button2").show()
                self.builder.get_object("hbox1").show()
                return
            
            grid = self.process_postcode(postcode, self.builder.get_object("eventbox1").get_child().get_active_text())
            
            if grid:
                output_text = ''.join([output_text, grid, "\n"])
            else:
                output_text = ''.join([output_text, "", "\n"])
                
            count = count + 1
                
            self.builder.get_object("progressbar1").set_fraction(float(count)/total_count)
            self.builder.get_object("progressbar1").set_text(''.join([str(count), " of ", str(total_count)]))

            while gtk.events_pending():
                gtk.main_iteration()
                        
        output_text_buffer.set_text(output_text)
        
        self.builder.get_object("progressbar1").hide()
        self.builder.get_object("button1").show()
        self.builder.get_object("button6").hide()
        self.builder.get_object("button2").show()
        self.builder.get_object("hbox1").show()
        
    def cancel_convert(self, widget):
        self.cancel_convert = True
        
    def process_postcode(self, postcode, accuracy):
    
        try:
            postcode = (postcode.upper(),)
            self.cursor.execute('SELECT x, y FROM postcodes WHERE postcode=? LIMIT 1', postcode)

            for row in self.cursor:
                x = str(row[0])
                y = str(row[1])

            en_matrix = {
                        "04":"SA",
                        "14":"SB",
                        "24":"SC",
                        "34":"SD",
                        "44":"SE",
                        "03":"SF",
                        "13":"SG",
                        "23":"SH",
                        "33":"SJ",
                        "43":"SK",
                        "02":"SL",
                        "12":"SM",
                        "22":"SN",
                        "32":"SO",
                        "42":"SP",
                        "01":"SQ",
                        "11":"SR",
                        "21":"SS",
                        "31":"ST",
                        "41":"SU",
                        "00":"SV",
                        "10":"SW",
                        "20":"SX",
                        "30":"SY",
                        "40":"SZ",
                        "54":"TA",
                        "64":"TB",
                        "63":"TG",
                        "53":"TF",
                        "52":"TL",
                        "62":"TM",
                        "51":"TQ",
                        "61":"TR",
                        "50":"TV",
                        "60":"TW",
                        }
        
            if accuracy == "1" or accuracy == "1m":
                accuracy = 6
            elif accuracy == "10" or accuracy == "10m":
                accuracy = 5
            elif accuracy == "100" or accuracy == "100m":
                accuracy = 4
            elif accuracy == "1000" or accuracy == "1km":
                accuracy = 3
            elif accuracy == "10000" or accuracy == "10km":
                accuracy = 2
            elif accuracy == "100000" or accuracy == "100km":
                accuracy = 1
            else:
                accuracy = 6

            return ''.join([en_matrix[''.join([x[:1], y[:1]])], x[1:accuracy], y[1:accuracy]])
        except:
            return False
              
    def main_quit(self, widget, var=None):
        self.cursor.close()
        gtk.main_quit()

    def show_about_dialog(self, widget):
       about=gtk.AboutDialog()
       about.set_name("postcode2grid")
       about.set_copyright("2010 Charlie Barnes")
       about.set_authors(["Charlie Barnes <charlie@cucaera.co.uk>"])
       about.set_license("postcode2grid is free software; you can redistribute it and/or modify it under the terms of the GNU General Public License as published by the Free Software Foundation; either version 2 of the Licence, or (at your option) any later version.\n\npostcode2grid is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU General Public License for more details.\n\nYou should have received a copy of the GNU General Public License along with postcode2grid; if not, write to the Free Software Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA  02111-1307  USA\n\nContains Ordnance Survey data © Crown copyright and database right 2010\nContains Royal Mail data © Royal Mail copyright and database right 2010")
       about.set_wrap_license(True)
       about.set_website("http://cucaera.co.uk/software/postcode2grid/")
       about.set_transient_for(self.builder.get_object("window1"))
       result=about.run()
       about.destroy()

if __name__ == '__main__':
    grid2mifActions()
    gtk.main()
    
