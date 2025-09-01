const btnAddToBookList = $(".btn-add-to-booklist");
const btnRemoveFromBookList = $(".btn-remove-from-booklist");

const bookListBaseUrl = "/booklist";
const bookIdFieldName = "book_id";

const iconRemovePathOneDValue = "M6.146 6.146a.5.5 0 0 1 .708 0L8 7.293l1.146-1.147a.5.5 0 1 1 .708.708L8.707 8l1.147 1.146a.5.5 0 0 1-.708.708L8 8.707 6.854 9.854a.5.5 0 0 1-.708-.708L7.293 8 6.146 6.854a.5.5 0 0 1 0-.708";
const iconRemovePathTwoDValue = "M4 0a2 2 0 0 0-2 2v12a2 2 0 0 0 2 2h8a2 2 0 0 0 2-2V2a2 2 0 0 0-2-2zm0 1h8a1 1 0 0 1 1 1v12a1 1 0 0 1-1 1H4a1 1 0 0 1-1-1V2a1 1 0 0 1 1-1";
const iconAddPathOneDValue = "M8.5 6a.5.5 0 0 0-1 0v1.5H6a.5.5 0 0 0 0 1h1.5V10a.5.5 0 0 0 1 0V8.5H10a.5.5 0 0 0 0-1H8.5z";
const iconAddPathTwoDValue = "M2 2a2 2 0 0 1 2-2h8a2 2 0 0 1 2 2v12a2 2 0 0 1-2 2H4a2 2 0 0 1-2-2zm10-1H4a1 1 0 0 0-1 1v12a1 1 0 0 0 1 1h8a1 1 0 0 0 1-1V2a1 1 0 0 0-1-1";

function toggleButtonIcon(button, bookOnCurrentList) {
    let svg = button.find("svg", 0);
    let paths = svg.find("path");
    let pathOne = $(paths[0]);
    let pathTwo = $(paths[1]);

    if (bookOnCurrentList) {
        button.removeClass("btn-primary").addClass("btn-danger");
        button.removeClass("btn-add-to-booklist").addClass("btn-remove-from-booklist");
        svg.removeClass("bi-file-plus").addClass("bi-file-x");
        pathOne.attr("d", iconRemovePathOneDValue);
        pathTwo.attr("d", iconRemovePathTwoDValue);
        button.unbind("click");
        button.on("click", removeFromBookListEventHandler);
    }
    else {
        button.removeClass("btn-danger").addClass("btn-primary");
        button.removeClass("btn-remove-from-booklist").addClass("btn-add-to-booklist");
        svg.removeClass("bi-file-x").addClass("bi-file-plus");
        pathOne.attr("d", iconAddPathOneDValue);
        pathTwo.attr("d", iconAddPathTwoDValue);
        button.unbind("click");
        button.on("click", addToBookListEventHandler);
    }
}

function addToBookList(btn, bookId) {
     $.ajax(`${bookListBaseUrl}/add`, {
            "method": "POST",
            "dataType": "json",
            "async": false,
            "data": {
                book_id: bookId,
                "csrf_token": $(csrfTokenNodeId).val(),
            },
            "success": function () {
                toggleButtonIcon(btn, true);
            },
            "error": function (error) {
                console.log(error);
            }
     });
}

function removeFromBookList(btn, bookId) {
    $.ajax(`${bookListBaseUrl}/remove`, {
            "method": "POST",
            "dataType": "json",
            "async": false,
            "data": {
                "book_id": bookId,
                "csrf_token": $(csrfTokenNodeId).val()
            },
            "success": function () {
                toggleButtonIcon(btn, false);
            },
            "error": function (error) {
                console.log(error);
            }
    });
}

function addToBookListEventHandler(e) {
    e.preventDefault();
    let bookId = $(e.currentTarget).data("book-id");
    let button = $(e.currentTarget);
    addToBookList(button, bookId);
}

function removeFromBookListEventHandler(e) {
    e.preventDefault();
    let bookId = $(e.currentTarget).data("book-id");
    let button = $(e.currentTarget);
    removeFromBookList(button, bookId);
}

$(document).ready(function () {
    btnAddToBookList.on("click", addToBookListEventHandler);
    btnRemoveFromBookList.on("click", removeFromBookListEventHandler);
});