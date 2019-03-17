// client-side js
// run by the browser each time your view template referencing it is loaded
let artworks = [];
let mouseDataMap = {};
let stripWidth = 6;

// define variables that reference elements on our page
const previewParent = document.getElementById('preview');
const artworksList = document.getElementById('artworks');
const artistSelect = document.getElementById('input-select');

const rangeInput = document.getElementById('input-range');

const sleep = function(time) {
  return new Promise(function(resolve, reject) {
    setTimeout(function() {
      resolve();
    }, time);
  });
}

const preview_div = document.createElement('div');
preview_div.classList.add("dn", "bw2", "b-white", "bg-white", "sans-serif", "f7", "dark-gray", "b", "flex-column", "m-auto", "pa4");
preview_div.style["background-color"] = "rgba(255,255,255,0.9)";
preview_div.style["z-index"] = 2;
previewParent.appendChild(preview_div)

artworksList.addEventListener("mouseover", function( event ) {
    preview_div.classList.remove("dn")
      preview_div.classList.add("flex");
    const preview_img = document.createElement('img');
    const preview_description = document.createElement('p');
    preview_description.classList.add("tc");
    const item_data = mouseDataMap[event.target.id]
    preview_img.src = item_data.link
    preview_description.innerText = `${item_data.title}, ${item_data.year}`
    
    preview_div.appendChild(preview_img);
    preview_div.appendChild(preview_description);
    // setTimeout(function() {
    //   preview_img.remove();
    // }, 2000);
  }, false);

artworksList.addEventListener("mouseout", function( event ) {
    while(preview_div.firstChild){
      preview_div.removeChild(preview_div.firstChild);
    }
    preview_div.classList.add("dn")
      preview_div.classList.remove("flex");
  }, false);

const getArtistsListener = function() {
  // parse our response to convert to JSON
  let artists = JSON.parse(this.responseText);
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
      // setTimeout(function() {
        appendNewArtwork(row, index); 
      // }, (100.0/artworks.length) * index);
  });
  
  const scrollOptions = {
    left: artworksList.scrollWidth,
    behavior: 'smooth'
  }
  artworksList.scrollTo(scrollOptions);
}


const artworkRequest = new XMLHttpRequest();
artworkRequest.onload = getArtworksListener;
artworkRequest.open('get', '/getArtworks/' + "Raphael");
artworkRequest.send();

const artistRequest = new XMLHttpRequest();
artistRequest.onload = getArtistsListener;
artistRequest.open('get', '/getArtists');
artistRequest.send();

// a helper function that creates a list item for a given dream
const appendNewArtwork = function(artwork, index) {
  const artworkID = artwork.id
  let outerLI = document.getElementById(artworkID)
  if(!outerLI){
    outerLI = document.createElement('ul');
    outerLI.id = artworkID
    outerLI.classList.add("flex", "flex-column", "h-100", "w-100")
    outerLI.style['min-width'] = `${stripWidth}px`;
    artworksList.appendChild(outerLI);
  }
  const newListItem = document.createElement('li');
  newListItem.style['background-color'] = `hsl(${(artwork.h/255*360)}, ${(artwork.s/255*100)}%, ${(artwork.l/255*100)}%)`;
  newListItem.classList.add("ma0", "w-100", "item", "dib", "flex-start");
  //
  // newListItem.style['flex-basis'] = "10%";
  
  newListItem.style['flex-grow'] = artwork.p;
  mouseDataMap[index] = artwork;
  newListItem.id = index;
  outerLI.appendChild(newListItem);
  
}

// delay = new Promise() {
// }

// listen for the form to be submitted and add a new dream when it is
artistSelect.onchange = function(event) {
  // stop our form submission from refreshing the page
  event.preventDefault();
  
  while (artworksList.hasChildNodes()) {
    artworksList.removeChild(artworksList.lastChild);
  }
  
  const artworkRequest = new XMLHttpRequest();
  artworkRequest.onload = getArtworksListener;
  artworkRequest.open('get', '/getArtworks/' + artistSelect.value);
  artworkRequest.send();
  // get dream value and add it to the list
  // dreams.push(dreamInput.value);
  // appendNewDream(dreamInput.value);

  // reset form 
  // dreamInput.value = '';
  // dreamInput.focus();
};

rangeInput.onchange = function(event) {
  stripWidth = rangeInput.value;
  artworksList.childNodes.forEach((e) => {
    e.style['min-width'] = `${stripWidth}px`;
  })
}


const sort_types = ["year", "hue", "saturation", "lightness"]
sort_types.forEach((type) => {
  document.getElementById(type).addEventListener('click', (event) => {
    event.preventDefault();

    while (artworksList.hasChildNodes()) {
      artworksList.removeChild(artworksList.lastChild);
    }
    const artworkRequest = new XMLHttpRequest();
    artworkRequest.onload = getArtworksListener;
    if(type != "year"){
      type = type[0]
    }
    artworkRequest.open('get', `/getArtworks/${artistSelect.value}/${type}`);
    artworkRequest.send();
  });
})