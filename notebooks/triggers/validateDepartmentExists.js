function validateDepartmentExists() {
    var context = getContext();
    var request = context.getRequest();
    var newDocument = request.getBody();

    if (!newDocument.department) {
        newDocument["department"] = "General"
    }

    request.setBody(newDocument);
}