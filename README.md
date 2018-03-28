# html-link-checker
Crawl a website for broken links

Most useful for printing bad links + error messages:
```bash
    python checker.py http://icecube.wisc.edu --debug 2>&1|grep -v checking
```
