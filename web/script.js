google.charts.load('current', {'packages':['gauge']});
google.charts.setOnLoadCallback(drawChart);
function drawChart() {

  var data = google.visualization.arrayToDataTable([
    ['Label', 'Value'],
    ['Falcons', 80],
    ['Patriots', 55],
  ]);

  var options = {
    width: 800, height: 800,
    redFrom: 500, redTo: 550,
    yellowFrom:400, yellowTo: 500,
    minorTicks: 5, max: 550
  };

  var chart = new google.visualization.Gauge(document.getElementById('chart-div'));

  chart.draw(data, options);

  setInterval(function() {
    data.setValue(0, 1, 40 + Math.round(60 * Math.random()));
    chart.draw(data, options);
  }, 1000);
  setInterval(function() {
    data.setValue(1, 1, 40 + Math.round(60 * Math.random()));
    chart.draw(data, options);
  }, 1000);
  setInterval(function() {
    data.setValue(2, 1, 60 + Math.round(20 * Math.random()));
    chart.draw(data, options);
  }, 4000);
}
