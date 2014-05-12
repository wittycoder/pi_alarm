#Initial Raspberry Pi setup:
1) Install Raspbian (or your choice of distro)
2) On first boot, intial setup on monitor/keyboard with network connection
- First boot set the following options in Raspi-config
    - Expand Filesystem - Select and let it do it's thing
    - Change User Password - up to you...
    - Enable boot to Desktop/Scratch - Leave default boot to command line unless you need a desktop
    - Internationalization options -
        - Change Locale - up to you
        - Change timezone - Change this to be your local timezone (kind of important for clock)
        - Change Keyboard layout - up to you
    - Enable Camera - leave off
    - Add to Rastrack - up to you
    - Overclock - up to you, I leave it off
    - Advanced options -
        - Overscan - set to work correctly with your HDMI monitor
        - Hostname - set a hostname for the network (makes network setup easier)
        - Memory split - up to you (doesn't really matter if no display for clock)
        - SSH - enable SSH for remote access for later setup (can disable after setup if you just want the web interface)
        - SPI - disable
        - Audio - Generally Auto works fine, but choose 3.5mm if you want for a speaker
        - Update - You can update the tool now if you want, not required if you just installed
3) On reboot, note the IP address then we can do all of our other work remotely via ssh if desired.
    advanced: DHCP reservation:
    - login - pi/<password from earlier, default:raspberry>
    - get your MAC address - run 'ifconfig -a' and for ethernet built in look at eth0 for HWaddr
    - set this MAC as a DHCP reservation in your router if you want to have a reserved IP on your network
    - if you set a different address either bounce the interface or reboot
        - $ sudo dhclient -v -r eth0
        - $ sudo dhclient -v eth0
            OR
        - $ sudo reboot

4) Update everything - sudo apt-get dist-upgrade, then another reboot is likely going to be required

5) Run the setup script
    - sudo ./setup/setup_clock.sh
    - Some of the things in this script:
        - Setup flask for web service
        - Install sqlite3 for DB used in daemon as well as flask web service
        - Install init.sh script

6) Navigate to the IP address found in step #3 that you changed or noted.  You should see the clock web interface.

Notes/TODOs
-Add LEDs to show it off
-format alarm info
-add button to bring in new form to add alarm
-update daemon to run and check alarm time / frequency
-
-Android app to set/get alarms

