==========================
 NOAA sea level rise data
==========================

Tools to help explore NOAA sea level rise data.

https://coast.noaa.gov/slrdata/

Work in progress.

Most of the modules can be run as scripts and use `argparse` to parse
command line arguments,  try the following::

  python -m noashark.shark -h

  python -m noashark.raster -h

And go from there.


Some of the code is really slow for now, basically an index is needed
to allow us to randomly access the appropriate parts of these big
files.

Some of the utilities pop up a window, type *h* to get a list of
options printed to the console.

*R* currently starts things running.   Again, may be slow (see above).

Where from here?
================

This is actually a specific case of a more general problem: how to
distribute and work with grids of data?

The files here for a single *area* can take tens of giga-bytes, and
there are a lot of areas.

The astro world solves this problem by providing scriptable
interfaces, together with python code that that allow you
to query subsets of the larger database.

For climate and geographical data things generally become complicated.

The `blume` project has some evolving ideas on ways to distribute such
datasets.

It revolves around distributing *meta data*, rather than the data
itself.  Together with a way to retrieve a set of data matching given
meta data.

Back to noahshark
=================

I think the plan from here is to write out some meta data about the
actual data, and use that data to be help more generic software
quickly browse the data.

Meta data includes corners of each tile.

Everything is on a grid and all the relevant meta data is, of course,
available in the FileGDB.

There are typically multiple tiles available for each grid location.

