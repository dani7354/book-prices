const chartHeight = 400;

function createChart(container, priceHistoryResponse) {
    let dates = priceHistoryResponse["dates"];
    let prices = priceHistoryResponse["prices"];
    var options = {
          series: [{ name: "Pris", data: prices }],
          chart: {
          height: chartHeight,
          type: 'line',
          zoom: {
            enabled: false
          }
        },
        dataLabels: {
          enabled: false
        },
        stroke: {
          curve: 'straight'
        },
        grid: {
          row: {
            colors: ['#f3f3f3', 'transparent'],
            opacity: 0.5
          },
        },
        xaxis: {
          title: { text: "Dato" },
          categories: dates
        },
        yaxis: {
          title: { text: 'Pris' }
        }};

    var chart = new ApexCharts(container.get(0), options);
    chart.render();
}