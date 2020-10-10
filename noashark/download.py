
import argparse
import csv

def slr_urls(region, subregion):

    return dict(
        slrurl=f"//coast.noaa.gov/htdata/Inundation/SLR/SLRdata/{region}/{subregion}_slr_data_dist.zip",
        confurl=f"//coast.noaa.gov/htdata/Inundation/SLR/ConfData/Distribution/{region}/{subregion}_conf_data.zip",
        demurl=f"//coast.noaa.gov/htdata/Inundation/SLR/SLRdata/{region}/{subregion}_dem.zip",
        slrdepthurl=f"//coast.noaa.gov/htdata/Inundation/SLR/SLRdata/{region}/{subregion}_slr_raster_data_dist.zip")

# one size fits all for flood frequency data
ffurl="//coast.noaa.gov/htdata/Inundation/SLR/FloodFreqData/Flood_Frequency_data_dist.zip"



if __name__ == '__main__':


    parser = argparse.ArgumentParser()

    parser.add_argument('-areas', default='areas.csv')

    args = parser.parse_args()
    
    areas = open(args.areas)
    for row in csv.DictReader(open(args.areas).read(),
                              fields=['region', 'subregion']):
        print(row)
        print(slr_urls(row[0], row[1]))
