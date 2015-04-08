uk-public-spending
------------------

#### Scraper

`scraper.py` scrapes public spending data from [data.gov.uk] (http://data.gov.uk/).

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

#### To do

+ Scraped spending files are those that satisfy the search criteria "spend". Is there any other search criteria to use?

+ As a result, some scraped files are not public spending files. For example, the Office for National Statistics publishes Family Spending files. Those files satisfy the search criteria "spend" but are not public spending files. Is there a way to exclude those files?

+ The number of scraped publishers from the [API] (http://data.gov.uk/api/3/action/organization_list) is slightly lower than the number of publishers according to the [web interface] (http://data.gov.uk/publisher): 1326 vs. 1331. Why?

#### License

All code is licensed under the GNU General Public License version 2. See `LICENSE.txt`.

