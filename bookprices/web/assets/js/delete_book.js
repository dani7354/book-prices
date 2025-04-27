const baseUrl = "/book";
const redirectUrl = "/search";
const btnDeleteBook = $("#btn-delete-book");


$(document).ready(function () {
    btnDeleteBook.on("click", function (e){
        e.preventDefault();
        if (confirm("Er du sikker på at du vil slette bogen?")) {
            let bookId = $(e.target).data("book-id");
            deleteBook(bookId);
        }
    });
});

function deleteBook(bookId) {
    let url = `${baseUrl}/delete/${bookId}`;
    $.ajax(url, {
        "method": "POST",
        "dataType": "json",
        "data": {
            "csrf_token": $(csrfTokenNodeId).val()
        },
        "success": function () {
            window.location.href  = redirectUrl;
        },
        "error": function (error) {
            console.log(error);
        }
    });
}