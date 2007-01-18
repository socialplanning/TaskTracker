/////////////////////////////////////////////////////////////////////////////////////
//
// DateBocks - Intuitive Date Input Selection
// http://datebocks.inimit.com
//
//
// Created by: 
//      Nathaniel Brown - http://nshb.net
//      Email: nshb(at)inimit.com
//
// Inspired by: 
//      Simon Willison - http://simon.incutio.com
//
// License:
//      GNU Lesser General Public License version 2.1 or above.
//      http://www.gnu.org/licenses/lgpl.html
//
// Bugs:
//      Please submit bug reports to http://dev.toolbocks.com
//
// Comments:
//      Any feedback or suggestions, please email nshb(at)inimit.com
//
// Donations:
//      If Datebocks has saved your life, or close to it, please send a donation
//      to donate(at)toolbocks.com
//
/////////////////////////////////////////////////////////////////////////////////////


////////////////////////////////////////////////////////////////////////////////
///// Dependencies

// add indexOf function to Array type
// finds the index of the first occurence of item in the array, or -1 if not found
Array.prototype.indexOf = function(item) {
    for (var i = 0; i < this.length; i++) {
        if (this[i] == item) {
            return i;
        }
    }
    return -1;
};

// add filter function to Array type
// returns an array of items judged true by the passed in test function
Array.prototype.filter = function(test) {
    var matches = [];
    for (var i = 0; i < this.length; i++) {
        if (test(this[i])) {
            matches[matches.length] = this[i];
        }
    }
    return matches;
};

// add right function to String type
// returns the rightmost x characters
String.prototype.right = function( intLength ) {
   if (intLength >= this.length)
      return this;
   else
      return this.substr( this.length - intLength, intLength );
};

// add trim function to String type
// trims leading and trailing whitespace
String.prototype.trim = function() { return this.replace(/^\s+|\s+$/, ''); };

var Class = {
  create: function() {
    return function() {
      this.initialize.apply(this, arguments);
    }
  }
}

Object.extend = function(destination, source) {
  for (var property in source) {
    destination[property] = source[property];
  }
  return destination;
}

////////////////////////////////////////////////////////////////////////////////
///// DateBocks

var DateBocks = Class.create();

DateBocks.VERSION = '3.0.0';

DateBocks.prototype = {

    /* Configuration Options ---------------------------------------------- */

    //  - iso
    //  - de
    //  - us
    //  - dd/mm/yyyy
    //  - dd-mm-yyyy
    //  - mm/dd/yyyy
    //  - mm.dd.yyyy
    //  - yyyy-mm-dd

    dateType                : 'iso',

    messageSpanSuffix       : 'Msg',

    messageSpanErrorClass   : 'error',

    messageSpanSuccessClass : '',
    
    dateBocksElementId      : '',

    autoRollOver            : true,

    calendarAlign           : 'Br',

    calendarIfFormat        : null, // set in constructor

    calendarFormatString    : null, // set in constructor
    

    /* Properties --------------------------------------------------------- */

    'monthNames': [
        'January',
        'February',
        'March',
        'April',
        'May',
        'June',
        'July',
        'August',
        'September',
        'October',
        'November',
        'December'
    ],

    'weekdayNames': [
        'Sunday',
        'Monday',
        'Tuesday',
        'Wednesday',
        'Thursday',
        'Friday',
        'Saturday'
    ],

    dateParsePatterns: [
        // Today
        {   re: /^tod|now/i,
            handler: function(db, bits) {
                return new Date();
            } 
        },
        // Tomorrow
        {   re: /^tom/i,
            handler: function(db, bits) {
                var d = new Date(); 
                d.setDate(d.getDate() + 1); 
                return d;
            }
        },
        // Yesterday
        {   re: /^yes/i,
            handler: function(db, bits) {
                var d = new Date();
                d.setDate(d.getDate() - 1);
                return d;
            }
        },
        // 4th
        {   re: /^(\d{1,2})(st|nd|rd|th)?$/i, 
            handler: function(db, bits) {
    
                var d = new Date();
                var yyyy = d.getFullYear();
                var dd = parseInt(bits[1], 10);
                var mm = d.getMonth();
    
                if ( db.dateInRange( yyyy, mm, dd ) )
                   return db.getDateObj(yyyy, mm, dd);
    
            }
        },
        // 4th Jan
        {   re: /^(\d{1,2})(?:st|nd|rd|th)? (?:of\s)?(\w+)$/i, 
            handler: function(db, bits) {
    
                var d = new Date();
                var yyyy = d.getFullYear();
                var dd = parseInt(bits[1], 10);
                var mm = db.parseMonth(bits[2]);
    
                if ( db.dateInRange( yyyy, mm, dd ) )
                   return db.getDateObj(yyyy, mm, dd);
    
            }
        },
        // 4th Jan 2003
        {   re: /^(\d{1,2})(?:st|nd|rd|th)? (?:of )?(\w+),? (\d{4})$/i,
            handler: function(db, bits) {
                var d = new Date();
                d.setDate(parseInt(bits[1], 10));
                d.setMonth(db.parseMonth(bits[2]));
                d.setYear(bits[3]);
                return d;
            }
        },
        // Jan 4th
        {   re: /^(\w+) (\d{1,2})(?:st|nd|rd|th)?$/i, 
            handler: function(db, bits) {
    
                var d = new Date();
                var yyyy = d.getFullYear(); 
                var dd = parseInt(bits[2], 10);
                var mm = db.parseMonth(bits[1]);
    
                if ( db.dateInRange( yyyy, mm, dd ) )
                   return db.getDateObj(yyyy, mm, dd);
    
            }
        },
        // Jan 4th 2003
        {   re: /^(\w+) (\d{1,2})(?:st|nd|rd|th)?,? (\d{4})$/i,
            handler: function(db, bits) {
    
                var yyyy = parseInt(bits[3], 10); 
                var dd = parseInt(bits[2], 10);
                var mm = db.parseMonth(bits[1]);
    
                if ( db.dateInRange( yyyy, mm, dd ) )
                   return db.getDateObj(yyyy, mm, dd);
    
            }
        },
        // Next Week, Last Week, Next Month, Last Month, Next Year, Last Year
        {   re: /((next|last)\s(week|month|year))/i,
            handler: function(db, bits) {
                var objDate = new Date();
                
                var dd = objDate.getDate();
                var mm = objDate.getMonth();
                var yyyy = objDate.getFullYear();
                
                switch (bits[3]) {
                  case 'week':
                    var newDay = (bits[2] == 'next') ? (dd + 7) : (dd - 7);
                    
                    objDate.setDate(newDay);
                    
                    break;
                  case 'month':
                    var newMonth = (bits[2] == 'next') ? (mm + 1) : (mm - 1);
                    
                    objDate.setMonth(newMonth);
                    
                    break;
                  case 'year':
                    var newYear = (bits[2] == 'next') ? (yyyy + 1) : (yyyy - 1);
                    
                    objDate.setYear(newYear);
                    
                    break;
                }
                
                return objDate;
            }
        },
        // next tuesday
        // this mon, tue, wed, thu, fri, sat, sun
        // mon, tue, wed, thu, fri, sat, sun
        {   re: /^(next|this)?\s?(\w+)$/i,
            handler: function(db, bits) {
    
                var d = new Date();
                var day = d.getDay();
                var newDay = db.parseWeekday(bits[2]);
                var addDays = newDay - day;
                if (newDay <= day) {
                    addDays += 7;
                }
                d.setDate(d.getDate() + addDays);
                return d;
    
            }
        },
        // last Tuesday
        {   re: /^last (\w+)$/i,
            handler: function(db, bits) {
    
                var d = new Date();
                var wd = d.getDay();
                var nwd = db.parseWeekday(bits[1]);
    
                // determine the number of days to subtract to get last weekday
                var addDays = (-1 * (wd + 7 - nwd)) % 7;
    
                // above calculate 0 if weekdays are the same so we have to change this to 7
                if (0 == addDays)
                   addDays = -7;
                
                // adjust date and return
                d.setDate(d.getDate() + addDays);
                return d;
    
            }
        },
        // mm/dd/yyyy (American style)
        {   re: /(\d{1,2})\/(\d{1,2})\/(\d{4})/,
            handler: function(db, bits) {
                // if config date type is set to another format, use that instead
                if (db.dateType == 'dd/mm/yyyy') {
                  var yyyy = parseInt(bits[3], 10);
                  var dd = parseInt(bits[1], 10);
                  var mm = parseInt(bits[2], 10) - 1;
                } else {
                  var yyyy = parseInt(bits[3], 10);
                  var dd = parseInt(bits[2], 10);
                  var mm = parseInt(bits[1], 10) - 1;
                }
    
                if ( db.dateInRange( yyyy, mm, dd ) )
                   return db.getDateObj(yyyy, mm, dd);
    
            }
        },
        // mm/dd/yy (American style) short year
        {   re: /(\d{1,2})\/(\d{1,2})\/(\d{1,2})/,
            handler: function(db, bits) {
    
                var d = new Date();
                var yyyy = d.getFullYear() - (d.getFullYear() % 100) + parseInt(bits[3], 10);
                var dd = parseInt(bits[2], 10);
                var mm = parseInt(bits[1], 10) - 1;
    
                if ( db.dateInRange(yyyy, mm, dd) )
                   return db.getDateObj(yyyy, mm, dd);
    
            }
        },
        // mm/dd (American style) omitted year
        {   re: /(\d{1,2})\/(\d{1,2})/,
            handler: function(db, bits) {
    
                var d = new Date();
                var yyyy = d.getFullYear();
                var dd = parseInt(bits[2], 10);
                var mm = parseInt(bits[1], 10) - 1;
    
                if ( db.dateInRange(yyyy, mm, dd) )
                   return db.getDateObj(yyyy, mm, dd);
    
            }
        },
        // mm-dd-yyyy
        {   re: /(\d{1,2})-(\d{1,2})-(\d{4})/,
            handler: function(db, bits) {
                if (db.dateType == 'dd-mm-yyyy') {
                  // if the config is set to use a different schema, then use that instead
                  var yyyy = parseInt(bits[3], 10);
                  var dd = parseInt(bits[1], 10);
                  var mm = parseInt(bits[2], 10) - 1;
                } else {
                  var yyyy = parseInt(bits[3], 10);
                  var dd = parseInt(bits[2], 10);
                  var mm = parseInt(bits[1], 10) - 1;
                }
    
                if ( db.dateInRange( yyyy, mm, dd ) ) {
                   return db.getDateObj(yyyy, mm, dd);
                }
    
            }
        },
        // dd.mm.yyyy
        {   re: /(\d{1,2})\.(\d{1,2})\.(\d{4})/,
            handler: function(db, bits) {
                var dd = parseInt(bits[1], 10);
                var mm = parseInt(bits[2], 10) - 1;
                var yyyy = parseInt(bits[3], 10);
    
                if ( db.dateInRange( yyyy, mm, dd ) )
                   return db.getDateObj(yyyy, mm, dd);
    
            }
        },
        // yyyy-mm-dd (ISO style)
        {   re: /(\d{4})-(\d{1,2})-(\d{1,2})/,
            handler: function(db, bits) {
    
                var yyyy = parseInt(bits[1], 10);
                var dd = parseInt(bits[3], 10);
                var mm = parseInt(bits[2], 10) - 1;
    
                if ( db.dateInRange( yyyy, mm, dd ) )
                   return db.getDateObj(yyyy, mm, dd);
    
            }
        },
        // yy-mm-dd (ISO style) short year
        {   re: /(\d{1,2})-(\d{1,2})-(\d{1,2})/,
            handler: function(db, bits) {
    
                var d = new Date();
                var yyyy = d.getFullYear() - (d.getFullYear() % 100) + parseInt(bits[1], 10);
                var dd = parseInt(bits[3], 10);
                var mm = parseInt(bits[2], 10) - 1;
    
                if ( db.dateInRange( yyyy, mm, dd ) )
                   return db.getDateObj(yyyy, mm, dd);
    
            }
        },
        // mm-dd (ISO style) omitted year
        {   re: /(\d{1,2})-(\d{1,2})/,
            handler: function(db, bits) {
    
                var d = new Date();
                var yyyy = d.getFullYear();
                var dd = parseInt(bits[2], 10);
                var mm = parseInt(bits[1], 10) - 1;
    
                if ( db.dateInRange( yyyy, mm, dd ) )
                   return db.getDateObj(yyyy, mm, dd);
    
            }
        }
    ],

    /* Methods ------------------------------------------------------------ */

    /* constructor */
    initialize: function(options) {
        Object.extend(this, options);
        
        switch (this.dateType) {
          case 'mm/dd/yyyy':
          case 'us':
              this.calendarIfFormat = '%m/%d/%Y';
              this.calendarFormatString = 'mm/dd/yyyy';
              break;
          case 'mm.dd.yyyy':
          case 'de':
              this.calendarIfFormat = '%m.%d.%Y';
              this.calendarFormatString = 'mm.dd.yyyy';
              break;
          case 'dd/mm/yyyy':
              this.calendarIfFormat = '%d/%m/%Y';
              this.calendarFormatString = 'dd/mm/yyyy';
              break;
          case 'dd-mm-yyyy':
              this.calendarIfFormat = '%d-%m-%Y';
              this.calendarFormatString = 'dd-mm-yyyy';
              break;
          case 'yyyy-mm-dd':
          case 'iso':
          case 'default':
          default:	      
              this.calendarIfFormat = '%Y-%m-%d';
              this.calendarFormatString = 'yyyy-mm-dd';
              break;
        }
    },

    /* Takes a string, returns the index of the month matching that string,
       throws an error if 0 or more than 1 matches
    */
    parseMonth: function(month) {
        var matches = this.monthNames.filter(function(item) { 
            return new RegExp("^" + month, "i").test(item);
        });
        if (matches.length == 0) {
            throw new Error("Invalid month string");
        }
        if (matches.length < 1) {
            throw new Error("Ambiguous month");
        }
        return this.monthNames.indexOf(matches[0]);
    },

    /* Same as parseMonth but for days of the week */
    parseWeekday: function(weekday) {
        var matches = this.weekdayNames.filter(function(item) {
            return new RegExp("^" + weekday, "i").test(item);
        });
        if (matches.length == 0) {
            throw new Error("Invalid day string");
        }
        if (matches.length < 1) {
            throw new Error("Ambiguous weekday");
        }
        return this.weekdayNames.indexOf(matches[0]);
    },

    /* Given a year, month, and day, perform sanity checks to make
       sure the date is sane.
    */
    dateInRange: function(yyyy, mm, dd) {

        // if month out of range
        if ( mm < 0 || mm > 11 )
            throw new Error('Invalid month value.  Valid months values are 1 to 12');

        if (!this.autoRollOver) {
            // get last day in month
            var d = (11 == mm)
                ? new Date(yyyy + 1, 0, 0)
                : new Date(yyyy, mm + 1, 0);

            // if date out of range
            if ( dd < 1 || dd > d.getDate() ) {
                throw new Error('Invalid date value.  Valid date values for '
                    + this.monthNames[mm]
                    + ' are 1 to '
                    + d.getDate().toString()
                );
            }
        }

        return true;
    },
    
    /* Get Date Object */
    
    getDateObj: function(yyyy, mm, dd) {
      var obj = new Date();
  
      obj.setDate(1);
      obj.setYear(yyyy);
      obj.setMonth(mm);
      obj.setDate(dd);
      
      return obj;
    },

    /* Take a string and run it through the dateParsePatterns.
       The first one that succeeds will return a Date object. */
    parseDateString: function(s) {
        var dateParsePatterns = this.dateParsePatterns;
        for (var i = 0; i < dateParsePatterns.length; i++) {
            var re      = dateParsePatterns[i].re;
            var handler = dateParsePatterns[i].handler;
            var bits    = re.exec(s);
            if (bits) {
                return handler(this, bits);
            }
        }
        throw new Error("Invalid date string");
    },

    /* Put an extra 0 in front of single digit integers. */
    zeroPad: function(integer) {
        if (integer < 10) {
            return '0' + integer;
        } else {
            return integer;
        }
    },

    /* Try to make sense of the date in id.value . */
    magicDate: function() {
	var input = document.getElementById(this.dateBocksElementId);
        var messageSpan = document.getElementById(input.id + this.messageSpanSuffix);

        try {
	    var num = input.id.replace('deadline_', '');
	    if (!input.value) {
		console.log("OO");
		if (num != input.id) {
		    return changeField(num, 'deadline');
		}	
	    }
            var d = this.parseDateString(input.value);

            var day = this.zeroPad(d.getDate());
            var month = this.zeroPad(d.getMonth() + 1);
            var year = d.getFullYear();

            switch (this.dateType) {
                case 'dd/mm/yyyy':
                    input.value = day + '/' + month + '/' + year;
                    break;
                case 'dd-mm-yyyy':
                    input.value = day + '-' + month + '-' + year;
                    break;
                case 'mm/dd/yyyy':
                case 'us':
                    input.value = month + '/' + day + '/' + year;
                    break;
                case 'mm.dd.yyyy':
                case 'de':
                    input.value = month + '.' + day + '.' + year;
                    break;
                case 'default':
                case 'iso':
                case 'yyyy-mm-dd':
                default:
		    input.value = year + '-' + month + '-' + day;
                    break;
            }

            input.className = '';
		
            // Human readable date
            if (messageSpan) {
                messageSpan.innerHTML = d.toDateString();
                messageSpan.className = this.messageSpanSuccessClass;
            }
	    if (num != input.id) {
		changeField(num, 'deadline');
	    }    
        }
        catch (e) {
            if (messageSpan) {
                var message = e.message;
                // Fix for IE6 bug
                if (message.indexOf('is null or not an object') > -1) {
                    message = 'Invalid date string';
                }
                messageSpan.innerHTML = message;
                messageSpan.className = this.messageSpanErrorClass;
            }
	    
        }
    },
    
    trim: function(string) { 
      return string.replace(/^\s+|\s+$/, ''); 
    },
    
    /* Key listener to catch the enter and return event */
    keyObserver: function(event, action) {
      var keyCode = event.keyCode ? event.keyCode : ((event.which) ? event.which : event.charCode);
      
    	if (keyCode == 13 || keyCode == 10) {
    		switch(action) {
    		  case 'parse':
    		    this.magicDate();
    		    break;
    		  case 'return':
    		  case 'false':
    		  default:
    		    return false;
    		    break;
    		}
      }
    },
    
    setDefaultFormatMessage: function() {
      document.getElementById(this.dateBocksElementId + 'Msg').innerHTML = this.calendarFormatString;
    }
};