# menuconfig

In order to get the proper configurations, we need the following:

- System configuration
    - None as Init system
    - None as /bin/sh
- Target packages
    - Disable BusyBox
- Filesystem images
    - Disable tar filesystem 

In addition, you need to disable `Kernel`, `Linux Kernel Extensions`, and `Linux Kernel Tools`, and set them to this:

```text
#
# Kernel
#
# BR2_LINUX_KERNEL is not set
```

Then, run `make sdk`
