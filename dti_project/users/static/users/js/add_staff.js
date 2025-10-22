document.getElementById('add-staff-form').addEventListener('submit', async function(e) {
    e.preventDefault();

    const form = this;
    const formData = new FormData(form);

    const response = await fetch("", {
        method: "POST",
        headers: { "X-Requested-With": "XMLHttpRequest" },
        body: formData
    });

    const data = await response.json();

    if (data.success) {
        // Load the popup HTML dynamically (fetch the separate HTML file)
        const popupContainer = document.getElementById('popup-container');
        const popupHTML = await fetch('/static/users/templates/staff_created_popup.html')
            .then(res => res.text());

        popupContainer.innerHTML = popupHTML;
        popupContainer.style.display = 'block';

        document.getElementById('popupEmail').innerText = data.email;
        document.getElementById('popupPassword').innerText = data.password;

        // Bind delete button
        document.getElementById('deleteBtn').onclick = async function() {
            await fetch(`/users/staff-accounts/delete/${data.user_id}/`, {
                method: "POST",
                headers: {
                    'X-CSRFToken': formData.get('csrfmiddlewaretoken'),
                    'X-Requested-With': 'XMLHttpRequest'
                }
            });
            window.location.href = "/users/staff-accounts/";  // Adjust URL if needed
        };
    } else {
        // handle errors here
        alert("Error creating staff account.");
    }
});
