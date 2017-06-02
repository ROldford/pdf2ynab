"""Converts bank transaction files to CSV file formatted for YouNeedABudget
Both PDF and CSVs can be reformatted

Version:

Note:
    CSV format is given at:
    http://classic.youneedabudget.com/support/article/csv-file-importing
    Required fields: Date,Payee,Category,Memo,Outflow,Inflow
    Best date format: MM/DD/YYYY
    Outflow/Inflow contain money values which can only have decimal separator

Args:
    bank_code (str): Code for bank that data is from
    input_file (str): Path to input file (PDF or CSV)
    output_file (str): Path to output CSV file
"""

import pandas as pd
import globals as gl
import bank_formats as bf
import magic
import re
import argparse
import tabula


def fix_duplicated_headers(the_dataframe):
    """Removes any rows that match the DataFrame header (i.e. column names)
    Needed when pulling from multi-page PDFs

    Args:
        the_dataframe (pandas.DataFrame): may have duped headers

    Returns:
        pandas.DataFrame: with duped headers removed
    """
    return_value = the_dataframe
    rows_to_remove = []
    header = return_value.columns.values.tolist()
    for row in the_dataframe.iterrows():
        index, data_series = row
        data = data_series.tolist()
        if data == header:
            rows_to_remove.append(index)
    return_value = return_value.drop(return_value.index[rows_to_remove])
    return return_value


def fix_columns(the_dataframe, columns_rename):
    """Renames/Removes/Adds columns to match YNAB format
    Uses columns_rename to do renaming

    Args:
        the_dataframe (pandas.DateFrame): DataFrame with bad columns
        columns_rename (dict): Good col name: Existing col name

    Returns:
        pandas.DateFrame: has all 6 columns from YNAB format
    """
    return_value = the_dataframe
    return_value.columns = [x.lower() for x in return_value.columns]
    return_value = the_dataframe.rename(    
        columns=columns_rename, inplace=False
    )
    return_value = return_value.reindex(
        columns=gl.COL_NAMES_LIST_ALL, fill_value=""
    )
    return return_value


def fix_money_columns(the_dataframe, separator):
    """Edits values in Outflow/Inflow columns to match correct format
    Correct format: No nondigits, except decimal separator

    Args:
        the_dataframe (pandas.DateFrame): DataFrame with money columns
        separator (gl.DECIMAL_SEPARATOR): Decimal separator (. or ,)

    Returns:
        pandas.DateFrame: has correct format in Outflow/Inflow
    """
    return_val = the_dataframe
    return_val[gl.COL_NAME_INFLOW] = return_val[gl.COL_NAME_INFLOW].apply(
        fix_money_value, args=(separator,)
    )
    return_val[gl.COL_NAME_OUTFLOW] = return_val[gl.COL_NAME_OUTFLOW].apply(
        fix_money_value, args=(separator,)
    )
    return return_val


def fix_money_value(the_string, separator):
    """Edits single value to match money format (no nondigits, decimal OK)

    Args:
        the_string (str): Value to be reformatted
        separator (gl.DECIMAL_SEPARATOR): Decimal separator (. or ,)

    Returns:
        str: Correctly formatted money value
    """
    return_value = the_string
    if separator == gl.DECIMAL_SEPARATOR.PERIOD:
        regex = r"[^\d\.]"
    elif separator == gl.DECIMAL_SEPARATOR.COMMA:
        regex = r"[^\d,]"
    return_value = re.sub(regex, '', the_string)
    return return_value


def fix_date_column(the_dataframe, regex, repl):
    """Edits values in Date column to match best date format

    Note:
        regex and repl should be found from bank_formats

    Args:
        the_dataframe (pandas.DateFrame): DataFrame with Date column
        regex (TYPE): Regex string for bank's date format
        repl (TYPE): Regex string to reformat bank's date format

    Returns:
        pandas.DateFrame: has correct format in Date column
    """
    return_value = the_dataframe
    date_list = the_dataframe[gl.COL_NAME_DATE].tolist()
    for i in range(len(date_list)):
        date_list[i] = re.sub(regex, repl, date_list[i])
    return_value[gl.COL_NAME_DATE] = date_list
    return return_value


def pdf2ynab(bank_code, input_file, output_file):
    """Main program flow

    Note:
        Only run by main()

    Args:
        bank_code (str): Code for bank that data is from
        input_file (str): Path to input file (PDF or CSV)
        output_file (str): Path to output CSV file
    """
    bank = bf.BANK_FORMATS[bank_code]
    col_format = bank[gl.BF_COL_FORMAT]
    date_regex = bank[gl.BF_DATE_REGEX]
    date_repl = bank[gl.BF_DATE_REPLACE]
    dec_separator = bank[gl.BF_DECIMAL_SEPARATOR]
    file_type = magic.from_file(input_file, mime=True)
    if "pdf" in file_type:
        base_dataframe = tabula.read_pdf(
            input_file,
            pages='all',
            guess=True,
            silent=True)
    else:
        base_dataframe = pd.read_csv(
            input_file,
            index_col=False,
            dtype=str,
            quotechar='"'
        )
    base_dataframe = base_dataframe.fillna("")
    no_extra_headers_dataframe = fix_duplicated_headers(base_dataframe)
    fixed_columns_dataframe = fix_columns(
        no_extra_headers_dataframe,
        col_format
    )
    fixed_money_values_dataframe = fix_money_columns(
        fixed_columns_dataframe,
        dec_separator
    )
    fully_fixed_dataframe = fix_date_column(
        fixed_money_values_dataframe,
        date_regex,
        date_repl
    )
    fully_fixed_dataframe.to_csv(
        output_file,
        columns=gl.COL_NAMES_LIST_ALL,
        index=False
    )


def main():
    """Only takes in args and passes to real main program flow in pdf2ynab()
    """

    parser = argparse.ArgumentParser()
    parser.add_argument(
        "bank_code",
        help="3 letter code representing the bank that the data comes from"
    )
    parser.add_argument(
        "input_file",
        help="PDF file containing bank transation data"
    )
    parser.add_argument(
        "output_file",
        help="Name of CSV file that output will be saved to"
    )
    program_args = parser.parse_args()
    bank_code = program_args.bank_code
    input_file = program_args.input_file
    output_file = program_args.output_file
    pdf2ynab(bank_code, input_file, output_file)


if __name__ == '__main__':
    main()
