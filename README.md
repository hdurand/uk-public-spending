uk-public-spending
------------------

#### Scraper

`scraper.py` scrapes public spending data from [data.gov.uk] (http://data.gov.uk/) (spend over £25,000 for departments and spend over £500 for local governments).

`scraper.py` searches packages of files that satisfy the search criteria "spend*" or "spent" or "expenditure" from [data.gov.uk] (http://data.gov.uk/).
Then, it keeps files with 500 or 25000 (written in any way) in the package title, the package name, the package description (notes), or the file description.

Traffic limits on data.gov.uk:
+ no concurrency
+ up to a maximum of 5 requests per second

See data.gov.uk [Terms and conditions] (http://data.gov.uk/terms-and-conditions).

`scraper.py` waits at least 0.3 seconds between two requests.

See data.gov.uk [API] (https://datagovuk.github.io/guidance/api.html) for more information about the API.

#### Data

`data/publishers-sample.csv`: sample of data.gov.uk publishers.

`data/datafiles-sample.csv`: sample of data.gov.uk spending files.

See `datapackage.json` and [Tabular Data Packages] (http://data.okfn.org/doc/tabular-data-package) for more information.

#### License

All code is licensed under the GNU General Public License version 2. See `LICENSE.txt`.

