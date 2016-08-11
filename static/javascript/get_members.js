//list possible representatives only after choose state.
$("#state_pick").change("state_value", showLegislators);
$("#state_pick").change("state_value", function () {
	$("#noMember").hide();
});

$("#address_pick").on("submit", SearchByAddress);

// bind showing the TrailMapTree function call to the event named show map
//that is called after member choice is submitted (below)
$("#map_viz").bind("showMap", showTrailMapTree);

// send member_id to route that will send back info for member_profile
$("form.repsDistrict").on("submit", function (evt) {

	evt.preventDefault();

	var member = {'member': $('select.member_choice option:selected').val()};

	$.get("/trail_map", member, function(result){
		console.log("ajax call")
		// show the map visualization div and trigger the function call to d3 j.s. of TrailMapTree
		$("#my-callout").hide();

		$('body').css('background-image', 'none');
		$("#map_viz").show('slow', function () {

			 $(this).trigger('showMap');
			 $("body::before").attr("width", "120%");
			 $("body::before").attr("height", "120%");

		});

		$("#legislators_display").hide();
		$("#state_pick").hide();
		$("#pick_by_address").hide();
		$("#your_district_reps").hide();
		$("#new_choice").show();
		$(".forms").append(result);

	});
});

$("#new_choice").on("click", function (evt){
	$("#map_viz").empty();
	$("#state_pick").show();
	$('#state_pick').find('option:first').prop('selected', 'selected');
	$("#pick_by_address").show();
	$("#new_choice").hide();
	$("#member_profile").remove();

});

// controls getting congressional delegation by address using Google Maps Geocode API on server
function SearchByAddress(evt) {

    evt.preventDefault();

    address = {'address': $("#address").val()};

    $.post("/address_search", address, function (result) {

        $('#repsByAddress').html();
        $('#your_district_reps').show();


        var legislators = result.legislators_by_address

        for (var i in legislators) {
          var state = legislators[i].state;
          if (legislators[i].chamber === "House" && legislators[i].district === 0) {
              district = legislators[i].state
            } else if (legislators[i].chamber === "House") {
              district = legislators[i].district
            };
          }

        $('#repsByAddress').html(state + " District " + district);

        $('.member_choice option').remove();

        $('#address_member_list').append("<option class='form-control'>" + "State Delegation" +"</option>");

        for (var i in legislators) {

          $('#address_member_list').append($("<option class='member_choice form-control'></option>").val(legislators[i].leg_id).text(legislators[i].title + ". " + legislators[i].first + " " + legislators[i].last + " (" + legislators[i].party + ")"));
        }

        });
};


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

    // $('#member_list').append("<option class='form-control'>" + "State Delegation" +"</option>");

    if (result.senators) {
      $('#member_list').append("<option class='chamber_label form-control'>" + "Senators" +"</option>");
      // $('#member_list').append("<optgroup label='Senators'>");

      for (var i in result.senators) {$('#member_list').append($("<option class='member_choice'></option>").val(result.senators[i].leg_id).text(result.senators[i].title + ". " + result.senators[i].first + " " + result.senators[i].last + " (" + result.senators[i].party + ")")); };

      // $('#member_list').append("</optgroup>");
    }

    // check for empty seats

    if (result.representatives.length > 0) {
      $('#member_list').append("<option class='chamber_label form-control'>" + "House Members" +"</option>");
      // $('#member_list').append("<optgroup label='House Members'>");

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

        $('#member_list').append($("<option class='member_choice form-control'></option>").val(sorted_reps[i].leg_id).text(sorted_reps[i].title + ". " + sorted_reps[i].first + " " + sorted_reps[i].last + " (" + sorted_reps[i].party + district + ")"));
        // $('#member_list').append("</optgroup>");

        };
    } else {
      $('#legislators_display').hide();
      $('#noMember').show();
      // $('#submit_member').attr("class", "disabled");
    }

    });

    $("#legislators_display").show();

  }
