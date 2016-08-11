// info sidebar toggle
$("#menu-toggle").click(function(e) {
	e.preventDefault();

	$("#wrapper").toggleClass("active");

    if ($('#dataButton').attr("href")) {
        $('#dataButton').removeAttr("href");
    } else {
        $('#dataButton').attr("href", "#dataInfo");
    };

    if ($('#graphButton').attr("href")) {
        $('#graphButton').removeAttr("href");
    } else {
        $('#graphButton').attr("href", "#graphInfo");
    };

    if ($('#siteButton').attr("href")) {
        $('#siteButton').removeAttr("href");
    } else {
        $('#siteButton').attr("href", "#siteInfo");
    };

});

// accordion toggle in info
$('.collapse').collapse("toggle");
