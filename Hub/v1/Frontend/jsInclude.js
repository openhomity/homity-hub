$(document).ready(function() {
	$.mobile.page.prototype.options.addBackBtn = "true";
	//$.mobile.page.prototype.options.backBtnText = "Go Back";
	$("#insideLights").click(function() {
		console.log('inside');
		var dataString = "status=false";
		$.ajax({
			type: "PUT",
			url: "v1/pin/77a377c765e9417e9175f048b764b347",
			data: dataString,
			success: function() {
				window.location.reload(true);
			}
		});
	});
	$("#outsideLights").click(function() {
		console.log('outside');
		var dataString = "status=false";
		$.ajax({
			type: "PUT",
			url: "v1/pin/43f79b58bbfb418d9436f01932020177",
			data: dataString,
			success: function() {
				window.location.reload(true);
			}
		});
	});
});