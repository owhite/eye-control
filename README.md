![alt tag](http://i.imgur.com/hB5c3m5.jpg)

Arduino driven [robotic eyeball](http://i.imgur.com/hB5c3m5.jpg). 

This uses arduino driven servos, laser cut metal parts ([site for my laser](http://nilno.com)), gamepad control via serial using pygame. 

Another [view](http://i.imgur.com/eNS1air.jpg). 

A [video](https://www.youtube.com/watch?v=fJ02YDaqGDI) of device, and 

CAD drawings [here](http://i.imgur.com/yjqVxtr.png) and [here](http://i.imgur.com/JlEJc0a.png) 

The following is the tricky parts to note:  
* plug in your arduino, figure out which port it's using. If you use the arduino IDE check Tools-->port. Then add that to your python code.  
* the [sketch](https://github.com/owhite/eye-control/tree/master/servo) has a couple other things like a sensor to detect movement, just remove that portion if you dont need.

BACKGROUND

I've been working on this for a few years. The physical device took a while to design - just a lot of iterations going from original design to several adjustments to how things fit. Then for a while I explored computer vision with openCV. I set up blob tracking wth a web camera and then ran into a big set of headaches. Going from a position in a visual field to accurately pointing the eye is not trivial because the camera was not -in- the eye. Eventually I put a laser pointer in a larger version and that was very instructive. It helped me realize the geometry of the system is such that you realize that a sweep in the x direction does not result in the pointer sweeping a straight line across the wall. So basically there is no linear relationship between any position of the eye and an XY field in computer space.
After that I made some software with tkinter to record movements of a game controller. This achieves a lot of really life like movements and I like that a lot more. You can see from the current incarnation of the board that I have a PIR movement detector, so currently I'm getting it to wake up when it detects movement, and I'll call it finished at that point.