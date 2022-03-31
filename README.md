# ons-sales-marker-analysis

Refactoring of the Prices Division's Sales Marker Analysis in Python

The aim of this project is to refactor the manual steps for performing the sales marker analysis --- requiring Excel, templating, and copying of data interactively --- into a streamlined Python workflow.

## Usage

0) Install the dependencies:

   ```sh
   pip install -r requirements.txt
   ```

1) Build the SQL query to retrieve, from VESPA, the data for the item category of interest over the month of interest:

   ```sh
   python SMA_build_query.py <item category>
   ```
   
   This will print out the queries as strings that you can paste into VESPA.

2) Save the data that is returned by the queries, keeping note of the paths, and which files correspond to which time periods.

3) Feed each file one-by-one into [SMA_parse_queried_files.py](./SMA_parse_queried_files.py) to parse the data and ...

   ```sh
   python SMA_parse_queried_files.py <input file>
   ```

## Methodology

### Building the query

The first script [SMA_build_query.py](./SMA_build_query.py) is intended to be as simple as possible to use. You essentially just need to pass in the item category of interest, and perhaps some other optional arguments related to the month of interest or any additional items in the category that can be ignored. Then, it builds SQL queries to select the relevant data for the month of interest, the previous month, and the same month in the previous year.

It should be fairly easy to extend the script. To add more item numbers to the list of ignored ones, you just need to update the dictionary in `ItemCategoryContainer.extract_items_to_ignore`. If there are additional items required that aren't captured by the typical item category range (specified in `ItemCategoryContainer.item_bounds`, add them in `ItemCategoryContainer.extra_item_ids`. To add an extra item category (currently, only alcohol, clothing, and furniture are supported), a few things in the `ItemCategoryContainer` class need updating. You can just follow the same approach as the other categories. Then you just need to update the `item_category` argument choices to include the name of your new item cateogry.

Since we are unable to query the database directly, this is the simplest approach I can think of. A manual step is required to connect to the database, paste the queries, and save the output "flat" files in preparation for the next step.

### Parsing the queried data

As of writing, I've only got a skeleton for this. The intention is to pass a flat file from the previous step to the script and it will strip the header and footer text (basically a copy of the query and some metadata), then convert the actual table (which looks like it's in reST) into a pandas dataframe. There might be a library/package to do this automatically. Otherwise it shouldn't be too difficult to brute force it. You just need to identify the row corresponding to the column headers, then read the table row-by-row and append it to a dataframe, delimiting by `|`.

Each flat file needs to be fed in to the script and converted appropriately. Then, it may make sense to save each dataframe in a CSV file so copies are kept. Or, the dataframes could be passed straight into the next step.

### Processing the parsed data

This bit is quite tricky, since in the Excel spreadsheets I'm basing this off, there's a lot of processing done with some large formulae. With some understanding of Excel, hopefully these could be translated into a series of simple pandas operations to achieve the desired result. Though, another issue is that not all item categories undergo the same processing. If I remember correctly, clothing requires some extra steps. So it could be difficult to write something general and scalable.

### Extensions

- Plotting
  - I've noticed some of the Excel spreadsheets contain embedded plots. These should be fairly easy to reproduce using a package like `matplotlib` and just directly plotting columns from the processed dataframe(s) in the previous step. They can then be saved as separate pngs/pdfs
- Supporting more item categories
  - One of the requests from Anna at the BoE was to possibly expand the scope of the sales marker analysis, i.e., to include more item categories. In the interactive workflow, this sounds like quite a cumbersome task, and was one of the reasons behind the refactor in Python
  - As outlined above, it should be fairly easy to add a new item category in [SMA_build_query.py](./SMA_build_query.py) for querying the relevant data
  - The second step of parsing the flat file from the query shouldn't need modification as the structures of the flat files should be consistent
  - However, depending on the objective, in the third step some bespoke processing may be required for an additional item category (like for clothing, which doesn't apply to alcohol or furniture). But if you write the code in a smart, modular way, it may work to have a core processing block that operates the same on every item category. Then, bespoke modules/functions can hook in after that to perform the item category-specific operations
