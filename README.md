Database Oeuvre
=================

Take every image of every painting/collage of twenty artists of the twentieth century. Then distill each image into a palette and arrange them chronologically.

Then print these images into a physical book.
![printed book of the project with stab binding](https://cdn.glitch.com/eee3898b-001d-4329-b12a-7a5714a25d06%2F20190307_154943.jpg?1552350044838)

Technical details
------------

On the front-end,
- colors rendered through simple DOM + css, mainly flexbox
- preview images hosted by webscraped site

On the back-end,
- based on node
- all data stored in a sqlite database file, constructed in python

Database
- sqlite file made through web scraping with [html-requests](https://html.python-requests.org/), the best python library for web scraping, and then calculating palletes with [Pillow](https://pillow.readthedocs.io/en/stable/) and [colorgram](https://pypi.org/project/colorgram.py/)


Made with [Glitch](https://glitch.com/)
-------------------

\ ゜o゜)ノ
