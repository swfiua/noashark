"""
Simple viewer for a really big tif file.
"""

import random
import argparse
import gdal
import curio
from collections import deque, Counter

from blume import magic, farm

from matplotlib import pyplot as plt

class Dem(magic.Ball):

    def set_args(self, args=None):

        parser = argparse.ArgumentParser()

        parser.add_argument('-filename')
        parser.add_argument('-size', type=int, default=1000)
        parser.add_argument('-xoff', type=int, default=0)
        parser.add_argument('-yoff', type=int, default=0)

        self.update(parser.parse_args(args))


    async def start(self):

        self.tif = gdal.Open(self.filename)

        band = self.tif.GetRasterBand(1)

        self.zoom = band.XSize // self.size


    async def run(self):

        # get a square from the image
        print(self.xoff, self.yoff, self.size)
        band = self.tif.GetRasterBand(1)

        while True:
            # random tiles
            self.xoff = min(random.randint(0, self.zoom) * self.size, band.XSize)
            self.yoff = min(random.randint(0, self.zoom) * self.size, band.YSize)
        
            square = band.ReadAsArray(
                xoff = self.xoff,
                yoff = self.yoff,
                win_xsize = self.size,
                win_ysize = self.size)

            if square is None:
                print(self.xoff, self.yoff)
                print(band.XSize, band.YSize)
                continue

            counts = Counter(square.flatten())
            print(counts.most_common(10))
            if len(counts) > 2:
                break

        plt.imshow(square, cmap=magic.random_colour())

        await self.put()

        #self.xoff += self.size
        #if self.xoff > band.XSize - self.size:
        #    self.xoff = 0
        #    self.yoff += self.size
        #
        #    if self.yoff >= band.YSize - self.size:
        #        self.yoff = 0

async def run():

    dem = Dem()
    dem.set_args()

    fm = farm.Farm()

    fm.add(dem)
    fm.shep.path.append(dem)

    await fm.start()
    await fm.run()

if __name__ == '__main__':

    magic.modes.rotate()
    curio.run(run())

    
