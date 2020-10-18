

import argparse
from pathlib import Path
import struct
from collections import deque, Counter

import gdal

import numpy as np
from blume import magic, farm

from matplotlib import pyplot as plt

class Shark:

    def __init__(self, path=None):
        

class Raster(magic.Ball):

    def set_args(self, args=None):

        parser = argparse.ArgumentParser()

        parser.add_argument('-row', type=int, default=450)
        parser.add_argument('-col', type=int, default=350)

        parser.add_argument('-size', type=int, default=1)

        parser.add_argument('-xblock', type=int, default=128)
        parser.add_argument('-yblock', type=int, default=128)

        parser.add_argument('filenames', nargs='*')

        args = parser.parse_args(None)

        self.update(args)

        self.filenames = deque(args.filenames)

    def make_index(self):

        name = Path(self.filenames[0])
        
        db = gdal.ogr.Open(self.filenames[0])

        print(db.name)

        print('layers:', db.GetLayerCount())

        layer = db.GetLayer(0)

        lookup = {}
        for fix in range(layer.GetFeatureCount()):
            feature = layer.GetFeature(fix + 1)
            lookup[(feature['row_nbr'], feature['col_nbr'])] = fix + 1

        return lookup


    async def run(self):

        db = gdal.ogr.Open(self.filenames[0])

        print(db.name)

        print('layers:', db.GetLayerCount())

        layer = db.GetLayer(0)

        print('building index')
        lookup = self.make_index(db)
        print('index done', len(lookup))

        area = np.zeros((500, 500))
        section = np.zeros((500, 500))

        gridsize = self.size +1
        grids = np.zeros((2, gridsize * self.xblock, gridsize * self.yblock), dtype=np.uint32)
    
        blocks = {}
        self.hits = 0

        #for fix in range(layer.GetFeatureCount()):
        for (row, col), fix in lookup.items():

            
            #await magic.sleep(self.sleep * 0.001)
            # see above -- things would be quicker with the index
            if row < self.row:
                continue

            if row > self.row + self.size:
                break

            if col < self.col or col > self.col + self.size:
                continue

            # fixme: need a mapping from {row, col} to feature index. this should speed things up
            # a fair bit.
            feature = layer.GetFeature(fix)

            area[row][col] += 1

            self.status = (fix, row, col)


            self.hits += 1
            block = feature.GetFieldAsBinary('block_data')


            form = '>16384H'

            channels = []
            #for slice in block[::2], block[1::2]:

            #for slice in block[3::4], block[2::4]:
            for start in range(2):
                aslice = block[start::2]
                channel = struct.unpack(form, aslice[:struct.calcsize(form)])
                channels.append(channel)

            #print(row, col, feature['block_key'], type(feature['block_key']),
            #      feature['rasterband_id'],
            #      feature['rrd_factor'])
            section[row][col] += 1


            row -= self.row
            col -= self.col
            size = self.size
            xb = self.xblock
            yb = self.yblock

            
            for grid, channel in zip(grids, channels):

                ch = np.array(channel).reshape((xb, yb))
                #plt.imshow(ch)
                #await self.put()

                grid[row * xb: (row + 1) * xb, col * yb: (col + 1) * yb] = ch

            
            #counts = Counter(arow)
            #print(len(counts))

        for ix, grid in enumerate(grids):
            plt.imshow(grid)

            plt.title(self.filenames[0] + f' channel: {ix}')
            plt.colorbar()
            await self.put()

        plt.imshow(area)
        plt.colorbar()
        await self.put()

        plt.imshow(section)
        plt.title('section')
        plt.colorbar()
        await self.put()
        
        self.filenames.rotate()


async def run(fm):

    await fm.start()
    await fm.run()

if __name__ == '__main__':


    ras = Raster()

    ras.set_args()

    fm = farm.Farm()
    fm.add(ras)

    fm.shep.path.append(ras)

    magic.run(run(fm))
