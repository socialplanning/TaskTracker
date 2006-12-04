function utc(d) {
    return Date.UTC(d.getFullYear(), d.getMonth(), d.getDate());
}

function date_diff(date1, date2) {
    var date1_UTC = utc(date1);
    var date2_UTC = utc(date2);
    return (date1_UTC - date2_UTC) / 86400000;
}

function dayOfWeek(day) {
    return "SunMonTueWedThuFriSatSun".substr(day * 3, 3);
}

function monthName(month) {
    var months = ["January", "February", "March", "April", "May", "June", "July", "August", "September", "October", "November", "December"];
    return months[month];
}


function pretty_date_engine(now, date) {
    var diff = date_diff(date, now);
    if (diff == -1) {
	return "Yesterday";
    }
    if (diff == 0) {
	return "Today";
    }
    if (diff == 1) {
	return "Tomorrow";
    }
    if (diff < 7) {
	return dayOfWeek(date.getDay());
    }
    if (diff < 90 && date.getYear() == now.getYear()) {
	return monthName(date.getMonth()) + " " + date.getDate()
    }
    return monthName(date.getMonth()) + " " + date.getDate() + ", " + date.getFullYear();
}

function pretty_date(date) {
    var now = new Date();
    return pretty_date_engine(now, date);
}


function test_pretty_date() {
    var now = new Date(2006, 0, 1);
    var dates = {
	'Today' : new Date(2006, 0, 1),
	'Tomorrow' : new Date(2006, 0, 2),
	'Yesterday' : new Date(2005, 11, 31),
	'Tue' : new Date(2006, 0, 3),
	'Sat' : new Date(2006, 0, 7),
	'January 8' : new Date(2006, 0, 8),
	'December 8, 2006' : new Date(2006, 11, 8),
	'January 8, 2007' : new Date(2007, 0, 8)
    };

    for (date in dates) {
	var pd = pretty_date_engine(now, dates[date]);
	if (pd != date) {
	    alert("failure mapping " + dates[date] + " to " + date + ", got " + pd);
	    break;
	}
    }
}
