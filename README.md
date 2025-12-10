Huawei-style Gesture File Transfer - Prototype
===============================================

What this is
------------
A prototype that demonstrates a Huawei-like "grab & drop" gesture file transfer:
- Use your webcam to detect hand gestures (open palm / fist) with MediaPipe.
- Make a fist to "grab" the sample image; open your palm to "drop" and send it to the receiver.
- Includes a Pygame window that visually follows the grabbed image for the "wow" effect.
- File transfer happens over TCP sockets to a receiver running server.py.

This is a prototype for learning & experimentation, not a production implementation.

Files
-----
- server.py       : Receiver. Run on the machine that will receive files.
- client.py       : Sender. Run on the machine with the webcam.
- gestures.py     : MediaPipe-based hand gesture detector.
- ui.py           : Pygame visual animation for grab/drop.
- sample.png      : Sample image to send.
- requirements.txt: Python packages to install.

Requirements
------------
- Python 3.8+
- Install dependencies:
    pip install -r requirements.txt

How to run
----------
1) On the RECEIVER machine (where you want the file to be saved), run:
    python server.py

   This will listen on port 5001 and save incoming file as 'received_<originalname>'.

2) On the SENDER machine (your webcam machine), edit client.py and set:
    SERVER_IP = "<receiver_ip_address>"

   Then run:
    python client.py

3) Use webcam window:
   - Show an OPEN PALM to idle.
   - Make a FIST to 'grab' the image (it will appear in the animation window and follow your hand).
   - Show OPEN PALM again to 'drop' — the file will be sent to the receiver.

Notes & Tips
-------------
- Ensure both machines are on the same local network.
- If firewall blocks the port, allow Python / port 5001 for testing.
- If MediaPipe fails to install on some platforms, check official docs.

License
-------
MIT - for educational use.

Enjoy! 🚀

Demo Video
----------
👉 Watch the demo here:  
**[Click to view demo video]https://drive.google.com/file/d/1a6JqfwHMIDpqd9taqJ1ir3yoiKgyfr2W/view?usp=drive_link**

