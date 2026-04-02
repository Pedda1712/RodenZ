import shutil
import numpy as np
import pickle
import os
from dataclasses import dataclass

import logging
logger = logging.getLogger(__name__)

# Saves a list in chunks to disk to not use all of the RAM
# Ideal for algorithms that access lists sequentially
# (like the Smoothing / Filtering algorithms :D)

@dataclass
class ListShelfInfo:
    chunk_size: int = 5000
    top_shelf: int = 0

class ListShelf:
    location: str
    info: ListShelfInfo
    info_file_path: str
    current_shelf_index: int = 0
    current_shelf: list[np.ndarray]
    write_barrier: bool = False

    def __init__(self, location: str, chunk_size = 5000):
        self.location = location
        self.info_file_path = f"{self.location}/ListShelfInfo.pickle"
        first_shelf_path = f"{self.location}/0.npy"
        if os.path.isdir(self.location):
            logger.debug(f"Location {self.location} exists, attempting shelf load ...")
            if not os.path.isfile(self.info_file_path):
                raise RuntimeError("Shelf folder exists, but no info file present")
            self.info = pickle.load(open(self.info_file_path, 'rb'))
            if not os.path.isfile(first_shelf_path):
                raise RuntimeError("Shelf folder and ListShelfInfo exists, but no shelf saved")
            self.current_shelf = [a for a in np.load(first_shelf_path)]
        else:
            logger.debug(f"Making new shelf at {self.location} ...")
            os.mkdir(self.location)
            self.info = ListShelfInfo()
            self.info.chunk_size = chunk_size
            pickle.dump(self.info, open(self.info_file_path, 'wb'), protocol=pickle.HIGHEST_PROTOCOL)
            self.current_shelf = []

    def load_shelf(self, index):
        if index == self.current_shelf_index:
            return
        self.flush()
        shelf_path = f"{self.location}/{index}.npy"
        logger.debug(f"Loading shelf component {shelf_path} ...")
        if not os.path.isfile(shelf_path):
            raise RuntimeError(f"Shelf {index} does not exist")
        self.current_shelf = [a for a in np.load(shelf_path)]
        self.current_shelf_index = index

    def load_top_shelf(self):
        if self.current_shelf_index != self.info.top_shelf:
            self.load_shelf(self.info.top_shelf)

    def __len__(self):
        self.load_top_shelf()
        saved = self.info.chunk_size * self.info.top_shelf
        in_ram = len(self.current_shelf)
        return saved + in_ram

    def _to_shelf_indices(self, index):
        if index == -1:
            index = self.__len__() - 1
        shelf_index = index // self.info.chunk_size
        in_array_index = index % self.info.chunk_size
        return shelf_index, in_array_index

    def __getitem__(self, index):
        shelf_index, in_array_index = self._to_shelf_indices(index)
        self.load_shelf(shelf_index)
        return self.current_shelf[in_array_index]

    def __setitem__(self, index, value):
        shelf_index, in_array_index = self._to_shelf_indices(index)
        self.load_shelf(shelf_index)
        self.write_barrier = True
        self.current_shelf[in_array_index] = value

    def append(self, value):
        self.load_top_shelf()
        if len(self.current_shelf) >= self.info.chunk_size:
            self.flush()
            self.info.top_shelf += 1
            self.current_shelf_index += 1
            self.current_shelf = []
        self.current_shelf.append(value)
        self.write_barrier = True

    def _remove_top_shelf(self):
        self.load_top_shelf()
        if len(self.current_shelf) != 0:
            raise RuntimeError("Trying to remove non-empty top shelf")
        shelf_path = f"{self.location}/{self.current_shelf_index}.npy"
        if os.path.isfile(shelf_path): # if top shelf was only in ram, it wasnt saved yet
            os.remove(shelf_path)
        self.info.top_shelf -= 1
        self.load_top_shelf()

    def pop(self):
        self.load_top_shelf()
        if len(self.current_shelf) == 0:
            self._remove_top_shelf()
        self.write_barrier = True
        value = self.current_shelf.pop()
        if len(self.current_shelf) == 0:
            self.flush()
        return value

    def clear(self):
        logger.debug(f"Removing shelf {self.location} ...")
        shutil.rmtree(self.location)
        
    def flush(self):
        pickle.dump(self.info, open(self.info_file_path, 'wb'), protocol=pickle.HIGHEST_PROTOCOL)
        shelf_path = f"{self.location}/{self.current_shelf_index}.npy"
        if self.write_barrier and not self.info.top_shelf < self.current_shelf_index:
            np.save(open(shelf_path, "wb"), np.array(self.current_shelf))
        self.write_barrier = False
