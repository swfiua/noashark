

import argparse
import gdal
import curio
from collections import deque, Counter
import numpy as np
from blume import magic, farm


class Raster(magic.Ball):

    def set_args(self, args=None):

        parser = argparse.ArgumentParser()
        parser.add_argument('filename')

        args = parser.parse_args(None)

        self.update(args)

    async def start(self):
        
        db = gdal.ogr.Open(self.filename)

        print('layers:', db.GetLayerCount())

        layer = db.GetLayer(0)

        print(layer.GetExtent())
        print(layer.GetFeatureCount())

        feature = layer.GetFeature(1)
        print(layer.GetFeaturesRead())

        rcounts = Counter()
        ccounts = Counter()

        for ix in range(layer.GetFeatureCount()):
            f = layer.GetFeature(ix+1)
            rcounts.update([f.GetFieldAsInteger(2)])
            ccounts.update([f.GetFieldAsInteger(3)])

        print(len(rcounts))
        print(len(ccounts))
        print(np.mean(rcounts.values()))
        print(np.mean(ccounts.values()))
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
