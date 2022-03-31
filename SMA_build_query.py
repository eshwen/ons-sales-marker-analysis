# -*- coding: utf-8 -*-
"""Perform the first step of the sales marker analysis for a given class of items for a given month of interest.

The month of interest is compared to the same month from the previous year to compare expenditure. It is also compared
to the previous month in the same year to track any sales marker changes.

This script builds the SQL query to retrieve the data for VESPA, accounting for items that should be ignored, and
additional items not captured by the category's typical bounds.

"""

__author__ = "eshwen.bhal@ext.ons.gov.uk"

import datetime
from argparse import ArgumentDefaultsHelpFormatter, ArgumentParser
from dateutil.relativedelta import relativedelta
from pathlib import Path


class ItemCategoryContainer(object):
    """Store data pertaining to item category of interest. Build SQL query to retrieve data from VESPA.
    
    Args:
        name (str): Name of category.
        month (str): Month of interest in YYYYMM format.
        items_to_ignore (list of int, optional): Item numbers to ignore. Default intelligently builds list.
    
    """
    
    def __init__(self, name, month, items_to_ignore=[]):
        """Initialise the class.

        Attributes:
            name (str): Name of category.
            month (str): Month of interest in YYYYMM format.
            items_to_ignore (list of int): Item numbers to ignore.

        """
        supported_cats = ["alcohol", "clothing", "furniture"]
        if name not in supported_cats:
            raise ValueError(f"The category {name} is not supported at this time.")
        self.name = name
        self.month = month

        self.items_to_ignore = items_to_ignore
        if not self.items_to_ignore:
            self.items_to_ignore = self.extract_items_to_ignore()

    def extract_items_to_ignore(self):
        """Retrieve ignored items from default lists.
        
        Returns:
            list of int: Item numbers to be ignored.

        """
        ignored = {
            "alcohol": [310301, 310302, 310306, 310307, 310309, 310310, 310315, 310316],
            "clothing": [],
            "furniture": []
        }
        return ignored[self.name]

    @property
    def item_bounds(self):
        """Item ID bounds for the category of interest.
        
        Returns:
            tuple containing:
                lower (int): Lower bound of category.
                upper (int): Upper bound of category.

        """
        bounds = {
            "alcohol": (310200, 310605),
            "clothing": (510100, 510599),
            "furniture": (430100, 430199)
        }
        lower, upper = bounds[self.name]
        return lower, upper

    @property
    def extra_item_ids(self):
        """Capture additional item IDs for the category missed by item_bounds().
        
        Returns:
            list of int: Item IDs.
  
        """
        extras = {
            "alcohol": [],
            "clothing": [
                440104,  # Dry cleaning man's suit
                440132,  # Added 2014 for men's clothing hire
            ],
            "furniture": [520132]
        }
        return extras[self.name]

    @property
    def sql_query(self):
        """Build the SQL query to extract data from VESPA.
        
        Returns:
            str: The query.
        
        """
        query = f"""select * from quote
where quote_date = {self.month}
and item_id > {self.item_bounds[0]}
and item_id < {self.item_bounds[1]}"""

        if self.extra_item_ids:
            for item in self.extra_item_ids:
                query += f"""
or quote_date = {self.month}
and item_id = {item}"""

        if self.items_to_ignore:
            _as_str = [str(i) for i in self.items_to_ignore]
            query += f"\nand item_id not in ({', '.join(_as_str)})"

        query += "\n;commit;"
        return query


def string_to_datetime(date_string, fmt="%Y%m"):
    """Convert a string to a datetime.datetime object.
    
    Args:
        date_string (str): String to convert.
        fmt (str, optional): Format of the string.
    
    Returns:
        datetime.datetime: Datetime object.

    """
    return datetime.datetime.strptime(date_string, fmt)


def datetime_to_string(date, fmt="%Y%m"):
    """Convert a datetime.datetime object to a string.
    
    Args:
        date (datetime.datetime): Instance of object to convert.
        fmt (str, optional): Format of the output string.
    
    Returns:
        str: Output string.

    """
    return date.strftime(fmt)


def parse_args():
    """Parse CLI arguments.
    
    Returns:
        argparse.Namespace: Parsed arguments accessible as object attributes.
    
    """
    parser = ArgumentParser(description=__doc__, formatter_class=ArgumentDefaultsHelpFormatter)
    parser.add_argument("item_category", choices=["alcohol", "clothing", "furniture"], help="Category to perform analysis for.")
    parser.add_argument("-m", "--month_of_interest", type=str, default=datetime.datetime.today().strftime("%Y%m"), help="Month of interest in fomat YYYYMM")
    parser.add_argument("-i", "--items_to_ignore", type=int, nargs="*", default=[], help="Item number(s) to ignore in analysis. Default intelligently ignores.")

    args = parser.parse_args()
    return args


if __name__ == "__main__":
    args = parse_args()

    container_this_month = ItemCategoryContainer(
        args.item_category,
        args.month_of_interest,
        items_to_ignore=args.items_to_ignore
    )
    print(f"Run this SQL query to retrieve the data for this month:\n{container_this_month.sql_query}\n")

    # Use SQL again to get the data from the previous month, instead of relying on existing data from spreadsheet
    last_month = string_to_datetime(args.month_of_interest) - relativedelta(months=1)
    last_month_str = datetime_to_string(last_month)
    container_last_month = ItemCategoryContainer(
        args.item_category,
        last_month_str,
        items_to_ignore=args.items_to_ignore
    )
    print(f"Run this SQL query to retrieve the data for last month:\n{container_last_month.sql_query}\n")

    # Use SQL again to get the data from the previous year, instead of relying on existing data from spreadsheet
    last_year = string_to_datetime(args.month_of_interest) - relativedelta(years=1)
    last_year_str = datetime_to_string(last_year)
    container_last_year = ItemCategoryContainer(
        args.item_category,
        last_year_str,
        items_to_ignore=args.items_to_ignore
    )
    print(f"Run this SQL query to retrieve the data for this month last year:\n{container_last_year.sql_query}\n")

    # Example: https://officenationalstatistics.sharepoint.com/:x:/r/sites/MSDCPI/_layouts/15/Doc.aspx?sourcedoc=%7BD5147CD2-09D1-49FB-9E9C-02DC116FE1D5%7D&file=202112_Item_Clothing_Quote_Analysis_APY.xlsx&action=default&mobileredirect=true
    # Use data_this_month, data_last_month, and data_last_year to create the temporary variables in cols A, W, and Z-AG of sheet '2021' and make the pivot tables based on those
    # I can also create the summary tables in sheet '2021 Summary' based on that same data
    # This is basically doing steps 5-10
