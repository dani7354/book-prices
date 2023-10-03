const chartContainer = $("#chart")

function createChart(priceHistoryResponse) {
    let dates = priceHistoryResponse["dates"];
    let prices_for_bookstores = priceHistoryResponse["prices"];
    let options = getChartBaseOptions();
    $.each(prices_for_bookstores, function (index, prices_for_bookstore) {
        options["series"][index] = { name: prices_for_bookstore.bookstore_name,  data: prices_for_bookstore.prices };
    });
    options["xaxis"]["categories"] = dates;

    let chart = new ApexCharts(chartContainer.get(0), options);
    chart.render();
}

$(document).ready(function () {
    let bookId = chartContainer.data("book");
    let url = `/api/book/${bookId}`;

    $.ajax(url, {
        "method" : "GET",
        "dataType": "json",
        "success" : function (data, status, xhr) {
            createChart(data);
        },
        "error" : function (error) {
            console.log(error);
        }
    });
});