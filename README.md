# PDF2YNAB

Converts bank transaction files to CSV file formatted for YouNeedABudget
Both PDF and CSVs can be reformatted

## Installation

1. Install Java 8+
2. pip3 install -r requirements.txt

## Usage

`python3 pdf2ynab.py "SCB" bank_pdf.pdf january.csv`

### Arguments
- bank_code
	- 3 letter code representing the bank that the PDF/CSV is from
- input_file
	- Path to the PDF/CSV to be reformatted
- output_file
	- Path to the output CSV file

## A note on contributing
Testing your contributions involves using bank data PDFs and CSVs, and clearly having PDFs full of your personal bank data is a problem.
If you'd like to contribute, make sure not to commit any files that have sensitive bank data.
- If PDFs or CSVs are edited to remove personal data, they can be committed and be part of pull requests.
- If you're doing integration tests that actually read from sensitive PDFs, separate those tests into their own file and don't add it.
- To make sure you don't accidentally add and commit sensitive files, add them to your .gitignore file.

## History

0.1.0 - Initial release

## Credits

By Ryan Oldford (ryan.oldford@gmail.com)