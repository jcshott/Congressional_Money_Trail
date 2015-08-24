// control get members by address using Google geocode and ajax req to get_address route
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

      // {'state_value': $("#state_value").val()};
      var latitude = results[0].geometry.location.G
      var longitude = results[0].geometry.location.K


      var coordinates = {'latitude': latitude, 'longitude': longitude}

        $.post("/address_search", coordinates, function (result) {
        
        $('#repsByAddress').html();
        $('#your_district_reps').show();


        var legislators = result.legislators_by_address

        for (var i in legislators) { 
          if (legislators[i].chamber === "House" && legislators[i].district === 0) {
              district = legislators[i].state
            } else if (legislators[i].chamber === "House") {
              district = legislators[i].district
            };
          }
          
        $('#repsByAddress').html("Your Congressional Delegation for District " + district);
         
        $('.member_choice option').remove();

        for (var i in legislators) {
                           
          $('#address_member_list').append($("<option class='member_choice'></option>").val(legislators[i].leg_id).text(legislators[i].title + ". " + legislators[i].first + " " + legislators[i].last + " (" + legislators[i].party + ")"));
        }
                
        });

      }

     else {
      alert('Address could not be found for the following reason: ' + status);
    }
  });
}


// Control drop-down menu using Ajax show only the legislators from the selected state
function showLegislators(evt) {

  evt.preventDefault();
  $('.member_choice option').remove();
  $('#your_district_reps').html();
  //post request takes a dictionary so send key/value pair of the key I want to get 
  state_value = {'state_value': $("#state_value").val()};


  //ajax that sends the state selected and gets back the json values id'd on server.
  //parse and put into the dropdown menu. assigning the leg_id to the value of the selection so can grab that on server side to query for contribution information.

  $.post("/state_info", state_value, function (result) {
      

    if (result.senators) {
      $('#member_list').append("<option class='chamber_label'>" + "Senators" +"</option>");
      
      for (var i in result.senators) {$('#member_list').append($("<option class='member_choice'></option>").val(result.senators[i].leg_id).text(result.senators[i].title + ". " + result.senators[i].first + " " + result.senators[i].last + " (" + result.senators[i].party + ")")); }
    }
    
    // check for empty seats
    
    if (result.representatives.length > 0) {
      $('#member_list').append("<option class='chamber_label'>" + "House Members" +"</option>");
      
      var representatives = result.representatives
      
      // thanks stack overflow
      function SortByDistrict(a, b){
        var aDist = a.district;
        var bDist= b.district; 
        return ((aDist < bDist) ? -1 : ((aDist > bDist) ? 1 : 0));
      };

      var sorted_reps = representatives.sort(SortByDistrict);

      // define special case for at-large (no district, only house member)
      for (var i in sorted_reps){
        if (sorted_reps[i].district === 0) {
          district = " - At-Large"
        } else {
          district = " - " + sorted_reps[i].district
        };
          
        // cycle through list of representatives returned, to pull relevant info out & put in drop-down menu
        
        $('#member_list').append($("<option class='member_choice'></option>").val(sorted_reps[i].leg_id).text(sorted_reps[i].title + ". " + sorted_reps[i].first + " " + sorted_reps[i].last + " (" + sorted_reps[i].party + district + ")")); 

        };
    } else {
      $('#member_list').append($("<option ></option>").text("Seat is vacant, choose again."));
      $('#submit_member').attr("class", "disabled");
    }

    });
    
    $("#legislators_display").show();

  }


