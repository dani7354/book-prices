const baseUrl = "/job";

const messageFieldName = "message";
const jobRunsFieldName = "job_runs";
const jobRunIdFieldName = "id";
const formActionUrlFieldName = "form_action_url";
const priorityFieldName = "priority";
const prioritiesFieldName = "priorities";


function showAlert(message, alertType, container) {
    let alert = $("<div></div>")
        .attr("class", `alert alert-${alertType} alert-dismissible fade show`)
        .attr("role", "alert")
        .text(message);
    alert.append(
        $("<button></button>")
            .attr("class", "btn-close")
            .attr("data-bs-dismiss", "alert")
            .attr("aria-label", "Close")
            .attr("type", "button"));
    container.prepend(alert);
    alert.alert();
}