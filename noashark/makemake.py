"""Make it all work

The idea here is to create some sort of meta data from the NOAA
data.

For now we have grids of values for different variables.

The grids form a mesh of latitude and longitudes.

Indeed, the data itself, conveniently provides coordinates for each layer.

The width and heigh, in degrees, and the minimum and maximum latitudes
and longitudes covered.

And tiles the whole area in tiles of a given width and height.

Since we are only interest in a small band around the coast, the bnd
part of the is a list of lat/lons covered by the table.

Or rather, the row and column of the regular grid covering the specified area.

"""

import random
import numpy as np
import hashlib

from blume import magic, farm

from matplotlib import pyplot as plt

from . import shark

from statistics import mean
import struct
from collections import Counter, deque
import inspect
import csv

class Jaws(shark.Shark):

    async def start(self):

        result = super().start()
        if inspect.iscoroutine(result):
            await result
        
        
        rows, cols, ixs, means = [], [], [], []
        counts = Counter(), Counter(), Counter(), Counter()

        
        for key, value in self.layers:
            print('opening for', key)
            meta = open(key + '.csv', 'w')
            writer = csv.writer(meta)
            writer.writerow('row,col,index,md5'.split(','))
            
            for ix, feature in enumerate(shark.generate_features(value.df)):
                ixs.append(ix)
                rows.append(feature['row_nbr'])
                cols.append(feature['col_nbr'])

                block = feature.GetFieldAsBinary('block_data')
                hx = hashlib.md5()
                hx.update(block)
                writer.writerow([rows[-1], cols[-1], ixs[-1], hx.hexdigest()])
            meta.close()

    async def run(self):

        key, value = self.layers[0]

        print(value.__dict__.keys())
        print(key)
        rows, cols, ixs, means = [], [], [], []
        counts = Counter(), Counter(), Counter(), Counter()
        for ix, feature in enumerate(shark.generate_features(value.df)):
            ixs.append(ix)
            rows.append(feature['row_nbr'])
            cols.append(feature['col_nbr'])

            block = feature.GetFieldAsBinary('block_data')

            form = 'B'
            nchan = 4
            #chunk = 2

            channels = []
            for start in range(nchan):
                data = struct.iter_unpack(form, block[start::nchan])
                channels.append(list(x[0] for x in data))
                #channels.append(struct.unpack(
                #    f'{size}' + form, block[start::nchan]))
                #counts[start].update(channels[-1])
                width, height = value.block_height, value.block_width
                img = np.array(channels[-1][:width*height])
                print(img.shape, value.block_height, value.block_width)
                img.resize((value.block_height, value.block_width))
                print(type(img), img.shape)
                plt.imshow(img)
                await self.put()

            means.append(mean(channels[0]))

            nchan = len(channels)
            

            print(means, len(means))
            await magic.sleep(0.01)
            for start in range(nchan):
                data = counts[start].most_common(6)
                print(start)
                print(data)
                #plt.plot([x[0] for x in data],
                #               [x[1] for x in data])
                #await self.put()
            for aix in range(nchan-1):
                if nchan == 1:
                    plt.plot(channels[aix])
                for bix in range(aix+1, nchan):
                    achannel = channels[aix]
                    bchannel = channels[bix]
                    plt.title(f'{aix} {bix}')
                    plt.scatter(achannel, bchannel)
                    await self.put()
            if ix > 1000:
                break

        plt.scatter(rows, cols, c=means)
        await self.put()
        #plt.scatter(rows, cols, c=ixs)
        self.layers.rotate()
                
            
if __name__ == '__main__':

    parser = magic.Parser()
    
    parser.add_argument('-meta', default='./meta')
    parser.add_argument('-topn', type=int, default=20)
    parser.add_argument('-name', default='MA')
    parser.add_argument('-path', default='.')
    parser.add_argument('-radius', default=10)
    parser.add_argument('-roff', default=None)
    parser.add_argument('-coff', default=None)

    jaws = Jaws()

    args = parser.parse_args()
    args.path = magic.Path(args.path)
    
    jaws.update(args)

    # for now dump out:
    # area

    fm = farm.Farm()
    fm.add(jaws)
    fm.shep.path.append(jaws)
    farm.run(fm)

    #jaws.start()

    #jaws.run()

    
