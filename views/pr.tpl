<html>
<head>
    <meta content="width=device-width, initial-scale=1" name="viewport" />
    <meta http-equiv="Cache-control" content="no-cache" charset="utf-8">
    <link rel="stylesheet" type="text/css" href="static/style.css">
</head>
<body>

    <div class="header">
        <a class="header_init" href="/init">Configuration and Spectrum</a> | 
        <a class="header_sync" href="/sync">Sync</a> | 
        <a class="header_doa" href="/doa">DOA Estimation</a> | 
        <a class="header_pr" id="active" href="/pr">Passive Radar</a>
    </div>

    <div class="card">

        <form action="/pr" method="post">
        
            <div class="field">
                <h2>Channel Configuration</h2>
            </div>
        
            <div class="field">
                <div class="field-label">
                    <label for="en_pr">Enable Passive Radar Processing</label>
                </div>
                <div class="field-body">
                    <input type="checkbox" name="en_pr" value="on" {{!'checked="checked"' if en_pr >= 1 else ""}}>
                </div>
            </div>
            
            <div class="field">
                <div class="field-label">
                    <label for="ref_ch">Reference Channel [0-3]:</label>
                </div>
                <div class="field-body">
                    <input type="number" value="{{ref_ch}}" step="1" name="ref_ch"/>
                </div>
            </div>
            
            <div class="field">
                <div class="field-label">
                    <label for="surv_ch">Suveillance Channel [0-3]:</label>
                </div>
                <div class="field-body">
                    <input type="number" value="{{surv_ch}}" step="1" name="surv_ch"/>
                </div>
            </div>
            
            
            <div class="field">
                <h2>Time domain clutter cancellation</h2>
            </div>
            
            <div class="field">
                <div class="field-label">
                    <label for="en_clutter">Enable/Disable</label>
                </div>
                <div class="field-body">
                    <input type="checkbox" name="en_clutter" value="on" {{!'checked="checked"' if en_clutter >= 1 else ""}}>
                </div>
            </div>
            
            <div class="field">
                <div class="field-label">
                    <label for="filt_dim">Filter Dimension:</label>
                </div>
                <div class="field-body">
                    <input type="number" value="{{filt_dim}}" step="1" name="filt_dim"/>
                </div>
            </div>



            <div class="field">
                <h2>Cross-Correlation Detector</h2>
            </div>
            
            <div class="field">
                <div class="field-label">
                    <label for="max_range">Max Range  (Must be power of 2):</label>
                </div>
                <div class="field-body">
                    <input type="number" value="{{max_range}}" step="1" name="max_range"/>
                </div>
            </div>
            
            <div class="field">
                <div class="field-label">
                    <label for="max_doppler">Max Doppler:</label>
                </div>
                <div class="field-body">
                    <input type="number" value="{{max_doppler}}" step="1" name="max_doppler"/>
                </div>
            </div>
            
            
            <div class="field">
                <div class="field-label">
                    <label for="windowing_mode">Windowing:</label>
                </div>
                <div class="field-body">
                    <select name="windowing_mode">
                        <option value="0" {{!'selected="selected"' if windowing_mode == 0 else ""}}>Rectangular</option>
                        <option value="1" {{!'selected="selected"' if windowing_mode == 1 else ""}}>Hamming</option>
                </select>
                </div>
            </div>
            
            <div class="field">
                <div class="field-label">
                    <label for="dyn_range">Dynamic Range</label>
                </div>
                <div class="field-body">
                    <input type="number" value="{{dyn_range}}" step="1" name="dyn_range"/>
                </div>
            </div>

            <div class="field">
                <h2>Automatic Detection (CA-CFAR)</h2>
            </div>
                

            <div class="field">
                <div class="field-label">
                    <label for="en_det">Enable/Disable</label>
                </div>
                <div class="field-body">
                    <input type="checkbox" name="en_det" value="on" {{!'checked="checked"' if en_det >= 1 else ""}}>
                </div>
            </div>
            
            <div class="field">
                <div class="field-label">
                    <label for="est_win">Estimation Window</label>
                </div>
                <div class="field-body">
                    <input type="number" value="{{est_win}}" step="1" name="est_win"/>
                </div>
            </div>
            
            <div class="field">
                <div class="field-label">
                    <label for="guard_win">Guard Window</label>
                </div>
                <div class="field-body">
                    <input type="number" value="{{guard_win}}" step="1" name="guard_win"/>
                </div>
            </div>
            
            <div class="field">
                <div class="field-label">
                    <label for="thresh_det">Threshold [dB]</label>
                </div>
                <div class="field-body">
                    <input type="number" value="{{thresh_det}}" step="0.01" name="thresh_det"/>
                </div>
            </div>

	    <div class="field">
                <h2>Other Settings</h2>
            </div>


	   <div class="field">
                <div class="field-label">
                    <label for="en_peakhold">Enable Peak Hold</label>
                </div>
                <div class="field-body">
                    <input type="checkbox" name="en_peakhold" value="on" {{!'checked="checked"' if en_peakhold >= 1 else ""}}>
                </div>
            </div>

            
            <div class="field">
                <input value="Update Paramaters" type="submit" class="btn"/>
            </div>
            
        </form>
    </div>
    <iframe width=100% height=5% src="http://{{ip_addr}}:8080/stats"></iframe>
    <hr>
    <!--<script type="text/javascript" src="/static/refresh_image.js" charset="utf-8" style="float:right"></script>
    <body onload="JavaScript:init('/static/pr.jpg');">
    <canvas id="canvas"/>
    </body>-->

    <iframe width=100% height=100% src="http://{{ip_addr}}:8081/passive_radar.html"></iframe>
</body>
</html>
