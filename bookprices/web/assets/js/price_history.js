const priceChartContainer = $("#chart");
const priceTable = $("#price-table");

function createChart(priceHistoryResponse) {
    let dates = priceHistoryResponse["dates"].slice().reverse(); // dates are returned in descending order
    let prices = priceHistoryResponse["prices"].slice().reverse();

    let options = getChartBaseOptions();
    options["series"][0] = { name: "Pris",  data: prices };
    options["xaxis"]["categories"] = dates;

    let chart = new ApexCharts(priceChartContainer.get(0), options);
    chart.render();
}

function createTable(priceHistoryResponse) {
    let dates_desc = priceHistoryResponse["dates"];
    let prices = priceHistoryResponse["prices"];

    $.each(dates_desc, function (index, date) {
        let price = prices[index];
        let row = $("<tr></tr>");
        row.append($("<td></td>").text(date));
        row.append($("<td></td>").text(price));
        priceTable.append(row);
    });
}

$(document).ready(function () {
    let bookId = priceChartContainer.data("book");
    let storeId = priceChartContainer.data("store");
    let url = `/api/book/${bookId}/store/${storeId}`;

    $.ajax(url, {
        "method" : "GET",
        "dataType": "json",
        "success" : function (data, status, xhr) {
            createTable(data);
            createChart(data);
        },
        "error" : function (error) {
            console.log(error);
        }
    });
});
