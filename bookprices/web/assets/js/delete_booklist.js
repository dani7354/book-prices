const baseUrl = "/booklist";
const btnDeleteBookList = $(".btn-delete-booklist");


$(document).ready(function () {
    btnDeleteBookList.on("click", function (e) {
        e.preventDefault();
        if (confirm("Er du sikker på, du vil slette denne bogliste?")) {
            let bookListId = $(e.target).data("booklist-id");
            deleteBookList(bookListId);
        }
    });
});


function deleteBookList(bookListId) {
    let url = `${baseUrl}/delete/${bookListId}`;
    $.ajax(url, {
        "method": "POST",
        "dataType": "json",
        "data": {
            "csrf_token": $(csrfTokenNodeId).val()
        },
        "success": function () {
            window.location.reload();
        },
        "error": function (error) {
            console.log(error);
        }
    });
}