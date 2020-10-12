

import argparse
import gdal
import curio
import binascii
from collections import deque, Counter
import numpy as np
from blume import magic, farm

from matplotlib import pyplot as plt

class Raster(magic.Ball):

    def set_args(self, args=None):

        parser = argparse.ArgumentParser()
        parser.add_argument('filename')

        args = parser.parse_args(None)

        self.update(args)

    async def run(self):
        
        db = gdal.ogr.Open(self.filename)

        print(db.name)

        print('layers:', db.GetLayerCount())

        layer = db.GetLayer(0)

        print(layer.GetExtent())
        print(layer.GetFeatureCount())

        feature = layer.GetFeature(1)
        print(layer.GetFeaturesRead())

        rcounts = Counter()
        ccounts = Counter()

        rows = []
        area = np.zeros((500, 500))
        
        for ix in range(layer.GetFeatureCount()):
            f = layer.GetFeature(ix+1)
            block = f.GetFieldAsBinary('block_data')
            row = f.GetFieldAsInteger(2)
            col = f.GetFieldAsInteger(3)

            area[row][col] += 1
            #if True:
            if col == 203:
                #print(row)
                #print(f'block of length {len(block)}')

                #print(binascii.unhexlify(block[:-3]))
                arow = [int(x) for x in block]
                print(arow[:10])
                rows.append(arow[:1000])

            rcounts.update([row])
            ccounts.update([col])

        rowlen = len(rows[0])
        rowlens = Counter(len(r) for r in rows)
        print(rowlens)

        plt.imshow(area)
        await self.put()
        
        print('number of rows', len(rows), len(rows[0]))
        xx = np.array(rows)
        print(xx.shape)
        plt.imshow(rows)
        await self.put()
                        
        print(len(rcounts))
        print(len(ccounts))
        print(np.mean([x for x in rcounts.values()]))
        print(np.mean([x for x in ccounts.values()]))
        print(rcounts.most_common(10))
        print(ccounts.most_common(10))

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
