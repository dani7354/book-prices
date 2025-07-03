const baseUrl = "/bookstore";
const redirectUrl = "/bookstore";
const btnDeleteUser = $(".btn-delete-bookstore");


$(document).ready(function () {
    btnDeleteUser.on("click", function (e) {
        e.preventDefault();
        if (confirm("Er du sikker på, at du vil slette boghandlen?")) {
            let bookstoreId = $(e.target).data("bookstore-id");
            deleteBookStore(bookstoreId);
        }
    });
});


function deleteBookStore(bookstoreId) {
    let url = `${baseUrl}/delete/${bookstoreId}`;
    $.ajax(url, {
        "method": "POST",
        "dataType": "json",
        "data": {
            "csrf_token": $(csrfTokenNodeId).val()
        },
        "success": function () {
            window.location.href = redirectUrl;
        },
        "error": function (error) {
            console.log(error);
        }
    });
}