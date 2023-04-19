"""Functions to work with results tables."""

from ij.measure import ResultsTable


def preset_results_column(results_table, column, value):
    """Pre-set all rows in given column of the ResultsTable with desired values.

    Parameters
    ----------
    results_table : ij.measure.ResultsTable
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
    """Add values to the ResultsTable starting from row 0 of a given column.

    Parameters
    ----------
    results_table : ij.measure.ResultsTable
        a reference of the IJ-ResultsTable
    column : string
        the column in which to add the values
    values : list(int, double or float)
        array with values to be added
    """
    for index, value in enumerate(values):
        results_table.setValue(column, index, value)

    results_table.show("Results")


def get_resultstable():
    """Instantiate or get the ResultsTable instance.

    Use to either get the current instance of the IJ ResultsTable or instantiate
    it if it does not yet exist.

    Returns
    -------
    ij.measure.ResultsTable
        A reference of the IJ-ResultsTable
    """
    rt = ResultsTable.getInstance()
    if not rt:
        rt = ResultsTable()
    return rt
