import globals as gl


BANK_FORMATS = {
    "SCB": {
        gl.BF_DESCRIPTION: "Siam Commercial Bank, Thailand",
        gl.BF_COL_FORMAT: {
            "date": gl.COL_NAME_DATE,
            "description": gl.COL_NAME_PAYEE,
            "withdrawal": gl.COL_NAME_OUTFLOW,
            "deposit": gl.COL_NAME_INFLOW,
            "deposits": gl.COL_NAME_INFLOW,
            "channel": gl.COL_NAME_MEMO
        },
        gl.BF_DATE_REGEX: r"(\d+)\/(\d+)\/(\d+)",
        gl.BF_DATE_REPLACE: r"\2/\1/\3",
        gl.BF_DECIMAL_SEPARATOR: gl.DECIMAL_SEPARATOR.PERIOD,
        gl.BF_DATE_SEPARATOR: gl.DATE_SEPARATOR.SLASH
    }
}
