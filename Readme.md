1- Install all dependencies. Make sure to follow Octopus Sensing installation steps from its website
2- Make sure both tobii are connected to the local network
3- Make sure phone and laptop that are streaming brainflow also are connected to the local network
4- Make sure both shimmer are mapped to the serial port successfully
   follow these steps for linux:
      1- Pair bluetooth and serial port (Shimmer password: 1234)
      2- hcitool scan 
         note: It shows the macaddress of each shimmer device. for shimmer it is something like this 00:06:66:F0:95:95
      3- vim /etc/bluetooth/rfcomm.conf 
         note: for each shimmer should be a line like this on this file (rfcomm0, rfcomm1, ...): 
                  rfcomm0{ bind no; device 00:06:66:F0:95:95; channel 1; comment "serial port" } 
      4- Run the following command for each shimmer in a terminal. The number of rfcomm and macaddress should be alligned with the config file
          sudo rfcomm connect rfcomm0 00:06:66:F0:95:95 // This is for reading bluetooth data from a serial port
      5- Give permission to access to rfcomm
         sudo chmod 777 /dev/rfcomm*

5- Run the code:
   a) controller_conversation.py :  
       For running the conversation study. 
       Make sure the length of baseline and conversation in the code are alligned with your expectation (Line 21,22).
       Make sure all expected devices are in the list of device coordinator  
       Enter key to start a conversation, Space key to stop a conversation before its allocated time. 
       python run controller_conversation.py p01

   b) controller_finger_tracking.py : 
       For running the finger tracking study. 
       Make sure the length of baseline and task in the code are alligned with your expectation (Line 36, 37).
       Make sure all expected devices are in the list of device coordinator
       Space key for starting each task
       python run controller_finger_tracking.py 0 p01
          first argument: block   #Block number(0, 1, 2, or 3)
          second argument: pair   #pair id (p01, p02, ...)

   c) controller_tapping_tangram.py
       For running the tangram or finger tapping task
       Space: start data recording, enter end data recording for tangram. tapping is 60 seconds
       Make sure all expected devices are in the list of device coordinator
       python run controller_tapping_tangram.py F p01
          first argument: task "Task ID, F: finger tapping, T: Tangram"
          second argument pair "pair id (p01, p02, ...)"

   d) remote_recording.py
        It receives Markers from anywhere in network, on port 9331. You can change the number of port in code
        Make sure the list of sensors are based on your expectation


