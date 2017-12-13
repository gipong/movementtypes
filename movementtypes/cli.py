# -*- coding: utf-8 -*-
import click
import movementtypes as mvtypes


@click.command(name='mvtypes')
@click.argument('path', type=click.Path(exists=True))
@click.argument('output')
@click.option('--threshold', default=15,
              help='the default threshold setting is 15 minutes by clustering the dataset before calculating velocity')
@click.option('--inepsg', default=4326,
              help='input projection, default is 4326')
@click.option('--outepsg', default=3857,
              help='coverting coordinates from inEPSG to outEPSG for calculating the point of velocity, default is 3857')
def main(path, output, threshold=15, inepsg=4326, outepsg=3857):
    """
        path: file path

        output: output file
    """
    df = mvtypes.mvtypes(path, threshold, inEPSG=inepsg, outEPSG=outepsg)
    df.optbwKDE()
    df.classifySpeed()
    df.export_csv(output)

if __name__ == "__main__":
    main()