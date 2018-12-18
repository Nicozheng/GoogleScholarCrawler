# Google Scholar Crawler
This is a short python program that search, format, and download paper form google scholar.

## Requirements
It has following requirements:

    - selenium  `pip install selenium`
    - webdriver `brew install selenium-server-standalone`
    - requests `pip install requests`
    - openpyxl `pip install openpyxl`

* I used the brew webdriver engine here, but you can change it to a local chromedriver file if you use Windows or Ubuntu.


## Using this program
1. download and unzip files in this git folder;
2. open terminal and cd to the target folder;
3. in target folder, change "config.json" file to change search keywords and target journals accordingly;
4. in terminal, use
```shell
python GoogleScholarCrawler.py config.json
```

## Functions
This program will create local file folders based on keywords and journals as following:
```shell
$ tree test_googlecrawer -d
test_googlecrawer
└── wikipedia  # keyword
    ├── information systems research  # journal
    ├── journal of management information systems
    ├── journal of the association for information systems
    ├── management science
    ├── mis quarterly
    └── operational research
```

In each folder, there is an excel log file recorded detailed search results (author, title, journal, year and whether pdf is avaliable).
There will also be all the pdf files that are publicly accessible in Google Scholar.

Here is how the log file will look like:
![log file sample](https://github.com/Nicozheng/GoogleScholarCrawler/blob/master/log_file_sample.png?raw=true)

The pdf files will be renamed as:
`author-year-title-journal.pdf`


## Get in touch
You can find me at
`nico921113[at]gmail[dot]com`
