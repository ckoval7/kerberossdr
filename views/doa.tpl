<html>
  <head>
    <meta content="width=device-width, initial-scale=1" name="viewport" />
    <meta http-equiv="Cache-control" content="no-cache" charset="utf-8">
    <link rel="stylesheet" type="text/css" href="static/style.css">
    <script>
      function check_uca() {
        sel = document.getElementById("ant_arrangement")
        var x = sel.options[sel.selectedIndex].text;
        if (x == "UCA"){
          document.getElementById("fb_avg").disabled=true;
          document.getElementById("fb_avg").checked = false;
        }
        else {
          document.getElementById("fb_avg").removeAttribute("disabled");
        }
      }
    </script>
  </head>
  <body>
    <p class="header"><a class="header_init" href="/init">Configuration and Spectrum</a> | <a class="header_sync" href="/sync">Sync</a> |
      <a class="header_doa" href="/doa">DOA Estimation</a> | <a class="header_pr" href="/pr">Passive Radar</a>
    </p>
    <hr>

    <p><a href="http://{{ip_addr}}:8081/compass.html">Compass</a></p>
    <hr>

    <h2>Antenna Configuration</h2>
    <form action="/doa" method="post">
            <input type="hidden" name="ant_config" value="ant_config" />

    	<p>Arrangement:
    	<select id="ant_arrangement" onChange="check_uca();" name = "ant_arrangement">
    		<option value="0" {{!'selected="selected"' if ant_arrangement_index == 0 else ""}}>ULA</option>
    		<option value="1" {{!'selected="selected"' if ant_arrangement_index == 1 else ""}}>UCA</option>
    	</select></p>

    	<!-- <p>Spacing [lambda]: <input type="number" value="{ {ant_spacing} }" step="0.0001" name="ant_spacing"/></p> -->
      <p>Spacing [meters]: <input type="number" value="{{ant_meters}}" step="0.0001" name="ant_spacing"/></p>

      <div id="checkox_wrapper">
      <div id="doa_checkboxes">
      	<input type="checkbox" name="en_doa" value="on" {{!'checked="checked"' if en_doa >= 1 else ""}}>Enable DOA<br>
        <p style="text-align: left; margin-bottom: 5px;">Algorithm:</p>
      	<input class="doa_check" type="checkbox" name="en_bartlett" value="on" {{!'checked="checked"' if en_bartlett >= 1 else ""}}>Bartlett<br>
      	<input class="doa_check" type="checkbox" name="en_capon" value="on" {{!'checked="checked"' if en_capon >= 1 else ""}}>Capon<br>
      	<input class="doa_check" type="checkbox" name="en_MEM" value="on" {{!'checked="checked"' if en_MEM >= 1 else ""}}>MEM<br>
      	<input class="doa_check" type="checkbox" name="en_MUSIC" value="on" {{!'checked="checked"' if en_MUSIC >= 1 else ""}}>MUSIC<br>
      </div>
      </div>
    	<br>

    	<input id="fb_avg" type="checkbox" name="en_fbavg" value="on" onChange="check_uca();" {{!'disabled' if ant_arrangement_index > 0 else ""}} {{!'checked="checked"' if en_fbavg >= 1 else ""}}>FB Average (Do not use with UCA)<br>

    	<p><input value="Update DOA" type="submit" /></p>
    </form>
    <hr>
    <iframe width=100% height=5% src="http://{{ip_addr}}:8080/stats"></iframe>
    <!--<script type="text/javascript" src="/static/refresh_image.js" charset="utf-8" style="float:right"></script>

    <body onload="JavaScript:init('/static/doa.jpg');">
    <canvas id="canvas"/>
    </body>-->

    <iframe width=100% height=100% src="http://{{ip_addr}}:8081/doa_graph.html"></iframe>
  </body>
</html>
