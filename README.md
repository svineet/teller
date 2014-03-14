teller
======

A IRC bot to tell people things when they come online.

Usage
-----

Install requirements:
    
    sudo pip install -r requirements.txt

Then run:

    python bot.py

It'll ask for the channel(only one channel supported as of now) and the pickle file name. The data is stored in this file, if you don't enter anything by default it's "tellerbot_data.pickle". Through this data persists over runs and reruns.
Fork and contribute! :)

Commands
--------

Tell someone:

    tellerbot tell svineet you're awesome

When svineet comes online, tellerbot will tell him this message.

Tell you when someone comes online(not yet functional):

    tellerbot tellme svineet

It'll ping you when svineet come online.
