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

3) Feed this into <WORK IN PROGRESS>
