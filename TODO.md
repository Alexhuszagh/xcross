# Entrypoint

- Specify /bin/bash as the entrypoint.
- Can specify paths as a resultr in there.
    - Need a CMake wrapper script, I believe.
    - Need to edit paths in scripts, IIRC.

# Cmake Wrapper Script

- Should be highest priority in the path
    - Should auto-provide the toolchain file.
    - Should add /opt/bin to the .profile.
        - Copy script to /opt/bin
        - Should actually make all symlinks there too...

- `export PATH=/opt/bin:"$PATH"`

# Single Layer Images

- Use single-layer images
- https://docs.docker.com/develop/develop-images/dockerfile_best-practices/

```dockerfile
# This results in a single layer image
FROM scratch
COPY --from=build /bin/project /bin/project
ENTRYPOINT ["/bin/project"]
CMD ["--help"]
```

# Tests

- Need tests to ensure that our scripts work.
