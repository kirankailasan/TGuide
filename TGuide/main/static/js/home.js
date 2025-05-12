// Popup Login Functionality
const loginButton = document.getElementById("loginBtn");
const popup = document.getElementById("popup");
const closePopupButton = document.getElementById("closePopup");

// Show the popup when the login button is clicked
if (loginButton) {
    loginButton.addEventListener("click", () => {
        popup.style.display = "flex";
    });
}

// Close the popup when the close button is clicked
if (closePopupButton) {
    closePopupButton.addEventListener("click", () => {
        popup.style.display = "none";
    });
}

// Close the popup when clicking outside the popup content
window.addEventListener("click", (event) => {
    if (event.target === popup) {
        popup.style.display = "none";
    }
});








