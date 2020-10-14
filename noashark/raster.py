

import argparse
import gdal
import curio
import struct
from collections import deque, Counter
import numpy as np
from blume import magic, farm

from matplotlib import pyplot as plt

class Raster(magic.Ball):

    def set_args(self, args=None):

        parser = argparse.ArgumentParser()
        parser.add_argument('-row', type=int, default=450)
        parser.add_argument('-col', type=int, default=350)
        parser.add_argument('-size', type=int, default=10)
        parser.add_argument('-xblock', type=int, default=128)
        parser.add_argument('-yblock', type=int, default=128)
        parser.add_argument('filenames', nargs='*')

        args = parser.parse_args(None)

        self.update(args)

        self.filenames = deque(args.filenames)

    async def run(self):

        db = gdal.ogr.Open(self.filenames[0])

        print(db.name)

        print('layers:', db.GetLayerCount())

        layer = db.GetLayer(0)

        area = np.zeros((500, 500))
        section = np.zeros((500, 500))

        gridsize = self.size +1
        grid = np.zeros((gridsize * self.xblock, gridsize * self.yblock))

        blocks = {}
        for fix in range(layer.GetFeatureCount()):

            feature = layer.GetFeature(fix + 1)
            row = feature['row_nbr']
            col = feature['col_nbr']

            area[row][col] += 1
            
            if row < self.row or row > self.row + self.size:
                continue

            if col < self.col or col > self.col + self.size:
                continue

            block = feature.GetFieldAsBinary('block_data')

            arow = struct.unpack("<16384I", block[:struct.calcsize("16384i")])

            #print(row, col, feature['block_key'], type(feature['block_key']),
            #      feature['rasterband_id'],
            #      feature['rrd_factor'])
            section[row][col] += 1

            array = np.array(arow)

            array = array.reshape((self.xblock, self.yblock))

            row -= self.row
            col -= self.col
            size = self.size
            xb = self.xblock
            yb = self.yblock
            grid[row * xb: (row + 1) * xb, col * yb: (col + 1) * yb] = array
            await curio.sleep(0.001)
            
            #counts = Counter(arow)
            #print(len(counts))
            #print(counts.most_common(20))

        plt.imshow(grid)
        plt.title(self.filenames[0])
        plt.colorbar()
        await self.put()

        #plt.imshow(area)
        #plt.colorbar()
        #await self.put()

        #plt.imshow(section)
        #plt.colorbar()
        #await self.put()
        
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

    curio.run(run(fm))
