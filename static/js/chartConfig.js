var chart;
Chart.defaults.global.defaultFontFamily = "Nunito";

function drawPitchChart(freqs, times) { 
  chartData = getInfoForGraph(freqs, times);
  var ctx = document.getElementById('chart').getContext('2d');
  chart = new Chart(ctx, {
    type: 'scatter',

    // The data for our dataset
    data: {
        datasets: [{
            label: "exercise",
            borderColor: 'rgb(0, 51, 153)',
            fill: false,
            data: chartData,
            steppedLine: true
        }],
    },

    // Configuration options go here
    options: {
      scales: {
            yAxes: [{
                type: 'logarithmic',
                ticks : { display : false }, 
                scaleLabel: {
                  display: true,
                  labelString: 'pitch (hz)'
                }
            }], 
            xAxes: [{
              scaleLabel: {
                display: true,
                labelString: 'time (seconds)'
              }
            }]
        }
    }
});

}


function getInfoForGraph(freqs, times) { 
  var data = []
  times.forEach( function(time, idx) {
    var point1 = {}; 
    var point2 = {};
    if (idx==0) { 
      point1['x'] = 0;
      point1['y'] = freqs[idx];
      data.push(point1);
    } else { 
      point1['x'] = data[data.length - 1]['x'];
      point1['y'] = freqs[idx];
      data.push(point1);
    }
    point2['x'] = data[data.length - 1]['x'] + time;
    point2['y'] = freqs[idx];
    data.push(point2);
  })
  return data
}

function resetCanvas() { 
  $('#chart').remove(); 
  $('#audioDisp').append('<canvas id="chart"><canvas>');
}