

import argparse
from pathlib import Path
import struct
from collections import deque, Counter
import functools

import gdal

from PIL import Image

import numpy as np
from blume import magic, farm

from matplotlib import pyplot as plt


class Raster(magic.Ball):

    def set_args(self, args=None):

        parser = argparse.ArgumentParser()

        parser.add_argument('-row', type=int, default=450)
        parser.add_argument('-col', type=int, default=350)

        parser.add_argument('-size', type=int, default=1)

        parser.add_argument('-xblock', type=int, default=128)
        parser.add_argument('-yblock', type=int, default=128)

        parser.add_argument('filenames', nargs='*')

        args = parser.parse_args(args)

        self.update(args)

        self.filenames = deque(args.filenames)


    @functools.lru_cache(maxsize=None)
    def get_index(self, name):

        name = Path(self.filenames[0])
        
        db = gdal.ogr.Open(self.filenames[0])

        print(db.name)

        print('layers (should only be one):', db.GetLayerCount())

        layer = db.GetLayer(0)

        lookup = {}
        for fix in range(layer.GetFeatureCount()):
            feature = layer.GetFeature(fix + 1)
            print(feature.keys())
            lookup[(feature['row_nbr'], feature['col_nbr'])] = fix + 1

        # just for curiosity
        print(type(feature))
        return lookup


    async def tile_map(self, lookup):

        keys = list(lookup.keys())
        print(keys)
        rmin, rmax = min(x[0] for x in keys), max(x[0] for x in keys)
        cmin, cmax = min(x[1] for x in keys), max(x[1] for x in keys)

        area = np.zeros((2 + rmax, 2 + cmax))
        print(area.shape)
        print(rmin, rmax)
        print(cmin, cmax)
        for row, col in lookup.keys():
            #print(row, col)
            area[row-rmin][col-cmin] += 1
        plt.imshow(area)
        await self.put()

    async def run(self):

        db = gdal.ogr.Open(self.filenames[0])

        name = db.name
        import time
        t1 = time.time()
        lookup = self.get_index(name)
        t2 = time.time()
        print('get index time', t2-t1)

        await self.tile_map(lookup)
        #return
        
        keys = list(lookup.keys())
        print(min(keys[0]), max(keys[0]))
        print(min(keys[1]), max(keys[1]))

        print('layers:', db.GetLayerCount())

        layer = db.GetLayer(0)


        area = np.zeros((500, 500))
        section = np.zeros((500, 500))

        gridsize = self.size +1
    
        blocks = {}
        self.hits = 0

        xb = self.xblock
        yb = self.yblock

        grids = [
            np.zeros((gridsize * xb, gridsize * yb, 4), dtype=np.uint32),
            np.zeros((gridsize * xb, gridsize * yb), dtype=np.uint32),
            np.zeros((gridsize * xb, gridsize * yb), dtype=np.uint32)]

        #for fix in range(layer.GetFeatureCount()):
        for (row, col), fix in lookup.items():
            print(row, col)
            
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
            t1 = time.time()
            feature = layer.GetFeature(fix)
            t2 = time.time()
            print('get feature time', t2-t1)
            area[row][col] += 1

            self.status = (fix, row, col)


            self.hits += 1
            block = feature.GetFieldAsBinary('block_data')


            form = '>16384H'

            channels = []
            #for slice in block[::2], block[1::2]:

            #for slice in block[3::4], block[2::4]:

            channel = np.array(struct.unpack(f'{len(block)}B', block))
            rgba = channel[:xb*yb*4].reshape((xb, yb, 4))
            channels.append(rgba)

            img = Image.frombytes('CMYK', (xb, yb), block)
            plt.imshow(img)
            await self.put()
            
            for start in range(2):
                aslice = block[start::2]
                channel = struct.unpack(form, aslice[:struct.calcsize(form)])
                channels.append(np.array(channel).reshape((xb, yb)))

            #print(row, col, feature['block_key'], type(feature['block_key']),
            #      feature['rasterband_id'],
            #      feature['rrd_factor'])
            section[row][col] += 1

            row -= self.row
            col -= self.col
            size = self.size

            
            for grid, channel in zip(grids, channels):

                grid[row * xb: (row + 1) * xb, col * yb: (col + 1) * yb] = channel

            
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



if __name__ == '__main__':


    ras = Raster()

    ras.set_args()

    fm = farm.Farm()
    fm.add(ras)

    # ho hum, still no magic roundabout
    fm.shep.path.append(ras)
    
    farm.run(fm)
    magic.run(run(fm))
