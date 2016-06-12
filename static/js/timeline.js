var scale = 0.05;
var now, startTime, stopTime;
var monthNames = ["January", "February", "March", "April", "May", "June", "July", "August", "September", "October", "November", "December" ];

var leftPos = function(time) {
	return scale * (time - startTime) / 1000.0 / 60;
}

var timeString = function(time) {
	var t = new Date(time);
	return [monthNames[t.getMonth()].substring(0, 3), t.getDate()].join(" ");
}

var splitOverlapping = function(lanes) {
	var ret = [];
	lanes.forEach(function(lane) {
		var newLanes = [ [] ];
		lane.forEach(function(ctf) {
			var collision = true;
			for (var i=0; i<newLanes.length; i++) {
				if (fitLane(newLanes[i], ctf)) {
					newLanes[i].push(ctf);
					collision = false;
					break;
				}
			}
			if (collision) newLanes.push([ctf]);
		});
		ret = ret.concat(newLanes);
	});
	return ret;
}

var bubbleUp = function(lanes, ctfs) {
	var returnLanes = lanes.concat([]);
	ctfs.forEach(function(ctf) {
		var i = returnLanes.length - 1;
		while (i >= 0) {
			if (!fitLane(returnLanes[i], ctf)) break;
			i -= 1;
		}
		if (i + 1 >= returnLanes.length) 
			returnLanes.push([ctf]);
		else
			returnLanes[i+1].push(ctf);
	});
	return returnLanes;
}

var group = function(arr, grouper) {
	var groups = {};
	arr.forEach(function(e) {
		var g = grouper(e);
		if (!groups[g]) groups[g] = [];
		groups[g].push(e);
	});
	return Object.keys(groups).sort().map(function(k) {
		return groups[k];
	});
}

var laneGrouper = function(t) {
	return 99;
}

var fitLane = function(lane, ctf2) {
	return !lane.some(function(ctf1) {
		return !(ctf1.endTime <= ctf2.startTime || ctf2.endTime <= ctf1.startTime);
	});
}

var renderCTF = function(ctf) {
	var ctf_days = ctf.duration / 7.0;
	var width = ctf.duration * 60 * scale;
	var left = leftPos(ctf.startTime);
	return "<a class='ctf' href='/events/" + ctf.id + "' style='width:" + width + "px;left:" + left + "px;'>"
		+ "<span class='name'>" + ctf.name + "</span>"
		+ "<span class='date'>" + timeString(ctf.startTime) + "</span>"
		+ "</a>";
}

$(document).ready(function() {
	now = Date.now();
	startTime = now - 7*24*60*60*1000;
	stopTime = startTime + 30*24*60*60*1000;

	$.get("/events/list/json", function(data) {
		data = JSON.parse(data);

		var daysBetween = 1;
		var time = new Date(startTime);
		time.setSeconds(0);
		time.setMinutes(0);
		time.setHours(0);

		var timeHeaders = [];
		while (time.getTime() < (stopTime - daysBetween*24*60*60*1000)) {
			var str = timeString(time);
			timeHeaders.push("<div class='timeheader" + (time.getDay() === 0 ? " week" : "") + "' style='left:" + leftPos(time.getTime()) + "px;min-width:80px;'>" + str + "</div>");
			time = new Date(time.getTime() + 86400000);
			// console.log(time.getTime(), stopTime);
		}
		$("#ctf_schedule .dragscroll .timeline").append(timeHeaders.join(""));
		$("#ctf_schedule .dragscroll .timeline").append("<div class='timeheader now' style='left:" + leftPos(now) + "px;'></div>");

		var lanes = splitOverlapping(bubbleUp(group(data, laneGrouper), []));
		console.log(lanes);
		lanes.filter(function(lane) {
			return lane.length > 0;
		}).map(function(lane) {
			var ctfs = [];
			lane.map(function(ctf) {
				ctfs.push(renderCTF(ctf));
			});
			$("#ctf_schedule .dragscroll").append("<div class='ctfline'>" + ctfs.join("") + "</div>");
		});
		$("#ctf_schedule .dragscroll")[0].scrollLeft = leftPos(now + 2*24*60*60*1000 - $("#ctf_schedule .dragscroll")[0].clientWidth / 2 / scale *60*1000);
	});
});