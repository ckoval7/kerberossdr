<html>
<meta content="width=device-width, initial-scale=1" name="viewport" />
<meta http-equiv="Cache-control" content="no-cache" charset="utf-8">
<link rel="stylesheet" type="text/css" href="static/style.css">
<p class="header"><a class="header_init" href="/init">Configuration and Spectrum</a> | <a class="header_sync" href="/sync">Sync</a> |
  <a class="header_doa" href="/doa">DOA Estimation</a> | <a class="header_pr" href="/pr">Passive Radar</a>
</p>
<hr>
<h2>Passive Radar</h2>
<form action="/pr" method="post">

	<p><b>Channel Configuration</b></p>

	<input type="checkbox" name="en_pr" value="on" {{!'checked="checked"' if en_pr >= 1 else ""}}>Enable Passive Radar Processing<br>
	<p>Reference Channel [0-3]: <input type="number" value="{{ref_ch}}" step="1" name="ref_ch"/></p>
	<p>Suveillance Channel [0-3]: <input type="number" value="{{surv_ch}}" step="1" name="surv_ch"/></p>

	<p><b>Time domain clutter cancellation</b></p>

	<input type="checkbox" name="en_clutter" value="on" {{!'checked="checked"' if en_clutter >= 1 else ""}}>Enable/Disable<br>
	<p>Filter Dimension: <input type="number" value="{{filt_dim}}" step="1" name="filt_dim"/></p>

	<b>Cross-Correlation Detector</b>
	<p>Max Range  (Must be power of 2): <input type="number" value="{{max_range}}" step="1" name="max_range"/></p>
	<p>Max Doppler: <input type="number" value="{{max_doppler}}" step="1" name="max_doppler"/></p>

        <p>Windowing:
        <select name = "windowing_mode">
                <option value="0" {{!'selected="selected"' if windowing_mode == 0 else ""}}>Rectangular</option>
                <option value="1" {{!'selected="selected"' if windowing_mode == 1 else ""}}>Hamming</option>
        </select></p>

	<p>Dynamic Range <input type="number" value="{{dyn_range}}" step="1" name="dyn_range"/></p>

	<p><b>Automatic Detection (CA-CFAR)</b></p>
	<input type="checkbox" name="en_det" value="on" {{!'checked="checked"' if en_det >= 1 else ""}}>Enable/Disable<br>

	<p>Estimation Window <input type="number" value="{{est_win}}" step="1" name="est_win"/></p>
	<p>Guard Window <input type="number" value="{{guard_win}}" step="1" name="guard_win"/></p>
	<p>Threshold [dB] <input type="number" value="{{thresh_det}}" step="0.01" name="thresh_det"/></p>


	<p><input value="Update Paramaters" type="submit" /></p>
</form>
<iframe width=100% height=5% src="http://{{ip_addr}}:8080/stats"></iframe>
<hr>
<!--<script type="text/javascript" src="/static/refresh_image.js" charset="utf-8" style="float:right"></script>
<body onload="JavaScript:init('/static/pr.jpg');">
<canvas id="canvas"/>
</body>-->

<iframe width=100% height=100% src="http://{{ip_addr}}:8081/passive_radar.html"></iframe>


</html>
