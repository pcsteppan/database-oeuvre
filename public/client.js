// client-side js
// run by the browser each time your view template referencing it is loaded
let artworks = [];
let mouseDataMap = {};

// define variables that reference elements on our page
const previewParent = document.getElementById('preview');
const artworksList = document.getElementById('artworks');
const artistForm = document.forms[0];
const artistSelect = artistForm.elements['artist_select'];
console.log(artistSelect)

artworksList.addEventListener("mouseover", function( event ) {
    const preview_div = document.createElement('div');
    preview_div.classList.add("w-20", "bw1", "b-white", "bg-white", "sans-serif", "f7", "dark-gray", "b", "flex", "flex-column", "m-auto", "pa4");
    preview_div.style["background-color"] = "rgba(255,255,255,0.9)";
    const preview_img = document.createElement('img');
    const preview_description = document.createElement('p');
    preview_description.classList.add("tc");
    const item_data = mouseDataMap[event.target.id]
    preview_div.id = event.target.id + '-img';
    preview_img.src = item_data.thumbnail_url
    preview_description.innerText = `${item_data.title}, ${item_data.year}`
    preview_div.style["z-index"] = 2;
    preview_div.appendChild(preview_img);
    preview_div.appendChild(preview_description);
    previewParent.appendChild(preview_div)
    // setTimeout(function() {
    //   preview_img.remove();
    // }, 12000);
  }, false);

artworksList.addEventListener("mouseout", function( event ) {
    const preview_img = document.getElementById(event.target.id + '-img');
    preview_img.remove();
  }, false);

const getArtistsListener = function() {
  // parse our response to convert to JSON
  // console.log(this.responseText);
  let artists = JSON.parse(this.responseText);
  console.log(artists)
  artists.forEach( function(row) {
    appendNewArtist(row);
  });
}

const appendNewArtist = function(artist) {
  const newArtistItem = document.createElement('option');
  newArtistItem.value = artist.name;
  newArtistItem.innerText = artist.name;
  newArtistItem.classList.add("code", "ttu", "f7");
  artistSelect.appendChild(newArtistItem);
}

// a helper function to call when our request for artworks is done
const getArtworksListener = function() {
  // parse our response to convert to JSON
  artworks = JSON.parse(this.responseText);
  mouseDataMap = {}
  artworks.forEach( function(row, index) {
    appendNewArtwork(row, index);
    
  });
}

// request the dreams from our app's sqlite database
const artworkRequest = new XMLHttpRequest();
artworkRequest.onload = getArtworksListener;
artworkRequest.open('get', '/getArtworks/' + "BOCCIONI");
artworkRequest.send();

const artistRequest = new XMLHttpRequest();
artistRequest.onload = getArtistsListener;
artistRequest.open('get', '/getArtists');
artistRequest.send();

// a helper function that creates a list item for a given dream
const appendNewArtwork = function(artwork, index) {
  const artworkID = artwork.thumbnail_url.split('id=')[1]
  let outerLI = document.getElementById(artworkID)
  if(!outerLI){
    outerLI = document.createElement('ul');
    outerLI.id = artworkID
    outerLI.classList.add("flex", "flex-column", "h-100", "w-100")
    artworksList.appendChild(outerLI)
  }
  const newListItem = document.createElement('li');
  newListItem.style['background-color'] = `hsl(${(artwork.h/255*360)}, ${(artwork.s/255*100)}%, ${(artwork.l/255*100)}%)`;
  newListItem.classList.add("ma0", "w-100", "item", "dib", "flex-start");
  // newListItem.style['flex-basis'] = "10%";
  newListItem.style['flex-grow'] = artwork.p;
  mouseDataMap[index] = artwork;
  newListItem.id = index;
  outerLI.appendChild(newListItem);
}



// listen for the form to be submitted and add a new dream when it is
artistSelect.onchange = function(event) {
  // stop our form submission from refreshing the page
  event.preventDefault();
  
  while (artworksList.hasChildNodes()) {
    artworksList.removeChild(artworksList.lastChild);
  }
  
  const artworkRequest = new XMLHttpRequest();
  artworkRequest.onload = getArtworksListener;
  console.log("requesting: /getArtworks/" + artistSelect.value);
  artworkRequest.open('get', '/getArtworks/' + artistSelect.value);
  artworkRequest.send();
  // get dream value and add it to the list
  // dreams.push(dreamInput.value);
  // appendNewDream(dreamInput.value);

  // reset form 
  // dreamInput.value = '';
  // dreamInput.focus();
};
