
Arduino driven [robotic eyeball](http://i.imgur.com/hB5c3m5.jpg). 

Arduino driven servos, laser cut metal parts ([site for my laser](http://nilno.com)), gamepad control via serial using pygame. 

Another [view](http://i.imgur.com/eNS1air.jpg). 

A [video](https://www.youtube.com/watch?v=fJ02YDaqGDI) of device, and drawings [here](http://i.imgur.com/JlEJc0a.png) and 

[here](http://i.imgur.com/yjqVxtr.png) of metal parts. 

The following is the tricky parts to note:  
* plug in your arduino, figure out which port it's using. If you use the arduino IDE check Tools-->port. Then add that to your python code.  
* the code I showed actually sends commands to four servos, you may need to modify for your purposes  
* the sketch has a couple other things like a sensor to detect movement, just remove that portion if you dont need.  