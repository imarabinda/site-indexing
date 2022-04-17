# First run   
```Python
pip install --upgrade google-api-python-client google-auth-httplib2 google-auth-oauthlib advertools
```
## Documentation

It is mandatory to get your google service account api key file and add it's path to `JSON_KEY_FILE` variable.
>Here's a [Indexing API Quickstart Guide](https://developers.google.com/search/apis/indexing-api/v3/quickstart)

`REQUEST_TYPE` enter default request type. By default it is `URL_UPDATED`.

`sitemap_url` enter your sitemap url. If empty getting urls from sitemap will be skipped.
`csv_path` enter your csv file path. If empty getting urls from csv file will be skipped.

>csv file must contain url column, request_type column is optional, add it if you need to overwrite default `REQUEST_TYPE` param.

Using `URLs` variable you can set your urls. It will be merged if you have requested urls from csv or sitemaps.

Using `EXCLUDE_URLs` you can remove specific url from batch request. 
>It is very useful when you're taking urls from sitemap and you want to exclude some urls.

Using `OVERWRITE_URLs` you can overwrite your urls `REQUEST_TYPE` param. 
>It is very useful when you're taking urls from sitemap and you want to overwrite some urls request type.

`main_engine()` is the entry function of this code.