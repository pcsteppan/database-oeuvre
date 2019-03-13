// server.js
// where your node app starts

// init project
var express = require('express');
var bodyParser = require('body-parser');
var app = express();
app.use(bodyParser.urlencoded({ extended: true }));

// we've started you off with Express, 
// but feel free to use whatever libs or frameworks you'd like through `package.json`.

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

// if ./.data/sqlite.db does not exist, create it, otherwise print records to console
db.serialize(function(){
  if (!exists) {
//     console.log("Does not exist");
//     db.run('CREATE TABLE Dreams (dream TEXT)');
//     console.log('New table Dreams created!');
    
//     // insert default dreams
//     db.serialize(function() {
//       db.run('INSERT INTO Dreams (dream) VALUES ("Find and count some sheep"), ("Climb a really tall mountain"), ("Wash the dishes")');
//     });
  }
  else {
    console.log('Database "' + dbFile + '" ready to go!');
    db.each('SELECT *', function(err, row) {
      if ( row ) {
        console.log('record:', row);
      }
    });
  }
});

// http://expressjs.com/en/starter/basic-routing.html
app.get('/', function(request, response) {
  response.sendFile(__dirname + '/views/index.html');
});

// endpoint to get all the dreams in the database
// currently this is the only endpoint, ie. adding dreams won't update the database
// read the sqlite3 module docs and try to add your own! https://www.npmjs.com/package/sqlite3
app.get('/getArtworks/:artist', function(request, response) {
  // console.log('getting artworks')
  //ArtworkColor.artwork_url = Artwork.thumbnail_url and
  db.all(`SELECT A.year, A.thumbnail_url, A.title, A.artist_name, AC.h, AC.s, AC.l, AC.p
      from Artwork A, ArtworkColor AC
      where A.thumbnail_url = AC.artwork_url
        and A.artist_name like "%${request.params.artist}%"
        and year <> "None"
      order by year, AC.s`, function(err, rows) {
    response.send(JSON.stringify(rows));
  });
});

app.get('/getArtists', function(req, res) {
  db.all('SELECT * from Artist' , function(err, rows) {
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
