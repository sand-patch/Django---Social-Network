document.addEventListener("DOMContentLoaded", (event) => {
    event.preventDefault();
    const toggles = document.querySelectorAll(".read-more");

    toggles.forEach((toggle) => {
        toggle.addEventListener("click", () => {
            const targetId = toggle.getAttribute("data-target");
            const body = document.getElementById(targetId);
            body.classList.toggle("collapsed");

            if (body.classList.contains("collapsed")) {
                toggle.textContent = "Read more";
            }
            else {
                toggle.textContent = "Show less";
            }
        });
    });

});