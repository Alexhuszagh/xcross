# menuconfig

In order to get the proper configurations, we need the following:

- System configuration
    - None as Init system
    - None as /bin/sh
- Target packages
    - Disable BusyBox
- Filesystem images
    - Disable tar filesystem 

Then, run `make sdk`
