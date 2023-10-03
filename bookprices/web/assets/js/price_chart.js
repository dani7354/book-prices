const chartHeight = 400;

function getChartBaseOptions() {
    let options = {
          series: [],
          chart: {
          height: chartHeight,
          type: "line",
          zoom: {
            enabled: false
          }
        },
        dataLabels: {
          enabled: false
        },
        stroke: {
          curve: "straight"
        },
        grid: {
          row: {
            colors: ["#f3f3f3", "transparent"],
            opacity: 0.5
          },
        },
        xaxis: {
          title: { text: "Dato" },
        },
        yaxis: {
          title: { text: "Pris" }
        }};

        return options;
}