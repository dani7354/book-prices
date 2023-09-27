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
