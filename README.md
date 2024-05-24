# Homemade Baseball Scoreboard - WORK IN PROGRESS

This project started after wondering how easily I could build a Scoreboard to support my son's Little League games.

Thanks to the wonderful guys over at [https://buildyourownscoreboard.wordpress.com/](https://buildyourownscoreboard.wordpress.com/) it was certainly doable and this project is 100% a derivative of their work.

The core of the Python to drive the LED's I found from someone attempting the same: [https://forums.raspberrypi.com/viewtopic.php?t=220728](https://forums.raspberrypi.com/viewtopic.php?t=220728)

This is still a work in progress. but the POC worked great!

# Components

While the original project above leveraged an Arduino, I skipped that step and leveraged the GPIO Pins on a RaspberryPi directly.
With that said, you'll need:

- RaspberryPi
- [TPIC6B595N](https://www.adafruit.com/product/457) Shift Registers
- LED Strips
    - What do you want to drive from the shift registers?
    - I used LED Strips cut to size purchased off ebay - [Like These](https://www.ebay.com/itm/283457840528?var=585286904293)
- Power Supplies
    - You'll need a 12V DC powersupply that can power all of your LED's + Rpi.
        - See below for how I performed my sizing
        - I ended up going with [https://www.amazon.com/gp/product/B0CBS4KTZ9/](https://www.amazon.com/gp/product/B0CBS4KTZ9/)
    - You'll also need a 5V transformer to step down that 12V and power your Rpi as well as the shift registers themselves:
        - [https://www.amazon.com/dp/B01M03288J](https://www.amazon.com/dp/B01M03288J)

# How it Works
1. TBD: The BuiltIn Wifi on the RaspberryPi is configured to act as An Access Point that you can join with your phone
    - The Wireless network config does not push a default gateway - to allow internet access on the device to continue to function as normal
    - I still need to verify if this is actually doable. (Preventing breaking internet access on the device you're using to connect)
        -If it doesn't work I'll need to bundle the Bootstrap and Jquery libraries currently being called via CDN
    - I'm considering hosting a Public DNS entry that resolves to the RFC1918 Address the Rpi will have, to make it easier to connect
1. Flask app serves a basic HTML file with javascript behind it to allow you to control the signage
    - On load, the page will retrieve the current state of the board from the app
    - TBD: Insert Screenshot of HTML
1. An endpoint '/board' expects you to POST a JSON object that contains all the elements of the signage
   - The object is then deconstructed into the relevent bits and pulsed out to the shift registers
   - When pulsing the data out to the shift registers - last chip first.
       - If Your registers are connected  1 -> 2 -> 3 -> 4
       - You need to send the data in order: 4, 3, 2, 1.  
1. Upon each POST - the state is persisted to a file to prevent data loss in the event of any power loss in the middle of a game. If this occurs, the board will load that last state when it comes back online!

# Wiring

- TBD: Diagram showing the wiring between the PS, RPi, Shift Registers, LEDs

# Configuring The Raspberry Pi

- TBD
    - Configure the Raspi To act as an AP
    - Install your needed python libs (RPi.GPIO & Flask)
    - Start the Flask app on boot
- Will attempt to incorporate a [Pi Zero W](https://www.raspberrypi.com/products/raspberry-pi-zero-w/) as part of the production build

# Calculating Your Power Consumption

- Depending on how big (or how small) you will build your display - you'll need to ensure you have enough power for all those LEDs

- In my case - it breaks out like this:
- The LED Strips are 12V - 300 LED;s) claim they will pull 5A
    - 5000ma / 300 = 17ma per LED
    - The Strips can be cut in groups of 3.
    - I'm planning each segment of my Numbers to be 9 LED's (Which creates a nice large footprint of: 12"x6").
        - That works out to be 63 LED's per Digit
    - 2 Digits each for the score, 1 Digit for the Inning (Not worried about Overtime)
        - 5 * 63 = 315 Leds
    - Balls, Outs, and Strikes will be represented by Squares of 9 LEDS each
        - 3 Balls, 2 Outs, 2 Strikes. 7 x 9 = 63
    - Total LEDs Required = 378 x 17ma = **6426ma**

-Powering Your LEDs isn't everything. The RaspberryPi (and the Shift Registers) are powered by 5V (Not 12V) so you'll need to step that down with anothe transformer, and account for that power draw.
    - Standard is to ensure you have 2.5A @ 5V to drive the Pi.
    - To Understand how much that results when stepping down from 12V:
        - Volts * Amps = Watts : 5 x 2.5 = 12.5w
        - Watts / Volts = Amps : 12.5 / 12 - **1.04A***

- Therefore I need just over 1 more Amp available from my 12V Transformer to drive the RaspberryPi.
    - (Not concerned with the 5v Draw from the shift registers... although maybe I should be?)

Total Power needed: **~7.5A @ 12V**

## Power on the go

Rhis project is meant to be portable and I don't expect to have AC Power on-site.
I'm plan to incorporate a 12V Lipo Battery. A 30Ah battery would give me ~3hrs at full load. One step at a time.

# Construction

Still Working on a design for the overall score board. I'm envisioing something around 5x2.5 ft.

I'm planning to build individual PCBs for each digit,
Each board will contain the LEDs (Obviously) Shift register, and headers for all the relevent connections (power and data).

By making the digits "modular", it should ease any future repair/replacement work.



