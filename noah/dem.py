"""
Simple viewer for a really big tif file.
"""


import argparse
import gdal
import curio

from blume import magic, farm

from matplotlib import pyplot as plt

class Dem(magic.Ball):


    async def start(self):

        self.band = gdal.Open(self.filename).GetRasterBand(0)

        self.xoff = 0
        self.yoff = 0

    async def run(self):

        square = band.ReadAsArray(
            xoff = self.xoff,
            yoff = self.yoff,
            win_xsize = self.size,
            win_ysize = self.size,)

        plt.imshow(square)

        self.put()

        self.xoff += self.size
        if self.xoff > self.band.Xsize:
            self.xoff = 0
            self.yoff += self.size

            if self.yoff >= self.size:
                self.yoff = 0

async def run(args):

    dem = Dem()

    dem.update(args)

    fm = farm.Farm()

    fm.add(dem)
    fm.shep.path.append(dem)

    await fm.start()
    await fm.run()

if __name__ == '__main__':


    parser = argparse.ArgumentParser()

    parser.add_argument('-filename')
    parser.add_argument('-size', type=int, default=1000)

    args = parser.parse_args()

    curio.run(run(args))

    
