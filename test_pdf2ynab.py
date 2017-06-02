"""Unit test suite for PDF2YNAB
"""

import unittest
import numpy as np
import pandas as pd
import pdf2ynab as p2y
import globals as gl
import bank_formats as bf


class TestFixDuplicatedHeaders(unittest.TestCase):

    def test_removes_duplicated_header(self):
        test_input = np.array([[
            "DATE",
            "TIME",
            "TRANSACTION",
            "CHANNEL",
            "DESCRIPTION",
            "CHQ NO.",
            "WITHDRAWAL",
            "DEPOSIT",
            "BALANCE"
        ], [
            "24/03/2017",
            "19:19",
            "X2",
            "POS",
            "BLAH",
            "",
            "-796.00",
            "",
            "+233,070.25"
        ], [
            "24/03/2017",
            "20:29",
            "X2",
            "ENET",
            "BLEH",
            "",
            "-100.00",
            "",
            "+232,970.25"
        ], [
            "DATE",
            "TIME",
            "TRANSACTION",
            "CHANNEL",
            "DESCRIPTION",
            "CHQ NO.",
            "WITHDRAWAL",
            "DEPOSIT",
            "BALANCE"
        ], [
            "24/03/2017",
            "20:31",
            "X2",
            "ENET",
            "FOO",
            "",
            "-35,000.00",
            "",
            "+197,970.25"
        ], [
            "26/03/2017",
            "20:04",
            "X2",
            "POS",
            "BAR",
            "",
            "-825.00",
            "",
            "+197,145.25"
        ]])
        test_dataframe = pd.DataFrame(
            data=test_input[1:, 0:],
            index=range(test_input.shape[0] - 1),
            columns=test_input[0, 0:]
        )
        result_dataframe = p2y.fix_duplicated_headers(test_dataframe)
        header = result_dataframe.columns.values.tolist()
        for row in result_dataframe.iterrows():
            data_series = row[1]
            data = data_series.tolist()
            self.assertNotEqual(data, header)


class TestFixColumnsMethod(unittest.TestCase):
    """Tests for fix_columns()
    Method should rename and edit columns to match YNAB format
    """

    def setUp(self):
        test_input_1 = np.array([[
            "DATE",
            "TIME",
            "TRANSACTION",
            "CHANNEL",
            "DESCRIPTION",
            "CHQ NO.",
            "WITHDRAWAL",
            "DEPOSIT",
            "BALANCE"
        ], [
            "01/02/2017",
            "10:11",
            "X2",
            "ENET",
            "FOO",
            "",
            "-500.00",
            "",
            "+483,346.08"
        ], [
            "28/02/2017",
            "16:17",
            "X1",
            "BCMS",
            "NERTZ",
            "",
            "",
            "+142,442.50",
            "+514,138.80"
        ]
        ])
        test_dataframe_1 = pd.DataFrame(
            data=test_input_1[1:, 0:],
            index=range(test_input_1.shape[0] - 1),
            columns=test_input_1[0, 0:]
        )
        bank = bf.BANK_FORMATS["SCB"]
        self.column_options = bank[gl.BF_COL_FORMAT]
        self.result_dataframe_1 = p2y.fix_columns(
            test_dataframe_1, self.column_options
        )

    def test_renamed_using_column_options(self):
        """Tests that method properly uses column_options
        """
        for column in self.column_options.keys():
            self.assertIn(
                column,
                self.result_dataframe_1.columns.values.tolist()
            )

    def test_date_column_has_date_string(self):
        """Tests that renamed "Date" column has date-type data
        Checks that string splits into 2 char, 2 char and 2/4 char strings
        """
        col_list_date = self.result_dataframe_1[gl.COL_NAME_DATE].tolist()
        for the_date in col_list_date:
            self.assertIsInstance(the_date, str)
            the_date_list = the_date.split("/")
            the_date_string_month = the_date_list[0]
            the_date_string_day = the_date_list[1]
            the_date_string_year = the_date_list[2]
            the_date_string_length_year = len(the_date_string_year)
            self.assertEqual(len(the_date_string_month), 2)
            self.assertEqual(len(the_date_string_day), 2)
            self.assertTrue(
                the_date_string_length_year == 4 or
                the_date_string_length_year == 2
            )

    def test_payee_column_is_full_of_strings(self):
        """Tests that renamed "Payee" column has a string in every entry
        """
        col_list_payee = self.result_dataframe_1[gl.COL_NAME_PAYEE].tolist()
        for the_payee in col_list_payee:
            self.assertIsInstance(the_payee, str)

    def test_money_columns_have_money_strings(self):
        """Tests that renamed "Outflow"/"Inflow" strings contain $ values
        String should contain digits
        Can have leading non-numeric characters
        Can have thousands separators
        Must have decimal separator and 2 decimal digits
        """
        regex = r"^(\+|-)\d+(,\d{3})*.\d{2}$"
        col_list_oflow = self.result_dataframe_1[gl.COL_NAME_OUTFLOW].tolist()
        col_list_iflow = self.result_dataframe_1[gl.COL_NAME_INFLOW].tolist()
        for outflow in col_list_oflow:
            if not len(outflow) == 0:
                self.assertRegex(outflow, regex)
        for inflow in col_list_iflow:
            if not len(inflow) == 0:
                self.assertRegex(inflow, regex)

    def test_correct_columns_in_correct_order(self):
        """Tests that fixed DataFrame has all correct columns
        """
        actual_columns = self.result_dataframe_1.columns.values.tolist()
        expected_columns = gl.COL_NAMES_LIST_ALL
        self.assertEqual(actual_columns, expected_columns)

    def test_expected_empty_columns_are_empty(self):
        """Tests that columns not in column_options only have empty strings
        """
        expected_empty_columns = []
        given_columns = self.column_options.keys()
        for expected_column in gl.COL_NAMES_LIST_ALL:
            if expected_column not in given_columns:
                expected_empty_columns.append(expected_column)
        for column in expected_empty_columns:
            column_list = self.result_dataframe_1[column].tolist()
            for entry in column_list:
                self.assertTrue(
                    (entry is None) or
                    (len(entry) == 0)
                )


class TestFixMoneyColumns(unittest.TestCase):
    """Tests for fix_money_columns()
    Method should fix values in "Inflow" and "Outflow" columns
    """

    def test_removes_nonnumerics_except_decimal(self):
        """Tests that method strips all non-numerics except decimal separator
        """
        test_input_1 = np.array([[
            "DATE",
            "TIME",
            "TRANSACTION",
            "CHANNEL",
            "DESCRIPTION",
            "CHQ NO.",
            "Outflow",
            "Inflow",
            "BALANCE"
        ], [
            "01/02/2017",
            "10:11",
            "X2",
            "ENET",
            "FOO",
            "",
            "-500.00",
            "",
            "+483,346.08"
        ], [
            "28/02/2017",
            "16:17",
            "X1",
            "BCMS",
            "NERTZ",
            "",
            "",
            "+142,442.50",
            "+514,138.80"
        ]
        ])
        test_dataframe_1 = pd.DataFrame(
            data=test_input_1[1:, 0:],
            index=range(test_input_1.shape[0] - 1),
            columns=test_input_1[0, 0:]
        )
        separator = gl.DECIMAL_SEPARATOR.PERIOD
        self.result_dataframe_1 = p2y.fix_money_columns(
            test_dataframe_1, separator
        )
        regex = r"\d+\.\d{2}"
        col_list_oflow = self.result_dataframe_1[gl.COL_NAME_OUTFLOW].tolist()
        col_list_iflow = self.result_dataframe_1[gl.COL_NAME_INFLOW].tolist()
        for outflow in col_list_oflow:
            if len(outflow) != 0:
                self.assertRegex(outflow, regex)
        for inflow in col_list_iflow:
            if len(inflow) != 0:
                self.assertRegex(inflow, regex)

    def test_strip_nondecimal_numerics_strips_correctly(self):
        """Tests that stripper function works properly
        """
        separator = gl.DECIMAL_SEPARATOR.PERIOD
        test_string_1 = "-500.00"
        test_string_2 = "+500.00"
        expected_string_1 = "500.00"
        test_string_3 = "5,000.00"
        expected_string_2 = "5000.00"
        result_1 = p2y.fix_money_value(test_string_1, separator)
        result_2 = p2y.fix_money_value(test_string_2, separator)
        result_3 = p2y.fix_money_value(test_string_3, separator)
        result_4 = p2y.fix_money_value(expected_string_1, separator)
        self.assertEqual(result_1, expected_string_1)
        self.assertEqual(result_2, expected_string_1)
        self.assertEqual(result_3, expected_string_2)
        self.assertEqual(result_4, expected_string_1)


class TestFixDateColumn(unittest.TestCase):
    """Tests for fix_date_column
    Method should fix strings in "Date" column to be easier to import to YNAB
    """

    def test_reformats_dates_correctly(self):
        """Tests that reformatted dates use MM/DD/YYYY format
        Month should be between 01 and 12
        Day should be between 01 and 31
        """
        test_input_1 = np.array([[
            "Date",
            "TIME",
            "TRANSACTION",
            "CHANNEL",
            "DESCRIPTION",
            "CHQ NO.",
            "WITHDRAWAL",
            "DEPOSIT",
            "BALANCE"
        ], [
            "01/02/2017",
            "10:11",
            "X2",
            "ENET",
            "FOO",
            "",
            "-500.00",
            "",
            "+483,346.08"
        ], [
            "28/02/2017",
            "16:17",
            "X1",
            "BCMS",
            "NERTZ",
            "",
            "",
            "+142,442.50",
            "+514,138.80"
        ]
        ])
        test_dataframe_1 = pd.DataFrame(
            data=test_input_1[1:, 0:],
            index=range(test_input_1.shape[0] - 1),
            columns=test_input_1[0, 0:]
        )
        bank = bf.BANK_FORMATS["SCB"]
        date_regex = bank[gl.BF_DATE_REGEX]
        date_repl = bank[gl.BF_DATE_REPLACE]
        result_dataframe_1 = p2y.fix_date_column(
            test_dataframe_1, date_regex, date_repl
        )
        col_list_date = result_dataframe_1[gl.COL_NAME_DATE].tolist()
        for the_date in col_list_date:
            the_date_list = the_date.split("/")
            the_date_string_month = the_date_list[0]
            the_date_string_day = the_date_list[1]
            the_date_string_year = the_date_list[2]
            the_date_string_length_year = len(the_date_string_year)
            self.assertEqual(len(the_date_string_month), 2)
            self.assertEqual(len(the_date_string_day), 2)
            self.assertTrue(the_date_string_length_year == 4)
            the_date_month = int(the_date_string_month)
            the_date_day = int(the_date_string_day)
            self.assertGreater(the_date_month, 0)
            self.assertGreater(the_date_day, 0)
            self.assertLess(the_date_month, 13)
            self.assertLess(the_date_day, 32)


if __name__ == '__main__':
    unittest.main()
