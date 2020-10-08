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

        self.tif = gdal.Open(self.filename)
        return

    async def run(self):

        # get a square from the image
        print(self.xoff, self.yoff, self.size)
        band = self.tif.GetRasterBand(1)
        square = band.ReadAsArray(
            xoff = self.xoff,
            yoff = self.yoff,
            win_xsize = self.size,
            win_ysize = self.size)
        print(square)
        plt.imshow(square)

        await self.put()

        self.xoff += self.size
        if self.xoff > band.XSize - self.size:
            self.xoff = 0
            self.yoff += self.size

            if self.yoff >= band.YSize - self.size:
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
    parser.add_argument('-xoff', type=int, default=0)
    parser.add_argument('-yoff', type=int, default=0)

    args = parser.parse_args()

    curio.run(run(args))

    
