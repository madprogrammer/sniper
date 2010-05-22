
function domReady()
{
	$("td.endtime").each(function() {
		$(this).countdown({
			until: fromISO8601($(this).text()),
			compact: true
		});
	});
}
