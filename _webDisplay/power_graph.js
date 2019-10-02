var canvas ;
var context ;
var Val_max;
var Val_min;
var sections;
var xScale;
var yScale;
		// Values for the Data Plot, they can also be obtained from a external file

var margin = 20;
var Power = [0,0];
for(var i = 0; i < 62; i++){
	//var min=0;
    //var max=25;
    var random = 0 //Math.random() * (+max - +min) + +min;
	Power.push(random);
}



function gr_init() {
		// set these values for your data
  Power.pop();
  Power.push(PWR_val);
	sections = 60;
	Val_max = 30;
	Val_min = 0;
	var stepSize = 3;
	var columnSize = 15;
	var rowSize = 20;
	var xAxis = [0];
	for(var i = 0; i < 61; i++){
		xAxis.push(i);
	}
		//

	canvas = document.getElementById("gr_canvas");
	context = canvas.getContext("2d");
  context.clearRect(0, 0, canvas.width, canvas.height);
	context.fillStyle = "#000000";
	context.font = "20 pt Verdana";

	yScale = (canvas.height - columnSize - margin) / (Val_max - Val_min); //11
	xScale = (canvas.width - rowSize - margin) / sections; //10

	context.strokeStyle="#009933"; // color of grid lines
	context.beginPath();
		// print Parameters on X axis, and grid lines on the graph

	for (i=1;i<=sections;i++) {
		var x = i * xScale;
		context.fillText(xAxis[i], x + margin, columnSize);
		context.moveTo(x + margin, columnSize);
		context.lineTo(x + margin, canvas.height - margin);
	}
		// print row header and draw horizontal grid lines
	var count =  0;
	for (scale=Val_max;scale>=Val_min;scale = scale - stepSize) {
		var y = columnSize + (yScale * count * stepSize);
		context.fillText(scale, margin, y);
		context.moveTo(rowSize + margin, y);
		context.lineTo(canvas.width - margin, y);
		count++;
	}
	context.strokeRect(0,0,canvas.width,canvas.height)
	//context.strokeRect(0 + margin,0 + margin,canvas.width - margin,canvas.height - margin)
	context.stroke();

	context.translate(rowSize,canvas.height + Val_min * yScale);
	context.scale(1,-1 * yScale);

		// Color of each dataplot items

	context.strokeStyle="#000066";
	plotData(Power);
}

function plotData(dataSet) {
	context.beginPath();
	context.moveTo(16, 0+(margin/yScale));
	for (i=1;i<=sections;i++) {
		context.lineTo(i * xScale, dataSet[i] + (margin/yScale));
	}
	context.stroke();
}
