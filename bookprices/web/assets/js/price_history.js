const priceChartContainer = $("#chart");
const priceTable = $("#price-table");

const pageHeading = $("h3");
const priceTableHeading = $("#price-table-heading");

function createChart(datesDesc, prices) {
    let datesAsc = datesDesc.slice().reverse(); // dates are returned in descending order
    let pricesOrdered = prices.slice().reverse();

    let options = getChartBaseOptions();
    options["series"][0] = { name: "Pris",  data: pricesOrdered };
    options["xaxis"]["categories"] = datesAsc;

    let chart = new ApexCharts(priceChartContainer.get(0), options);
    chart.render();
}

function createTable(datesDesc, prices) {
    $.each(datesDesc, function (index, date) {
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
            let datesDesc = data["dates"];
            let prices = data["prices"];
            if (datesDesc.length === 0 || prices.length === 0) {
                priceTable.remove();
                priceTableHeading.remove();
                pageHeading.text("Priser ikke hentet for den valgte webbutik");
            }
            else {
                createTable(datesDesc, prices);
                createChart(datesDesc, prices);
            }
        },
        "error" : function (error) {
            console.log(error);
        }
    });
});
