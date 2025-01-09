console.log("main.js loaded");

// Ensure styles and scripts load properly on mobile
document.addEventListener("DOMContentLoaded", function () {
    if (window.innerWidth < 768) {
        // Force a reload to ensure styles and scripts load
        if (!window.location.hash.includes("#reloaded")) {
            window.location.hash = "reloaded";
            window.location.reload();
        }
    }
});

const qrForm = document.getElementById("qr-form");
if (qrForm) {
    qrForm.addEventListener("submit", (e) => {
        const url = document.querySelector('input[name="url"]').value;
        const size = document.querySelector('input[name="box_size"]').value;

        console.log(`QR Code generated for URL: ${url}, Size: ${size}`);
    });
}