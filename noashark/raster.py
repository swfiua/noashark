

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
        parser.add_argument('-mask', type=int, default=255)
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
        grid = np.zeros((gridsize * self.xblock, gridsize * self.yblock), dtype=np.uint32)

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
            print(array[0], arow[0])

            array = array.reshape((self.xblock, self.yblock))

            row -= self.row
            col -= self.col
            size = self.size
            xb = self.xblock
            yb = self.yblock
            grid[row * xb: (row + 1) * xb, col * yb: (col + 1) * yb] = array
            await curio.sleep(self.sleep * 0.001)
            
            #counts = Counter(arow)
            #print(len(counts))
            #print(counts.most_common(20))
            
            #if len(block) > 128 * 128 * 4:
            if False:
                
                if row == 8 and col == 10:
                    for y in range(5):
                        for x in range(2):
                            bb = bin(array[y + (size//2)][x])
                            pad = 34 - len(bb)
                            print(('0' * pad) + bb[2:], end=' ')
                        print()
                else:
                    pass
                
                bitmap = np.zeros((128, 4096))

                for ir, rrr in enumerate(array):
                    ic = 0
                    for ccc in rrr:
                        for x in range(31, 0, -1):
                            bitmap[ir][ic] = (ccc >> x) & 1
                            ic += 1
                print(bitmap[0])
                print(array.shape)
                
                #xx = struct.unpack("<512i", block[128*128*4:])
                plt.imshow(bitmap)
                plt.colorbar()
                plt.title(f'{len(block)} {row} {col}')
                await self.put()
                
                #plt.title(f'{len(block)} {row} {col}')
                #plt.imshow(np.array(xx).reshape((16,32)))
                #plt.colorbar()
                #await self.put()

        plt.imshow(grid)
        print(arow[:20])
        print(grid[0])
        print(grid[64])
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
