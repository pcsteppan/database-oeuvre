// init project
var express = require('express');
var bodyParser = require('body-parser');
var app = express();
app.use(bodyParser.urlencoded({ extended: true }));

// http://expressjs.com/en/starter/static-files.html
app.use(express.static('public'));

// init sqlite db
var fs = require('fs');
var dbFile = 'artdata4.db';
var exists = fs.existsSync(dbFile);
var sqlite3 = require('sqlite3').verbose();
var db = new sqlite3.Database(dbFile, (err) => {
  if(err) {
    console.log('uh oh', err)
  }
});

// http://expressjs.com/en/starter/basic-routing.html
app.get('/', function(req, res) {
  res.sendFile(__dirname + '/views/index.html');
});

// endpoint to get all the dreams in the database
// currently this is the only endpoint, ie. adding dreams won't update the database
// read the sqlite3 module docs and try to add your own! https://www.npmjs.com/package/sqlite3
app.get('/getArtworks/:artist', function(req, res) {
  // console.log('getting artworks')
  //ArtworkColor.artwork_url = Artwork.thumbnail_url and
  db.all(`select Art.id, Art.Title, Art.link, Art.year, C.h, C.s, C.l, AC.p
    from Artist a, Artwork Art, Color C, Artworkcolor AC
    where a.name = "${req.params.artist}"
	    and a.id=art.artist_id
	    and ac.color_id = c.id
	    and ac.artwork_id = art.id
    order by art.year, art.id, ac.p`, function(err, rows) {
    res.send(JSON.stringify(rows));
  });
});

app.get('/getArtworks/:artist/:sort', function(req, res) {
  if(!['h','s','l','year'].includes(req.params.sort)){
    console.log(req.params.sort)
    return
  }
  
  //ArtworkColor.artwork_url = Artwork.thumbnail_url and
  db.all(`select Art.id, Art.Title, Art.link, Art.year, C.h, C.s, C.l, AC.p
    from Artist a, Artwork Art, Color C, Artworkcolor AC, (select avg(${req.params.sort}) as avg_sort, artwork.id as avg_id from color, artwork, artworkcolor where artwork.id = artworkcolor.artwork_id and color.id=artworkcolor.color_id group by artwork.id)
    where a.name = "${req.params.artist}"
	    and a.id=art.artist_id
	    and ac.color_id = c.id
	    and ac.artwork_id = art.id
		and avg_id=art.id
    order by avg_sort, ac.p`, function(err, rows) {
    res.send(JSON.stringify(rows));
  });
});

app.get('/getArtists', function(req, res) {
  db.all(`select artist.name
          from artist, (select min(artwork.year) as earliest_year, artist.id as id2 from artwork, artist where artwork.artist_id = artist.id group by artist.id)
          where artist.id = id2
          order by earliest_year` , function(err, rows) {
    res.send(JSON.stringify(rows));
  });
});

app.get('/getPalette/:url', function(req, res) {
  db.all('SELECT * from ArtworkColor where url = ' + req.params.url, function(err, rows){
    const palette = JSON.stringify(rows)
    console.log(palette)
  })
})

// listen for requests :)
var listener = app.listen(process.env.PORT, function() {
  console.log('Your app is listening on port ' + listener.address().port);
});
