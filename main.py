from requests_html import HTMLSession
from PIL import Image, ImageStat
import time, requests, json, re, sqlite3, os.path, unicodedata, colorgram

conn = None
c = None

def download_file(url):
  local_filename = img_dir + url.split('/')[-1].split('=')[-1] + ".jpg"
  # NOTE the stream=True parameter
  r = requests.get(url, stream=True)
  with open(local_filename, 'wb') as f:
      for chunk in r.iter_content(chunk_size=1024): 
          if chunk: # filter out keep-alive new chunks
              f.write(chunk)
  return local_filename

def slugify(value, allow_unicode=False):
  """
  Convert to ASCII if 'allow_unicode' is False. Convert spaces to hyphens.
  Remove characters that aren't alphanumerics, underscores, or hyphens.
  Convert to lowercase. Also strip leading and trailing whitespace.
  """
  value = str(value)
  return value
  if allow_unicode:
      value = unicodedata.normalize('NFKC', value)
  else:
      value = unicodedata.normalize('NFKD', value).encode('ascii', 'ignore').decode('ascii')
  value = re.sub(r'[^\w\s-]', '', value).strip().lower()
  return re.sub(r'[-\s]+', '-', value)

class Artist():
    artist_catalogue = ""
    color_db_id = 0
    base_url="http://www.the-athenaeum.org"

    def __init__(self, name):
        self.name = name
        self.url = self.findUrl()
        self.artworks = []

    def findUrl(self):
        if Artist.artist_catalogue == "":
            r = session.get("http://www.the-athenaeum.org/art/counts.php?s=au&m=a")
            Artist.artist_catalogue = {i.text: i.attrs.get('href') for i in r.html.find("tr > td:nth-child(1) > a:nth-child(1)")}
            # print(len(Artist.artist_catalogue))
            
        r = session.get(self.base_url + Artist.artist_catalogue.get(self.name))
        # partial css selector works here, whereas full css selector fails
        artwork_list_a = r.html.find("tr > td > a:nth-child(4)")
        return artwork_list_a[0].attrs.get("href")

    def addArtwork(self, artwork):
        self.artworks.append(artwork)

    def acquireArtworks(self):
        r = session.get(self.base_url + self.url)
        page_count_element = r.html.find("div.subtitle > a")
        if page_count_element:
            page_count = len(page_count_element) + 1
        else:
            page_count = 1

        paintings = 0
        non_paintings = 0

        for p in range(1, page_count):
            time.sleep(0.2)
            paginated_res = session.get(self.base_url + str.format("{}&p={}", self.url, p))
            titles = [title_link.text for title_link in paginated_res.html.find('tr > td:nth-child(2) > div:nth-child(1) > a:nth-child(1)')]
            thumbnails = [img.attrs.get('src') for img in paginated_res.html.find('tr > td:nth-child(1) > a:nth-child(1) > img:nth-child(1)')]
            descriptions = [description.text for description in paginated_res.html.find('tr > td:nth-child(2)')][1:]
        
            for item in zip(thumbnails, descriptions, titles):
                print("page: {}\t{}/{}".format(p, paintings, non_paintings), end="\r")
                if "Painting" not in item[1] and "Collage" not in item[1]:
                    non_paintings += 1
                    continue
                else:
                    paintings += 1
                title = slugify("".join([letter for letter in item[2] if letter is not "'"]))
                
                img_url = item[0]
                img_id = img_url.split('/')[-1].split('=')[-1] + ".jpg"
                # mo = yearRegex.search(item[1])
                mo = re.findall(r'\(([0-9-]+)\)', item[1])
                if mo:
                    year = mo[0]
                else:
                    year = None

                img_path = "http://www.the-athenaeum.org/art/" + img_url
                local_path = img_dir + img_path.split('/')[-1].split('=')[-1] + ".jpg"
                if not os.path.isfile(local_path):
                    download_file(img_path)
                    time.sleep(0.2)
                im = Image.open(local_path)
                
                palette = colorgram.extract(im, 20)
                palette.sort(key=lambda c: c.hsl.h)
                self.writeColorsToDatabase(palette, img_path)

                stats = ImageStat.Stat(im)
                average_color_in_hex = [hex(int(avg_band))[-2:] for avg_band in stats.mean]
                if len(average_color_in_hex) == 3 and year:
                    self.artworks.append({"title": title ,"online_file_path" : img_path, "local_thumbnail_url" : local_path, "hex_code" : "".join(average_color_in_hex), "year" : year})
                im.close()

    def writeArtistToDatabase(self):
        c.execute("INSERT INTO Artist VALUES (\'{}\')".format(self.name))
        conn.commit()

    def writeArtworkToDatabase(self, artwork):
        # print("INSERT INTO Artwork VALUES (\'{}\', \'{}\', \'{}\', \'{}\', \'{}\')".format(artwork.get('hex_code'), artwork.get('online_file_path'), artwork.get('year'), artwork.get('title'), self.name))
        c.execute("INSERT INTO Artwork VALUES (\'{}\', \'{}\', \'{}\', \'{}\', \'{}\')".format(artwork.get('hex_code'), artwork.get('online_file_path'), artwork.get('year'), artwork.get('title'), self.name))
        # conn.commit()

    def writeArtworksToDatabase(self):
        print("Writing {} by {} to database.".format(len(self.artworks), self.name))
        for artwork in self.artworks:
            self.writeArtworkToDatabase(artwork)
        conn.commit()
    
    def writeToDatabase(self):
        self.writeArtistToDatabase()
        self.writeArtworksToDatabase()
    
    def writeColorsToDatabase(self, colors, url):
        for color in colors:
            self.writeColorToDatabase(color, url)
        # print("INSERT INTO ArtworkColor VALUES (\'{}\', \'{}\')".format(Artist.color_db_id, url))
        # conn.commit()
    
    def writeColorToDatabase(self, color, url):
        # print("INSERT INTO Color VALUES (\'{}\', \'{}\', \'{}\', \'{}\')".format(color.hsl.h, color.hsl.s, color.hsl.l, Artist.color_db_id))
        # c.execute("INSERT INTO Color VALUES (\'{}\', \'{}\', \'{}\', \'{}\', \'{}\')".format(, Artist.color_db_id))
        c.execute("INSERT INTO ArtworkColor VALUES (\'{}\', \'{}\',\'{}\', \'{}\',\'{}\')".format(color.hsl.h, color.hsl.s, color.hsl.l, color.proportion, url))
        Artist.color_db_id += 1


class Artwork():
    def __init__(self, url, year, avg_color):
        self.url = url
        self.year = year
        self.avg_color = avg_color
        self.colors = []

def setupDatabase(db_name):
    global conn
    # if os.path.isfile(db_name):
    #     os.remove(db_name)
    conn = sqlite3.connect(db_name)
    global c
    c = conn.cursor()

    commands = [
        '''
        CREATE TABLE IF NOT EXISTS Artwork (
            hex_code VARCHAR(6),
            thumbnail_url VARCHAR(61),
            year VARCHAR(15),
            title VARCHAR(400),
            artist_name VARCHAR(30),
            FOREIGN KEY(artist_name) REFERENCES artist(name),
            PRIMARY KEY(thumbnail_url)
        );
        ''',
        '''
        CREATE TABLE IF NOT EXISTS ArtworkColor (
            h VARCHAR(3),
            s VARCHAR(3),
            l VARCHAR(3),
            p REAL,
            artwork_url VARCHAR(61),
            FOREIGN KEY(artwork_url) REFERENCES artwork(thumbnail_url)
        );
        ''',
        '''
        CREATE TABLE IF NOT EXISTS Artist (
            name VARCHAR(30) NULL
        );
        '''
        ]

    for command in commands:
        c.execute(command) 

def closeDatabase():
    conn.close()

if __name__ == "__main__":
    yearRegex = re.compile(r'\(([0-9-]+)\)')
    img_dir = './thumbnails/'
    session = HTMLSession()

    artists = []
    artist_names = [
        "BOCCIONI, Umberto",
        "BRAQUE, Georges",
        "CÉZANNE, Paul",
        "DELACROIX, Eugène",
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

    setupDatabase("painters5.db")
    for name in artist_names:
        artists.append(Artist(name))
        print("finding artwork by {}".format(artists[-1].name))
        artists[-1].acquireArtworks()
        artists[-1].writeToDatabase()

    closeDatabase()

    

"""
for link in links:
    linked_image_response = session.get("http://www.the-athenaeum.org/art/" + link)

    anchor_tag_to_big_image = list(linked_image_response.html.find('a'))[5]#imgTextHolder > table:nth-child(1) > tbody:nth-child(1) > tr:nth-child(1) > td:nth-child(1) > table:nth-child(1) > tbody:nth-child(1) > tr:nth-child(2) > td:nth-child(1) > a:nth-child(1)', first=True)

    baseurl = "/".join(r.html.base_url.split("/")[:-1])
    big_image_link = baseurl + "/" + anchor_tag_to_big_image.attrs.get('href')
    download_file(big_image_link)
    print(str.format("download success: {}", big_image_link), end='\n')
    time.sleep(0.1)
"""
