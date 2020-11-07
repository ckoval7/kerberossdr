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
    <div class="header">
        <a class="header_init" href="/init">Configuration and Spectrum</a> |
        <a class="header_sync" href="/sync">Sync</a> |
        <a class="header_doa" id="active" href="/doa">DOA Estimation</a> |
        <a class="header_pr" href="/pr">Passive Radar</a>
    </div>

    <div class="card">
        <div class="field">
            <p class="btn"><a href="http://{{ip_addr}}:8081/compass.html">Compass</a></p>
        </div>
    </div>

    <div class="card">
        <div class="field">
            <h2>Antenna Configuration</h2>
        </div>
        <form action="/doa" method="post">
            <input type="hidden" name="ant_config" value="ant_config" />

            <div class="field">
                <div class="field-label">
                    <label for="ant_arrangement">Arrangement:</label>
                </div>
                <div class="field-body">
                    <select id="ant_arrangement" onChange="check_uca();" name = "ant_arrangement">
                        <option value="0" {{!'selected="selected"' if ant_arrangement_index == 0 else ""}}>ULA</option>
                        <option value="1" {{!'selected="selected"' if ant_arrangement_index == 1 else ""}}>UCA</option>
                    </select>
                </div>
            </div>

            <div class="field">
                <div class="field-label">
                    <label for="ant_spacing">Spacing [meters]:</label>
                </div>
                <div class="field-body">
                    <input id="inputMeters" type="number" value="{{ant_meters}}" step="0.0001" name="ant_spacing" oninput="from_meters(this.value)"/>
                </div>
                <div class="field-label">
                    <label for="ant_spacing">Spacing [feet]:</label>
                </div>
                <div class="field-body">
                    <input id="inputFeet" type="number" step="0.0001" oninput="from_feet(this.value)" placeholder="Feet"/>
                </div>
                <div class="field-label">
                    <label for="ant_spacing">Spacing [inches]:</label>
                </div>
                <div class="field-body">
                    <input id="inputInches" type="number" step="0.0001" oninput="from_inches(this.value)" placeholder="Inches"/>
                </div>
            </div>

            <script type="text/javascript">
              function from_meters(valNum) {
                document.getElementById("inputFeet").value=(valNum*3.28084).toFixed(4);
                document.getElementById("inputInches").value=(valNum*39.3701).toFixed(4);
              }
              function from_feet(valNum) {
                document.getElementById("inputMeters").value=(valNum/3.2808).toFixed(4);
                document.getElementById("inputInches").value=(valNum*12).toFixed(4);
              }
              function from_inches(valNum) {
                document.getElementById("inputMeters").value=(valNum/39.3701).toFixed(4);
                document.getElementById("inputFeet").value=(valNum/12).toFixed(4);
              }
            </script>

            <div class="field">
                <div class="field-label">
                    <label for="en_doa">Enable DOA</label>
                </div>
                <div class="field-body">
                    <input type="checkbox" name="en_doa" value="on" {{!'checked="checked"' if en_doa >= 1 else ""}}>
                </div>
            </div>

            <div class="field">
                <div class="field-label">
                    <label for="doa_check">Algorithm</label>
                </div>
                <div class="field-body">
                    <input class="doa_check" type="checkbox" name="en_bartlett" value="on" {{!'checked="checked"' if en_bartlett >= 1 else ""}}>Bartlett<br>
                    <input class="doa_check" type="checkbox" name="en_capon" value="on" {{!'checked="checked"' if en_capon >= 1 else ""}}>Capon<br>
                    <input class="doa_check" type="checkbox" name="en_MEM" value="on" {{!'checked="checked"' if en_MEM >= 1 else ""}}>MEM<br>
                    <input class="doa_check" type="checkbox" name="en_MUSIC" value="on" {{!'checked="checked"' if en_MUSIC >= 1 else ""}}>MUSIC<br>
                </div>
            </div>


            <div class="field">
                <div class="field-label">
                    <label for="en_fbavg">FB Average (Do not use with UCA)</label>
                </div>
                <div class="field-body">
                    <input id="fb_avg" type="checkbox" name="en_fbavg" value="on" onChange="check_uca();" {{!'disabled' if ant_arrangement_index > 0 else ""}} {{!'checked="checked"' if en_fbavg >= 1 else ""}}>
                </div>
            </div>


            <div class="field">
                <input value="Update DOA" type="submit" class="btn" />
            </div>
        </form>
    </div>

    <iframe width=100% height=5% src="http://{{ip_addr}}:8080/stats"></iframe>
    <!--<script type="text/javascript" src="/static/refresh_image.js" charset="utf-8" style="float:right"></script>

    <body onload="JavaScript:init('/static/doa.jpg');">
    <canvas id="canvas"/>
    </body>-->

    <iframe width=100% height=100% src="http://{{ip_addr}}:8081/doa_graph.html"></iframe>
  </body>
</html>
