// Const values. Adjust these for intermittant signals. E.g. Update compass ONLY when received power
// is above a certain value
    var MIN_PWR = 0;
    var MIN_CONF = 0;

// Global variables
    var img = null;
    var needle = null;
    var ctx = null;
    var str = "";
    var DOA_deg = 0;
    var PWR_val = 0;
    var CONF_val = 0;
    var first_entry = 1;

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

            // Restore the previous drawing state
            ctx.restore();
        }
        // Increment the angle of the needle by 5 degrees

        var DOA_message = "Estimated DOA: ";
        DOA_message = DOA_message.concat(DOA_deg," deg");
        document.getElementById("doa").innerHTML = DOA_message;

        var PWR_message = "Signal Power: ";
        PWR_message = PWR_message.concat(Math.round(PWR_val * 100)/100, " dB");
        document.getElementById("pwr").innerHTML = PWR_message;

        var CONF_message = "DOA Confidence: ";
        CONF_message = CONF_message.concat(CONF_val);
        document.getElementById("conf").innerHTML = CONF_message;
    };

}

function imgLoaded() {
    // Image loaded event complete.  Start the timer
    setInterval(draw, 100);
}

function getSize() {
    // Body has 8px of padding on each side
    var width = window.innerWidth - 16;
    var height = window.innerHeight - 16;
    
    // Canvas width & height = 100%
    // Max-width & max-height = 800px
    var size = Math.min(width, height, 800);
    
    return size;
}

function setCookie() {
    var d = new Date();
    d.setTime(d.getTime() + (10*365*24*60*60*1000)); // ten years from now
    var expires = "expires=" + d.toGMTString();
    
    MIN_PWR = document.getElementById('MIN_PWR').value;
    MIN_CONF = document.getElementById('MIN_CONF').value;
    
    document.cookie = 'MIN_PWR' + "=" + MIN_PWR + ";" + expires + ";path=/";
    document.cookie = 'MIN_CONF' + "=" + MIN_CONF + ";" + expires + ";path=/";
}

function getCookie(cname) {
    var name = cname + "=";
    var decodedCookie = decodeURIComponent(document.cookie);
    var ca = decodedCookie.split(';');
    for(var i = 0; i < ca.length; i++) {
        var c = ca[i];
        while (c.charAt(0) == ' ') {
            c = c.substring(1);
        }
        if (c.indexOf(name) == 0) {
            return c.substring(name.length, c.length);
        }
    }
    return "";
}

function checkCookie() {
    MIN_PWR = getCookie("MIN_PWR");
    MIN_CONF = getCookie("MIN_CONF");
    if (MIN_PWR == "") {
        MIN_PWR = 0;
    }
    if (MIN_CONF == "") {
        MIN_CONF = 0;
    }
    document.getElementById("MIN_PWR").value = MIN_PWR;
    document.getElementById("MIN_CONF").value = MIN_CONF;
}

function init() {
    // Grab the compass element
    var canvas = document.getElementById('compass');
    var size = getSize();
    var scale = size/800;
    
    // Set the min power and confidence
    checkCookie();

    canvas.width = size;
    canvas.height = size;
    

    // Is Canvas supported?
    if (canvas.getContext('2d')) {
        ctx = canvas.getContext('2d');
        ctx.scale(scale, scale, scale);

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
