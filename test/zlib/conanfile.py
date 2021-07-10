from conans import ConanFile, Meson

class ZlibExec(ConanFile):
    name = "zlibexec"
    version = "0.1"
    settings = "os", "compiler", "build_type", "arch"
    generators = "cmake", "pkg_config"
    requires = "zlib/1.2.11"

    def build(self):
        meson = Meson(self)
        meson.configure(build_folder="build")
        meson.build()
