from abc import ABC, abstractmethod
import glob
from typing import List, Dict


class BaseReader(ABC):
    def __init__(self):
        pass

    @abstractmethod
    def read(self, path) -> List[Dict]:
        pass

    def read_directory(self, path, file_mask="*.xml"):
        full_path = path + "/" + file_mask
        for filename in glob.glob(full_path):
            for entry in self.read(filename):
                yield entry
