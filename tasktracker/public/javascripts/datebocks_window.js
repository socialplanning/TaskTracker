DateBocks.windowProperties = function(params) {
  var oRegex = new RegExp('');
  oRegex.compile( "(?:^|,)([^=]+)=(\\d+|yes|no|auto)", 'gim' );
  
  var oProperties = new Object();
  var oPropertiesMatch;
  
  while( ( oPropertiesMatch = oRegex.exec( params ) ) != null )  {
    var sValue = oPropertiesMatch[2];
  
    if ( sValue == ( 'yes' || '1' ) ) {
    	oProperties[ oPropertiesMatch[1] ] = true;
    } else if ( (! isNaN( sValue ) && sValue != 0) || ('auto' == sValue ) ) {
    	oProperties[ oPropertiesMatch[1] ] = sValue;
    }
	}
	
	return oProperties;
};
  
DateBocks.windowOpenCenter = function(url, name, properties){
  try {
    var oProperties = DateBocks.windowProperties(properties);
    
    //if( !oProperties['autocenter'] || oProperties['fullscreen'] ) {
    //  return window.open(window_url, window_name, window_properties);
    //}
    
    w = parseInt(oProperties['width']);
    h = parseInt(oProperties['height']);
    w = w > 0 ? w : 640;
    h = h > 0 ? h : 480;
    
    if (screen) {
      t = (screen.height - h) / 2;
      l = (screen.width - w) / 2;
    } else {
      t = 250;
      l = 250;
    }
    
    properties = (w>0?",width="+w:"") + (h>0?",height="+h:"") + (t>0?",top="+t:"") + (l>0?",left="+l:"") + "," + properties.replace(/,(width=\s*\d+\s*|height=\s*\d+\s*|top=\s*\d+\s*||left=\s*\d+\s*)/gi, "");
    return window.open(url, name, properties);
  } catch( e ) {};
};