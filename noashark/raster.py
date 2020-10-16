

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
        parser.add_argument('-mask', type=int, default=0xff00)
        parser.add_argument('-shift', type=int, default=0)
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
        grids = [
            np.zeros((gridsize * self.xblock, gridsize * self.yblock), dtype=np.uint32),
            np.zeros((gridsize * self.xblock, gridsize * self.yblock), dtype=np.uint32),
            np.zeros((gridsize * self.xblock, gridsize * self.yblock), dtype=np.uint32),
            np.zeros((gridsize * self.xblock, gridsize * self.yblock), dtype=np.uint32)]
                

        blocks = {}
        for fix in range(layer.GetFeatureCount()):

            # fixme: need a mapping from {row, col} to feature index. this should speed things up
            # a fair bit.
            feature = layer.GetFeature(fix + 1)
            row = feature['row_nbr']
            col = feature['col_nbr']

            area[row][col] += 1

            # see above -- things would be quicker with the index
            if row < self.row or row > self.row + self.size:
                continue

            if col < self.col or col > self.col + self.size:
                continue

            block = feature.GetFieldAsBinary('block_data')

            arow = struct.unpack("<16384i", block[:struct.calcsize("16384i")])

            #print(row, col, feature['block_key'], type(feature['block_key']),
            #      feature['rasterband_id'],
            #      feature['rrd_factor'])
            section[row][col] += 1


            row -= self.row
            col -= self.col
            size = self.size
            xb = self.xblock
            yb = self.yblock
            
            arrays = []
            shifts = (0, 8, 16, 24)
            masks = (0xff, 0xff, 0xffff)
            for ix, shift in enumerate(shifts):
                array = np.array([(x & (255 << shift)) >> shift for x in arow])


                if shift == 0:
                    array = np.where(array == 255, 0, array)
                    array = np.where(array < 55, 55, array)
                array = array.reshape((self.xblock, self.yblock))

                arrays.append(array)



                grids[ix][row * xb: (row + 1) * xb, col * yb: (col + 1) * yb] = array
                await curio.sleep(self.sleep * 0.001)
            
            #counts = Counter(arow)
            #print(len(counts))

        for shift, grid in zip(shifts, grids):
            plt.imshow(grid)

            plt.title(self.filenames[0] + f'shift:{shift}')
            plt.colorbar()
            await self.put()

        plt.imshow(area)
        plt.colorbar()
        await self.put()

        plt.imshow(section)
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

    curio.run(run(fm))
