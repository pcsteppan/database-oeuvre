from requests_html import HTMLSession
from peewee import *
from PIL import Image, ImageStat
import colorgram, os.path, re, requests, sqlite3, time, unicodedata

if os.path.exists('artdata.db'):
    os.remove('artdata.db')

db = SqliteDatabase('artdata.db', pragmas={
    'journal_mode':'off',
    'synchronous' : '0',
    'locking_mode' : 'exclusive'
    }) # pragmas in hopes of faster writing time
catalogue = dict()

# Data Models
class Artist(Model):
    name = CharField()
    url = CharField()

    class Meta:
        database = db

class Artwork(Model):
    title = CharField(max_length=100)
    year = CharField(max_length=9)
    link = CharField(max_length=100)
    # size = CharField()
    artist = ForeignKeyField(Artist, backref='artworks')

    class Meta:
        database = db

class Color(Model):
    h = CharField(max_length=3)
    s = CharField(max_length=3)
    l = CharField(max_length=3)

    class Meta:
        indexes = (
            # create a unique on h/s/l
            (('h', 's', 'l'), True),
        )
        database = db

class ArtworkColor(Model):
    artwork = ForeignKeyField(Artwork, backref='artworkcolors')
    color = ForeignKeyField(Color, backref='artworkcolors')
    p = DecimalField()

    class Meta:
        primary_key = CompositeKey('artwork', 'color')
        database = db


def download_file(url, local_filename):
  r = requests.get(url, stream=True)
  with open(local_filename, 'wb') as f:
      for chunk in r.iter_content(chunk_size=1024): 
          if chunk: # filter out keep-alive new chunks
              f.write(chunk)
  return local_filename

db.connect()
session = HTMLSession()

artist_names = [
    "CÉZANNE, Paul",
    "DELACROIX, Eugène",
    "BOCCIONI, Umberto",
    "BRAQUE, Georges",
    "GAUGUIN, Eugene-Henri Paul",
    "GOGH, Vincent Willem van",
    "GORKY, Arshile",
    "HODLER, Ferdinand",
    "HOPPER, Edward",
    "KAHLO, Frida",
    "KANDINSKY, Wassily",
    "KIRCHNER, Ernst Ludwig",
    "KLIMT, Gustav",
    "MALEVICH, Kasimir Severinovich",
    "MATISSE, Henri-Émile-Bénoit",
    "MONDRIAN, Pieter Cornelis",
    "MONET, Oscar-Claude",
    "MUNCH, Edvard",
    "PICASSO, Pablo",
    "POUSSIN, Nicolas",
    "Raphael",
    "RENOIR, Pierre Auguste",
    "RIJN, Rembrandt van",
    "ROTHKO, Mark",
    "ROUSSEAU, Henri",
    "RUBENS, Peter Paul",
    "SCHIELE, Egon",
    "SCHWITTERS, Kurt",
    "SEURAT, Georges",
    "TOULOUSE-LAUTREC, Henri de",
    "DE ZURBARÁN, Francisco"
]

#acquire list of all people and store in catalogue
r = session.get("http://www.the-athenaeum.org/art/counts.php?s=au&m=a")
if os.path.exists("catalog.txt"):
    with open("catalog.txt", "r", encoding="utf8") as fhand:
        items = [i.split("::") for i in fhand.readlines()]
        catalog = {i[0] : i[1] for i in items}
else:
    with open("catalog.txt", "w", encoding="utf8") as fhand:
        catalog = {i.find("td")[0].text : i.find("td>a")[1].absolute_links.pop() for i in r.html.find("tr.r1, tr.r2")}
        for (k, v) in catalog.items():
            fhand.write("{}::{}\n".format(k, v))

# iterate through list of people
Artist.create_table()
Artwork.create_table()
Color.create_table()
ArtworkColor.create_table()



for artist_name in artist_names:
    # save people and their artwork listing
    try:
        artist = Artist.create(name=artist_name, url=catalog.get(artist_name))
    except:
        continue
    

for artist in Artist.select():
    time.sleep(0.2)
    page_n = 1
    print()
    temp_artworks = []
    temp_colors = []
    temp_artworkcolors = []
    while True:
        page_r = session.get(artist.url + "&p=" + str(page_n))
        page_n += 1

        artwork_items = page_r.html.find("tr.r1, tr.r2")

        if len(artwork_items) is 0:
            break

        for item_index, artwork_item in enumerate(artwork_items):
            print("Processing: {}\tPage: {}\tArtwork: {}".format(artist.name, str(page_n-1).zfill(2), str((page_n-2)*100+item_index+1).zfill(4)), end="\r")
            link = "/".join(artist.url.split("/")[:-1]) + "/" + artwork_item.find("td:nth-child(1) > a:nth-child(1) > img")[0].attrs.get('src')
            description = artwork_item.find("td:nth-child(2)")[0]
            title = description.find("div:nth-child(1) > a:nth-child(1)")[0].text
            year = re.findall(r'\(([0-9-]+)\)', description.text)
            if not ("Painting" in description.text or "Collage" in description.text):
                continue

            if len(year) is 1:
                year = year[0]
            else:
                continue
            
            artwork = Artwork.create(title=title,year=year,artist=artist,link=link)
            # artwork.save()
            temp_artworks.append(artwork)

            local_path = "images/{}.jpg".format(link.split("=")[-1])
            if not os.path.exists(local_path):
                download_file(link, local_path)
                time.sleep(0.2)
            
            im = Image.open(local_path)
            palette = colorgram.extract(im, 10)
            im.close()

            # palette.sort(key=lambda c: c.hsl.h)
            for color in palette:
                try:
                    my_color = Color.create(h=color.hsl.h, s=color.hsl.s, l=color.hsl.l)
                except:
                    my_color = Color.get(Color.h==color.hsl.h, Color.s==color.hsl.s, Color.l==color.hsl.l)
                my_color_join = ArtworkColor.create(artwork=artwork, color=my_color, p=color.proportion)    
print()
db.close()