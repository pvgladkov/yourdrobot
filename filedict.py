import os
import json
from collections import UserDict


class FileDict(UserDict):
    def __init__(self, filename):
        self.data = {}
        self._file = filename
        if os.path.exists(self._file):
            with open(self._file) as f:
                self.data = json.load(f)

    def __setitem__(self, key, item):
        self.data[key] = item
        with open(self._file, 'w')as f:
            msg = json.dumps(
                self.data,
                indent=4,
                separators=(',', ': '),
                ensure_ascii=False)
            f.write(msg)