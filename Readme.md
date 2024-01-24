# Very quick and dirty importer for Mediawiki dumps into wikijs

This tool can take a dump of a MediaWiki database and ingest files and articles to a WikiJS. It was meant to work one time for our makerspace to migrate from MediaWiki to WikiJS so don't expect too much from it.  It worked good enough for us but your mileage may vary. As the code is here you can always adapt it to ingest your data.

Usage:

1. Dump your MediaWiki database to an XML archive 
``` 
php dumpBackup.php --current --include-files --quiet  \
    --uploads --output=/tmp/data/mediawiki_dump.xml

```

2. Build and run the docker
```
docker build . -t mwimporter
docker run --rm -it -v "/tmp/data:/data" -e "GRAPHQLURL=<your URL to wikijs>" \
           -e "GRAPHQLKEY=<your API token>" \
           -e "DUMPFILE=<filename to import>.xml" mwimporter
```
You can set option UPLOAD='False' to skip uploading of files in the dump and set CREATE='False' to skip creating of articles if desired.

If you got the keys and URLs correct it will convert your articles from MediaWiki format to HTML format for the ckeditor so you can edit in a more WYSIWYG fashion. It will also import files and images. If your articles are referring to the images it will work in most cases but it doesn't compensate for URL-encoded filenames so not all pages will render perfectly. 

Count on some additional manual work on cleaning up articles after the import, but it does mitigate the pain of migration.

