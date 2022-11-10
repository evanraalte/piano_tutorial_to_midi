## Convert piano tutorials to sheet music

### The why
Did you ever see a recorded piano cover of a song that you'd like to learn? Also prefer to read sheet music instead of scrolling through videos looking for the correct notes? Then look no further, this application got you covered :).

However, if an arist sells the sheet music, please consider buying that instead. Making covers is a lot of work and they deserve the reward.

A picture says more than a thousand words, so a video must be even better!
![Alt Text](docs/demo.gif)

### What is it?
I have to admit, I don't have you fully covered. This tool can be of great help though! It provides a simple interface that helps you convert a youtube video of someone playing a piano tutorial e.g. [the video that I used in the demo](https://www.youtube.com/watch?v=aP2ZCzMQaRs) to a MIDI file. There are tools out there that do this as well, but I think mine has a more user friendly interface. You just follow the steps on the right and you are done!

### So what can I do with the MIDI file that your tool produces? 
Glad that you asked! There is a tool called  MuseScore (https://musescore.org/en) that allows one to import [midi files](https://musescore.org/en/handbook/3/midi-import), and convert them to sheet music. This process is called quantization.

The flow is therefore:
1. Find a video that you like and enter the url in the application, then you can download it.
2. Follow the steps in the tool, and convert the video to a midi file. The steps basically ensure that the tool know where to look for key presses, and which hand is doing the presses.
3. After conversion, you can import the midi file in MuseScore to generate sheet music. This is not extremely straight forward, as it needs to know how to map the notes to the sheet music. There are many tutorials on this, but experience is also a great teacher!
4. After you are done, you can print the generated sheets and learn the song :)

### Motivation
I started learning myself piano 3 years ago. My best motivation is to play songs that I like. Unfortunately some contemporary music is not available in sheet music. However, there are some nice folks that play songs and show you the bars (Guitar hero style) on YouTube, which is very useful! I still prefer to read sheet music, as it allows me to read the piece in my own pace, without screens, instead of having to scroll through a video. Unfortunately many people don't make/sell the accompanying sheet music. That is where I figured that I could jump in! There were some tools out there that did something similar, but there was none with a good user interface. Besides, I never did graphical user interfaces myself, so it was a good learning experience!

### Running the application
I have only tested this in Linux (Fedora 36) and [WSL 2.0](https://learn.microsoft.com/en-us/windows/wsl/install) (Ubuntu, with X11 forwarding). Please let me know if you have any issues running the application, and I will look into it!

To run the application on Linux, first install `Python3`, `pip` and the opencv dependencies:
```bash
sudo apt update && sudo apt upgrade -y
sudo apt install python3 
sudo apt install python3-pip
sudo apt install python3-opencv
sudo apt install libegl1
```
Then you can install the required Python packages:
```bash
pip3 install -r requirements.txt 
```

Optionally run it in venv (recommended):
```bash
python3 -m pip install virtualenv
python3 -m virtualenv env
source env/bin/activate
python3 -m pip install -r requirements.txt 
```

Finally run the application:
```bash
python3 main.py
```

