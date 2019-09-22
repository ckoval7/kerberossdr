// Const values. Adjust these for intermittant signals. E.g. Update compass ONLY when received power
// is above a certain value
const MIN_PWR = 0;
const MIN_CONF = 0;

// Global variable
var     img = null,
	needle = null,
	ctx = null,
        str = "",
	DOA_deg = 0;
        PWR_val = 0;
        CONF_val = 0;
        first_entry = 1;
function clearCanvas() {
	 // clear canvas
	ctx.clearRect(0, 0, 800, 800);
}

function parseXml(xmlStr) {
   return new window.DOMParser().parseFromString(xmlStr, "text/xml");
}


function draw() {

        // 1. create a new XMLHttpRequest object -- an object like any other!
        var myRequest = new XMLHttpRequest();
        // 2. open the request and pass the HTTP method name and the resource as parameters
        myRequest.open('GET', 'DOA_value.html');
        myRequest.send();
        // 3. write a function that runs anytime the state of the AJAX request changes
        myRequest.onreadystatechange = function () {
        // 4. check if the request has a readyState of 4, which indicates the server has responded (complete)
        if (myRequest.readyState === 4) {
            // 5. insert the text sent by the server into the HTML of the 'ajax-content'
            //alert("KESZ");
            var response = myRequest.responseText; // Has the form of <DOA>..</DOA>
            response = "<DATA>" + response + "</DATA>";
            var xml = parseXml(response);
            DOA_deg = 360 - Number(xml.getElementsByTagName("DOA")[0].childNodes[0].nodeValue);
            PWR_val = Math.max(Number(xml.getElementsByTagName("PWR")[0].childNodes[0].nodeValue), 0);
            CONF_val = Math.max(Number(xml.getElementsByTagName("CONF")[0].childNodes[0].nodeValue), 0);
            //DOA_deg  =  Number(response.replace( /\D+/g, ''));
            //Number(response.slice(5,str.lastIndexOf(response)-5));
            //var res = str.slice(5, 8);
            //console.log(response);
            //console.log(response.slice(5,str.lastIndexOf(response)-5));
            console.log(DOA_deg);

        }

        if ((PWR_val >= MIN_PWR && CONF_val >= MIN_CONF) || first_entry == 1) {

                first_entry = 0;

		clearCanvas();

		// Draw the compass onto the canvas
		ctx.drawImage(img, 0, 0);

		// Save the current drawing state
		ctx.save();

		// Now move across and down half the
		ctx.translate(400, 400);  // Set to canvas size/2

	        //degrees=45
		// Rotate around this point
		ctx.rotate(DOA_deg * (Math.PI / 180));

		// Draw the image back and up
		ctx.drawImage(needle, -45, -400); // Set to arrow size/2


	        //ctx.fillRect(-20, -50, 20, 100);

		// Restore the previous drawing state
		ctx.restore();
        }
		// Increment the angle of the needle by 5 degrees

	var DOA_message = "Estimated DOA: ";
	DOA_message = DOA_message.concat(DOA_deg," deg");
	document.getElementById("doa").innerHTML = DOA_message;

	var PWR_message = "Signal Power: ";
	PWR_message = PWR_message.concat(PWR_val, " dB");
	document.getElementById("pwr").innerHTML = PWR_message;

	var CONF_message = "DOA Confidence: ";
	CONF_message = CONF_message.concat(CONF_val);
	document.getElementById("conf").innerHTML = CONF_message;

        //alert("ALERT");


};

}

function imgLoaded() {
	// Image loaded event complete.  Start the timer
	setInterval(draw, 100);
}

function init() {
	// Grab the compass element
	var canvas = document.getElementById('compass');

	// Canvas supported?
	if (canvas.getContext('2d')) {
		ctx = canvas.getContext('2d');

		// Load the needle image
		needle = new Image();
		needle.src = 'arrow.png';

		// Load the compass image
		img = new Image();
		img.src = 'hydra_compass.png';
		img.onload = imgLoaded;
	} else {
		alert("Canvas not supported!");
	}
}
