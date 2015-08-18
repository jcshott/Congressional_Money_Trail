var geocoder

function initialize() {
  console.log("initialized")
  geocoder = new google.maps.Geocoder();
  
  document.getElementById('submit_geocode').addEventListener('click', function(evt) {
    evt.preventDefault();
    geocodeAddress(geocoder);
});
}

function geocodeAddress(geocoder) {
  
  var address = document.getElementById('address').value;
  
  geocoder.geocode({'address': address}, function(results, status) {
    if (status === google.maps.GeocoderStatus.OK) {
      console.log("map google call")
      // {'state_value': $("#state_value").val()};
      var latitude = results[0].geometry.location.G
      var longitude = results[0].geometry.location.K
      
      console.log(latitude)
      console.log(longitude)

      var coordinates = {'latitude': latitude, 'longitude': longitude}

      console.log(coordinates)

      $.post("/address_search", coordinates, function (result) {
        console.log(result)
      });
// NEED to set up ajax request to get the info and send back into a div #your_district_reps that shows members names, title, party. the link you click will send member id similar to picking from list
      // latitude = results[0].geometry.location.G
      // longitude = results[0].geometry.location.K

      // $.post("/address_search", state_value, function (result) {

      // }

    } else {
      alert('Geocode was not successful for the following reason: ' + status);
    }
  });
}