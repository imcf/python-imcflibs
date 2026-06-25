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


def add_results_to_resultstable(results_table, column, values, rows=None):
    """Add values to the ResultsTable in a specified column.

    This function works in two ways, depending on the value of `rows`:

    1. If rows is `None`, it adds values sequentially starting from row 0.
    2. If rows is a list of int, it adds values to the given row indices.

    Parameters
    ----------
    results_table : ij.measure.ResultsTable
        A reference to the IJ-ResultsTable
    column : str
        The column in which to add the values.
    values : list of int, float or str
        Values to be added.
    rows : list of int, optional
        Specific row indices where values should be added. If None, values are
        added sequentially starting from row 0.

    Examples
    --------
    To add the same value (42) to a given `ResultsTable` to rows 1, 3 and 5:
    >>> add_results_to_resultstable(rt, "Intensity", 42, rows=[1, 3, 5])
    """
    if not isinstance(values, list) and rows is not None:
        values = [values] * len(rows)

    # Case 1: Add values sequentially from row 0
    if rows is None:
        for index, value in enumerate(values):
            results_table.setValue(column, index, value)

    # Case 2: Add values to specific rows
    else:
        if len(values) != len(rows):
            raise ValueError(f"Length mismatch: values ({len(values)}) and rows ({len(rows)})")

        for i, row_index in enumerate(rows):
            results_table.setValue(column, row_index, values[i])

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
