
Arduino driven [robotic eyeball](http://i.imgur.com/hB5c3m5.jpg). 

This uses arduino driven servos, laser cut metal parts ([site for my laser](http://nilno.com)), gamepad control via serial using pygame. 

Another [view](http://i.imgur.com/eNS1air.jpg). 

A [video](https://www.youtube.com/watch?v=fJ02YDaqGDI) of device, and 

CAD drawings [here](http://i.imgur.com/yjqVxtr.png) and [here](http://i.imgur.com/JlEJc0a.png) 

The following is the tricky parts to note:  
* plug in your arduino, figure out which port it's using. If you use the arduino IDE check Tools-->port. Then add that to your python code.  
* the [sketch](https://github.com/owhite/eye-control/tree/master/servo) has a couple other things like a sensor to detect movement, just remove that portion if you dont need.  