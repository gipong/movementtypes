Movementtypes
=============
extract GPS traces from file and analyze them to reveal movement types

Install
-------
movementtypes is available on pypi, https://pypi.python.org/pypi/movementtypes/0.1.1

.. code-block:: bash

    $ pip install movementtypes

Documentation
-------------
http://movementtypes.readthedocs.io/en/latest/

Usage
-----

CSV file format requirements

* The file must be include column headings.
* Character encodings such as BIG-5 have been converted to UTF-8.

Required columns in the CSV file

id, lat, lng, alt, time

Columns in the CSV file

* id: specific id number for identity field
* lat,lng: if the position information is DMS format(Degrees, minutes and seconds), you need to convert to decimal degrees
* time: this value can be YYYY-MM-DD hh:mm:ss or ISO 8601 date and time format

.. code-block:: python

    import movementtypes as mvt

    df = mvt.mvtypes("data/gps-trajectory.csv")
    # using the KDE module to choose an optimal bandwidth
    df.optbwKDE()

    # check the result
    print(df.result)

    # using calVelocity
    print(df.calVelocity(df.data.iloc[17], df.data.iloc[18][:-1], df.data.iloc[19]))

    # classify speed based on the result
    df.classifySpeed()
    df.export_csv("output.csv")

Public GPS traces on OSM https://www.openstreetmap.org/traces

(gpx2csv can convert the GPX file to valid CSV files)

.. code-block:: python

    # path can be your file path or public gpx link
    mvt.convert.gpx2csv("https://www.openstreetmap.org/trace/2550408/data", 'osmdata')

    df = mvt.mvtypes('osmdata.csv')

    df.optbwKDE()
    print(df.result)

Command line usage
------------------
.. code-block:: bash

    $ mvtypes --help
    Usage: mvtypes [OPTIONS] PATH OUTPUT

      path: file path

      output: output file

    Options:
      --threshold INTEGER  the default threshold setting is 15 minutes by
                           clustering the dataset before calculating velocity
      --inepsg INTEGER     input projection, default is 4326
      --outepsg INTEGER    coverting coordinates from inEPSG to outEPSG for
                           calculating the point of velocity, default is 3857
      --help               Show this message and exit.