const priceChartContainer = $("#chart");
const priceTable = $("#price-table");

const pageHeading = $("h3");
const priceTableHeading = $("#price-table-heading");

function createChart(datesDesc, prices, color) {
    let datesAsc = datesDesc.slice().reverse(); // dates are returned in descending order
    let pricesOrdered = prices.slice().reverse();

    let options = getChartBaseOptions();
    console.log("Setting color to: " + color);
    options["series"] = [
        {
            name: "Pris",
            color: color,
            data: pricesOrdered
        }
    ];
    options["xaxis"]["categories"] = datesAsc;
    console.log(options);

    let chart = new ApexCharts(priceChartContainer.get(0), options);
    chart.render();
}

function createTable(datesDesc, prices, rowsCss) {
    $.each(datesDesc, function (index, date) {
        let price = prices[index];
        let rowCssClass = rowsCss[index];
        let row = $("<tr></tr>").addClass(rowCssClass);
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
            let color = data["color"];
            let rowsCss = data["row_css_classes"];
            if (datesDesc.length === 0 || prices.length === 0) {
                priceTable.remove();
                priceTableHeading.remove();
                pageHeading.text("Priser ikke hentet for den valgte webbutik");
            }
            else {
                createTable(datesDesc, prices, rowsCss);
                createChart(datesDesc, prices, color);
            }
        },
        "error" : function (error) {
            console.log(error);
        }
    });
});
