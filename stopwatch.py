#!/usr/bin/env python

import os
from threading import Thread
import time, datetime
import Tkinter

class Stopwatch:
    """Generic stopwatch class. Controls starting and keeping track of
    the time."""

    def __init__(self):
        """Initialize Stopwatch instance."""
        self.first_time = 0.
        self.curr_time = 0.
        self.running = False
        self.thread = None

    def start(self, string_var):
        """Spawn a new thread to start the stopwatch."""
        self.running = True
        self.first_time = datetime.datetime.now()
        self.thread = StopwatchThread(self, string_var)
        self.thread.start()

    def stop(self, string_var):
        """Stop the subthread to stop the stopwatch."""
        self.running = False
        self.thread._Thread__stop()
        self.first_time = 0.

    def toggle(self, string_var):
        """Toggle state of stopwatch."""
        if self.running:
            self.stop(string_var)
        else:
            self.start(string_var)

class StopwatchThread(Thread):
    """Thread for stopwatch counting."""

    def __init__(self, watch, string_var):
        """Initialize the StopwatchThread instance."""
        Thread.__init__(self)
        self.watch = watch
        self.string_var = string_var

    def run(self):
        """Main thread method."""
        while True:
            self.watch.curr_time = datetime.datetime.now()
            the_time = self.watch.curr_time - self.watch.first_time
            #self.string_var.set(time.strftime("%H:%M:%S", time.gmtime(the_time)))
            hours = the_time.seconds/(60*60)
            minutes = the_time.seconds/60
            seconds = the_time.seconds%60
            self.string_var.set("%02i:%02i:%02i.%02i" % (hours, minutes, seconds, the_time.microseconds/1e4))
            time.sleep(0.005)
            if not self.isAlive():
                break

class TkStopwatch:
    """Class for Tk version of the stopwatch."""

    def __init__(self, parent, stopwatch):
        """Initialize and pack all relevant widgets."""
        self.parent = parent
        self.stopwatch = stopwatch
        self.time_string = Tkinter.StringVar(value="00:00:00.00")
        self.startstop_string = Tkinter.StringVar(value="Start")

        # Current time
        self.lTime = Tkinter.Label(self.parent, textvariable=self.time_string, font=("FreeSans", 20))
        self.lTime.pack(side=Tkinter.LEFT)

        # Starts/stops the stopwatch
        self.bStartStop = Tkinter.Button(self.parent, textvariable=self.startstop_string, command=self.toggle)
        self.bStartStop.pack(side=Tkinter.LEFT)

        # Quit button
        self.bQuit = Tkinter.Button(self.parent, text="Quit", fg="red", command=self.quit)
        self.bQuit.pack(side=Tkinter.LEFT)

    def toggle(self):
        """Toggle stopwatch state."""
        if self.stopwatch.running:
            self.startstop_string.set("Start")
        else:
            self.startstop_string.set("Stop")
        self.stopwatch.toggle(self.time_string)

    def quit(self):
        """Quit program."""
        self.stopwatch.stop(self.time_string)
        self.parent.quit()

if __name__ == "__main__":
    watch = Stopwatch()
    tkroot = Tkinter.Tk()
    tkroot.title("Stopwatch")
    tkwatch = TkStopwatch(tkroot, watch)
    tkroot.mainloop()
