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

        $('#your_district_reps').show()

        var legislators = result.legislators_by_address

        for (var i in legislators) {
          console.log(legislators[i].chamber)
          console.log(legislators[i].sen_rank)
          console.log(legislators[i].leg_id)
          
          if (legislators[i].chamber === "Senate" && legislators[i].sen_rank === "Senior Seat"){
            var senior_sen = legislators[i]
            }

          else if (legislators[i].chamber === "Senate" && legislators[i].sen_rank === "Junior Seat"){
            var junior_sen = legislators[i]
            }
          else {
            var house_rep = legislators[i]
          }
        
        // handle what members show up depending if there are vacant seats or its a house member only (i.e.delegates)  
        }
        if (senior_sen && junior_sen && house_rep) {
          $('#sen1').show();
          $('#sen1id').attr("value", senior_sen.leg_id);
          $('#sen1name').attr("value", senior_sen.title + ". " + senior_sen.first + " " + senior_sen.last + " (" + senior_sen.party + " - " + senior_sen.sen_rank + " )");

          $('#sen2').show();
          $('#sen2id').attr("value", junior_sen.leg_id);
          $('#sen2name').attr("value", junior_sen.title + ". " + junior_sen.first + " " + junior_sen.last + " (" + junior_sen.party + " - " + junior_sen.sen_rank + " )");

          $('#rep').show();
          $('#repId').attr("value", house_rep.leg_id);
          $('#repName').attr("value", house_rep.title + ". " + house_rep.first + " " + house_rep.last + " (" + house_rep.party + " - " + house_rep.district + " )");
        }

        else if (senior_sen && junior_sen) {
          
          $('#sen1').show();
          $('#sen1id').attr("value", senior_sen.leg_id);
          $('#sen1name').attr("value", senior_sen.title + ". " + senior_sen.first + " " + senior_sen.last + " (" + senior_sen.party + " - " + senior_sen.sen_rank + " )");

          $('#sen2').show();
          $('#sen2id').attr("value", junior_sen.leg_id);
          $('#sen2name').attr("value", junior_sen.title + ". " + junior_sen.first + " " + junior_sen.last + " (" + junior_sen.party + " - " + junior_sen.sen_rank + " )");
        }

        else if (senior_sen) {
          $('#sen1').show();
          $('#sen1id').attr("value", senior_sen.leg_id);
          $('#sen1name').attr("value", senior_sen.title + ". " + senior_sen.first + " " + senior_sen.last + " (" + senior_sen.party + " - " + senior_sen.sen_rank + " )");
        }

        else if (junior_sen) {
          $('#sen2').show();
          $('#sen2id').attr("value", junior_sen.leg_id);
          $('#sen2name').attr("value", junior_sen.title + ". " + junior_sen.first + " " + junior_sen.last + " (" + junior_sen.party + " - " + junior_sen.sen_rank + " )");
        }

        else if (!(senior_sen || junior_sen)){
          $('#rep').show();
          $('#repId').attr("value", house_rep.leg_id);
          $('#repName').attr("value", house_rep.title + ". " + house_rep.first + " " + house_rep.last + " (" + house_rep.party + " - " + house_rep.district + " )");
        }

        })

      }

     else {
      alert('Geocode was not successful for the following reason: ' + status);
    }
  });
}


// Control drop-down menu using Ajax show only the legislators from the selected state
function showLegislators(evt) {

  evt.preventDefault();
  $('#member_choice option').remove();
  $('#your_district_reps').html();
  //post request takes a dictionary so send key/value pair of the key I want to get 
  state_value = {'state_value': $("#state_value").val()};

  console.log(state_value)

  //ajax that sends the state selected and gets back the json values id'd on server.
  //parse and put into the dropdown menu. assigning the leg_id to the value of the selection so can grab that on server side to query for contribution information.

  $.post("/state_info", state_value, function (result) {
      console.log(result)
      console.log(result.representatives)
      console.log(result.representatives.length)

    if (result.senators) {
      $('#member_choice').append("<option class=chamber_label>" + "Senators" +"</option>");
      
      for (var i in result.senators) {$('#member_choice').append($("<option class=senate></option>").val(result.senators[i].leg_id).text(result.senators[i].title + ". " + result.senators[i].first + " " + result.senators[i].last + " (" + result.senators[i].party + ")")); }
    }
    
    // empty seats
    
    if (result.representatives.length > 0) {
      $('#member_choice').append("<option class=chamber_label>" + "House Members" +"</option>");
      
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
        
        $('#member_choice').append($("<option class=house></option>").val(sorted_reps[i].leg_id).text(sorted_reps[i].title + ". " + sorted_reps[i].first + " " + sorted_reps[i].last + " (" + sorted_reps[i].party + district + ")")); 

        };
    } else {
      $('#your_district_reps').html("Sorry, that seat is vacant")
    }

    });
    
    $("#legislators_display").show();

  }


