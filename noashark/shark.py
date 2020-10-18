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

import gdal

import numpy as n
from blume import magic, farm

from matplotlib import pyplot as plt

import geopandas

class Shark:

    TABLES = dict(
        catalog=1,
        config=2,
        coords=3,
        layers=4,
    )
    
    def __init__(self, path='.'):

        self.path = Path(path)


        pprint(read_database(self.path, 1))

        tables = self.load_table(1)
        for name in tables.Name:
            print(name)
        return

        
        for database in sorted(self.path.glob('*.gdbtable')):
            print(database)
            df = geopandas.read_file(database)

            print(df.head(20))

    def load_table(self, n=1):
        """ Load a table """
        df = geopandas.read_file(self.path / f'a{n:08x}.gdbtable')
        return df
                               
def open_database(path, n):

    return gdal.ogr.Open(str(Path(path) / f'a{n:08x}.gdbtable'))


def read_features(df):
    
    layer = df.GetLayer(0)

    data = []
    for item in range(layer.GetFeatureCount()):
        feature = layer.GetFeature(item + 1)
        data.append(feature.items())
        
    return data

if __name__ == '__main__':

    Shark()
