const chartHeight = 400;

function getChartBaseOptions() {
    return {
            series: [],
            chart: {
                height: chartHeight,
                type: "line",
                zoom: {
                    enabled: false
                }
            },
            dataLabels: {
                enabled: true
            },
            stroke: {
                curve: "stepline",
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
            }
        };
}