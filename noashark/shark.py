"""Thanks to for helping me find my way around gdb databases.

https://github.com/rouault/dump_gdbtable/wiki/FGDB-Spec

The first table in a database, a00000001.gdbtable, lists all the
tables in the database, including itself.

There is no table that lists all tables that do not list themselves.

For the database of NOAA flood data that I am exploring, the first 20
rows are as follows:

0            GDB_SystemCatalog           0     None
1                   GDB_DBTune           0     None
2              GDB_SpatialRefs           0     None
3                    GDB_Items           0     None
4                GDB_ItemTypes           0     None
5        GDB_ItemRelationships           0     None
6    GDB_ItemRelationshipTypes           0     None
7               GDB_ReplicaLog           2     None
8             MA_slr_depth_0ft           0     None
9    fras_ras_MA_slr_depth_0ft           0     None
10   fras_aux_MA_slr_depth_0ft           0     None
11   fras_blk_MA_slr_depth_0ft           0     None
12   fras_bnd_MA_slr_depth_0ft           0     None
13           MA_slr_depth_10ft           0     None
14  fras_ras_MA_slr_depth_10ft           0     None
15  fras_aux_MA_slr_depth_10ft           0     None
16  fras_blk_MA_slr_depth_10ft           0     None
17  fras_bnd_MA_slr_depth_10ft           0     None
18            MA_slr_depth_1ft           0     None
19   fras_ras_MA_slr_depth_1ft           0     None
...



"""


import argparse
from pathlib import Path
import struct
from collections import deque, Counter
from pprint import pprint
import time

import gdal

import numpy as n
from blume import magic, farm

from matplotlib import pyplot as plt

import geopandas

class Shark(magic.Ball):

    TABLES = dict(
        catalog=1,
        config=2,
        coords=3,
        layers=4,
    )
    
    def start(self):

        self.path = Path(self.path)

        self.depths = {}

        pprint(self.load_table(1).head(self.topn))

        tables = self.load_table(self.TABLES['catalog'])
        print(tables.index)
        table_lookup = {}
        for ix,name in enumerate(tables.Name):
            table_lookup[name] = ix + 1
            print(name)

        self.table_lookup = table_lookup
        print(len(table_lookup))
        #return

        self.config = self.load_table(self.TABLES['config']).to_dict()

        self.coords = self.load_table(self.TABLES['coords'])
        print(self.coords.iloc[0])

        layers = self.load_table(self.TABLES['layers'])
        print(layers.iloc[0])
        print('XXXXXXXXXXXXXXX')

        self.layers = {}
        lastparms = None
        for name, index in self.table_lookup.items():
            #print(name, index)
            if '_blk_' in name:
                print(name, index)

                print(f'Parms for {name} {index}')

                parms = self.table_lookup[name.replace('_blk_', '_bnd_')]
                
                parms = self.load_table(parms).iloc[0].to_dict()

                if lastparms:
                    for key, value in parms.items():
                        if lastparms[key] != value:
                            print(key, value, lastparms[key])
                    if parms != lastparms:
                        print('parms differ')
                lastparms = parms.copy()


                # probably should just have one object for each table.
                parms['index'] = index
                parms['name'] = name

                pprint(parms)

                layer = Layer(self.path, parms)
                self.layers[name] = layer

        self.layers = deque(self.layers.items())
        self.dates()
                    
    def dates(self):

        for name, layer in self.layers:
            print(time.ctime(layer.cdate), layer.mdate - layer.cdate)

    def load_table(self, n=1):
        """ Load a table """
        df = geopandas.read_file(self.path / f'a{n:08x}.gdbtable')
        return df
    

    def grid(self, lat=None, lon=None, size=None):
        """ Return a dictionary of tiles for this location """
        pass


class Layer:

    def __init__(self, path, parms):

        self.__dict__.update(parms)

        self.df = open_database(path, parms['index'])
        
                               
def open_database(path, n):

    return gdal.ogr.Open(str(Path(path) / f'a{n:08x}.gdbtable'))


def generate_features(df):
    
    layer = df.GetLayer(0)

    data = []
    for item in range(layer.GetFeatureCount()):
        feature = layer.GetFeature(item + 1)
        yield feature
        

if __name__ == '__main__':

    parser = magic.Parser()
    parser.add_argument('-topn', type=int, default=20)
    parser.add_argument('-name', default='unknown')
    parser.add_argument('-path', default='.')

    shark = Shark()

    # parse args and figure out what we need here
    args = parser.parse_args()
    args.path = Path(args.path)

    # tell the shark what is going on
    shark.update(args)

    # let it start and run
    magic.run(shark.start())
    
    magic.run(shark.run())
