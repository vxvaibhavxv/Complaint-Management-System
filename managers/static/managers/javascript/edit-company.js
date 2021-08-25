function removeLogo() {
    let companyLogo = document.getElementById("companyLogo");

    if (companyLogo.src === "https://via.placeholder.com/512") {
        return;
    }

    fetch("/managers/remove-logo/", {
        method: "POST",
        headers: {
            "X-CSRFToken": document.querySelector("[name=csrfmiddlewaretoken]").value
        }
    })
    .then(response => response.json())
    .then(response => {
        if (response.success) {
            companyLogo.src = "https://via.placeholder.com/512";
        }
    });
}