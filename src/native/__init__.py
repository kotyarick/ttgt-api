import platform
import ctypes

_library = ctypes.CDLL("src/native/" + ("backend.dll" if any(platform.win32_ver()) else "libbackend.so"))

def parse_schedule():
    _library.parse()

if __name__ == "__main__":
    parse_schedule()
