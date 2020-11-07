import json
import os

if os.path.exists('settings.json'):
    with open('settings.json', 'r') as myfile:
        settings=json.loads(myfile.read())
else:
    settings = {}
    with open('settings.json', 'w') as outfile:
        json.dump(settings, outfile)

# Receiver Configuration
center_freq = settings.get("center_freq", 100.0)
samp_index = settings.get("samp_index", 2)
uniform_gain = settings.get("uniform_gain", 0)
gain_index = settings.get("gain_index", 0)
gain_index_2 = settings.get("gain_index_2", 0)
gain_index_3 = settings.get("gain_index_3", 0)
gain_index_4 = settings.get("gain_index_4", 0)
dc_comp = settings.get("dc_comp", 0)
filt_bw = settings.get("filt_bw", 150.0)
fir_size = settings.get("fir_size", 0)
decimation = settings.get("decimation", 1)

# Sync
en_sync = settings.get("en_sync", 0)
en_noise = settings.get("en_noise", 0)

# DOA Estimation
ant_arrangement_index = settings.get("ant_arrangement_index", "0")
ant_spacing = settings.get("ant_spacing", "0.5")
en_doa = settings.get("en_doa", None)
en_bartlett = settings.get("en_bartlett", None)
en_capon = settings.get("en_capon", None)
en_MEM = settings.get("en_MEM", None)
en_MUSIC = settings.get("en_MUSIC", None)
en_fbavg = settings.get("en_fbavg", None)

# Passive Radar
en_pr = settings.get("en_pr", None)
ref_ch = settings.get("ref_ch", "0")
surv_ch = settings.get("surv_ch", "1")
en_clutter = settings.get("en_clutter", None)
filt_dim = settings.get("filt_dim", "127")
max_range = settings.get("max_range", "128.0")
max_doppler = settings.get("max_doppler", "500.0")
windowing_mode = settings.get("windowing_mode", "0")
dyn_range = settings.get("dyn_range", "20")
en_det = settings.get("en_det", None)
est_win = settings.get("est_win", "10")
guard_win = settings.get("guard_win", "4")
thresh_det = settings.get("thresh_det", "13.0")
en_peakhold = settings.get("en_peakhold", None)

def write():
    data = {}

    # Configuration
    data["center_freq"] = center_freq
    data["samp_index"] = samp_index
    data["uniform_gain"] = uniform_gain
    data["gain_index"] = gain_index
    data["gain_index_2"] = gain_index_2
    data["gain_index_3"] = gain_index_3
    data["gain_index_4"] = gain_index_4
    data["dc_comp"] = dc_comp
    data["filt_bw"] = filt_bw
    data["fir_size"] = fir_size
    data["decimation"] = decimation

    # Sync
    data["en_sync"] = en_sync
    data["en_noise"] = en_noise

    # DOA Estimation
    data["ant_arrangement_index"] = ant_arrangement_index
    data["ant_spacing"] = ant_spacing
    data["en_doa"] = en_doa
    data["en_bartlett"] = en_bartlett
    data["en_capon"] = en_capon
    data["en_MEM"] = en_MEM
    data["en_MUSIC"] = en_MUSIC
    data["en_fbavg"] = en_fbavg

    # Passive Radar
    data["en_pr"] = en_pr
    data["ref_ch"] = ref_ch
    data["surv_ch"] = surv_ch
    data["en_clutter"] = en_clutter
    data["filt_dim"] = filt_dim
    data["max_range"] = max_range
    data["max_doppler"] = max_doppler
    data["windowing_mode"] = windowing_mode
    data["dyn_range"] = dyn_range
    data["en_det"] = en_det
    data["est_win"] = est_win
    data["guard_win"] = guard_win
    data["thresh_det"] = thresh_det
    data["en_peakhold"] = en_peakhold

    with open('settings.json', 'w') as outfile:
        json.dump(data, outfile)
