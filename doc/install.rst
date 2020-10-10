=========
 Install
=========

Pre-requisites
==============

You will likely need 

You will also need `blume`, probably best to install that from source
code.  It is a pure python project and still evolving::

  git clone https://github.com/swfiua/blume

  cd blume

  python3 -m pip install -e .

Installing *blume* should get you a copy of matplotlib too.

Noashark
========

Now to install *noashark*, it is the same process as for blume::

  git clone https://github.com/swfiua/noashark

  cd noashark

  python3 -m pip install -e .



The pip install command installs the current folder (hopefully a
python project), in **editable** mode.

That means you just need to do a *git pull* to get the latest code.



