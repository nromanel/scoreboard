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
1 TBD: The BuiltIn Wifi on the RaspberryPi is configured to act as An Access Point that you can join with your phone
    - The Wireless network config does not push a default gateway - to allow internet access on the device to continue to function as normal
    - I still need to verify if this is actually doable. (Preventing breaking internet access on the device you're using to connect)
        -If it doesn't work I'll need to bundle the Bootstrap and Jquery libraries currently being called via CDN
    - I'm considering hosting a Public DNS entry that resolves to the RFC1918 Address the Rpi will have, to make it easier to connect
1 Flask app serves a basic HTML file with javascript behind it to allow you to control the signage
    - On load, the page will retrieve the current state of the board from the app
    - TBD: Insert Screenshot of HTML
1 An endpoint '/board' expects you to POST a JSON object for each part of the signage
   1 The object is then deconstructed into the relevent bits and pulsed out to the shift registers
1 Upon each POST - the state is persisted to a file to prevent data loss in the event of any power loss in the middle of a game.

# Wiring

Coming Soon

# Calculating Your Power Consumption

Coming Soon


