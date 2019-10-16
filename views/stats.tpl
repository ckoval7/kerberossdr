<hmtl>
 <head>
  <meta http-equiv="refresh" content="1">
 </head>
 <body>
   Update Rate: {{upd_rate}} | Overdrive: {{ovr_drv}}<br>
   % if autocal_status == "No GPIO":
       AutoCal Status: <span style="font-size:12pt; font-weight:600; color:#ff0000;">{{autocal_status}}</span>
   % else:
       AutoCal Status: {{autocal_status}}
  % end
</body>
</html>
