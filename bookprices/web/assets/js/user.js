const logoutUrl = "/auth/logout";
const logoutButtonId = "#logout-link";

function logoutUser() {
    let url = `${logoutUrl}?redirect_url=${encodeURIComponent(window.location.pathname + window.location.search)}`;
    $.ajax({
        url: url,
        type: "POST",
        dataType: "json",
        data: {
            "csrf_token": $(csrfTokenNodeId).val()
        },
        success: function(data) {
            window.location = data.redirect_url;
        },
        error: function(error) {
            console.log(error);
        }
    });
}

$(document).ready(function() {
    $(logoutButtonId).click(function() {
        logoutUser();
    });
})
