"""Functions to work with results tables."""


def preset_results_column(results_table, column, value):
    """pre-set all rows in given column of the IJ-ResultsTable with desired value

    Parameters
    ----------
    results_table : ResultsTable
        a reference of the IJ-ResultsTable
    column : str
        the desired column. will be created if it does not yet exist
    value : str, float or int
        the value to be set
    """
    for i in range(results_table.size()):
        results_table.setValue(column, i, value)

    results_table.show("Results")


def add_results_to_resultstable(results_table, column, values):
    """add values to the ResultsTable starting from row 0 of a given column

    Parameters
    ----------
    results_table : ResultsTable
        a reference of the IJ-ResultsTable
    column : string
        the column in which to add the values
    values : array
        tarray with values to be added
    """
    for index, value in enumerate(values):
        results_table.setValue(column, index, value)

    results_table.show("Results")
