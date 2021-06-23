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
# Kernel Header Options
#
# BR2_KERNEL_HEADERS_4_4 is not set
# BR2_KERNEL_HEADERS_4_9 is not set
# BR2_KERNEL_HEADERS_4_14 is not set
# BR2_KERNEL_HEADERS_4_19 is not set
# BR2_KERNEL_HEADERS_5_4 is not set
BR2_KERNEL_HEADERS_5_10=y
# BR2_KERNEL_HEADERS_VERSION is not set
# BR2_KERNEL_HEADERS_CUSTOM_TARBALL is not set
# BR2_KERNEL_HEADERS_CUSTOM_GIT is not set
BR2_KERNEL_HEADERS_LATEST=y
BR2_DEFAULT_KERNEL_HEADERS="5.10.43"
BR2_PACKAGE_LINUX_HEADERS=y

#
# Kernel
#
# BR2_LINUX_KERNEL is not set
```

Then, run `make sdk`
