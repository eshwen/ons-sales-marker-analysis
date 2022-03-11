# -*- coding: utf-8 -*-
"""Parse a "flat" file created by running the queries from SMA_build_query.

Load up the file, strip all the unnecessary text, and convert the reST
formatted table into a dataframe.

Todo:
    Either run over one file at a time and save to a CSV for the next step
    (processing), or just take in all 3 files and do processing here.

"""

__author__ = "eshwen.bhal@ext.ons.gov.uk"

from argparse import ArgumentDefaultsHelpFormatter, ArgumentParser
from pathlib import Path


def strip_text():
    """Strip out the header and footer text from the file."""
    pass


def convert_str_to_df():
    """Convert the reST table into a pandas.DataFrame."""
    pass


def parse_args():
    """Parse CLI arguments.
    
    Returns:
        argparse.Namespace: Parsed arguments accessible as object attributes.
    
    """
    parser = ArgumentParser(description=__doc__, formatter_class=ArgumentDefaultsHelpFormatter)
    parser.add_argument("in_file", type=str, help="Input file.")

    args = parser.parse_args()
    return args


if __name__ == "__main__":
    args = parse_args()
    