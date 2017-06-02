import enum


COL_NAME_DATE = "Date"
COL_NAME_PAYEE = "Payee"
COL_NAME_CATEGORY = "Category"
COL_NAME_MEMO = "Memo"
COL_NAME_OUTFLOW = "Outflow"
COL_NAME_INFLOW = "Inflow"
COL_NAMES_LIST_ALL = [
    COL_NAME_DATE, COL_NAME_PAYEE, COL_NAME_CATEGORY,
    COL_NAME_MEMO, COL_NAME_OUTFLOW, COL_NAME_INFLOW
]
COL_NAMES_LIST_REQUIRED = [
    COL_NAME_DATE, COL_NAME_PAYEE,
    COL_NAME_OUTFLOW, COL_NAME_INFLOW
]
COL_NAMES_LIST_OPTIONAL = [COL_NAME_CATEGORY, COL_NAME_MEMO]

BF_DESCRIPTION = "description"
BF_COL_FORMAT = "column_format"
BF_DATE_REGEX = "date_regex"
BF_DATE_REPLACE = "date_repl"
BF_DATE_SEPARATOR = "date_separator"
BF_DECIMAL_SEPARATOR = "decimal_separator"


class DECIMAL_SEPARATOR(enum.Enum):
    PERIOD = "."
    COMMA = ","


class DATE_SEPARATOR(enum.Enum):
    SLASH = "/"
    DASH = "-"
