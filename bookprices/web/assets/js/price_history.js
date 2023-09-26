const chartHeight = 400;
const priceChartContainer = $("#chart");
const priceTable = $("#price-table");

function createTable(container, priceHistoryResponse) {
    let dates_desc = priceHistoryResponse["dates"];
    let prices = priceHistoryResponse["prices"];

    $.each(dates_desc, function (index, date) {
        let price = prices[index];
        let row = $("<tr></tr>");
        row.append($("<td></td>").text(date));
        row.append($("<td></td>").text(price));
        container.append(row);
    });
}

function createChart(container, priceHistoryResponse) {
    let dates = priceHistoryResponse["dates"];
    let prices = priceHistoryResponse["prices"];
    var options = {
          series: [{
            name: "Pris",
            data: prices
        }],
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

$(document).ready(function () {
    let bookId = priceChartContainer.data("book");
    let storeId = priceChartContainer.data("store");
    let url = `/api/book/${bookId}/store/${storeId}`;

    $.ajax(url, {
        "method" : "GET",
        "dataType": "json",
        "success" : function (data, status, xhr) {
            createTable(priceTable, data);
            createChart(priceChartContainer, data);
        },
        "error" : function (error) {
            console.log(error);
        }
    });
});
