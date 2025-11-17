const likeState = {};

document.addEventListener('DOMContentLoaded', () => {
    //https://developer.mozilla.org/en-US/docs/Web/Security/Attacks/CSRF
    const getCookie = (name) => {
        return document.cookie
        .split('; ')
        .map(cookie => cookie.split('='))
        .find(([key]) => key === name)?.[1] || null;
    };

    const likeButton = document.querySelector(".like-button");
    const targetId = likeButton.getAttribute("data-target");
    const likeElement = document.getElementById(`like-count-${targetId}`);

    fetch(`/like/${targetId}`)
    .then(response => (response.ok && response.headers.get("content-type")?.includes("application/json")) ? response.json() : {})
    .then(data => {
        Object.assign(likeState, data);
        update_ui(targetId, true);
        if (likeElement) {
            likeElement.innerHTML = likeState[targetId];
        }
    })
    .catch(error => console.error("Could not fetch likes, ignoring for now", error));

    likeButton.addEventListener("click", () => {
        const isLiked = !!likeState[targetId];
        const url = `/post/${targetId}`;
        const options = {
            method: isLiked ? "DELETE" : "PUT",
            headers: {"X-CSRFToken": getCookie('csrftoken')}
        };

        fetch(url, options)
        .then(response => {
            if (response.status === 302 || response.url.includes("/login/")) {
                window.location.href = "/login/";
            }
            if (response.ok) {
                return response.json();
            }
            throw new Error("Bad Response");
        })
        .then(data => {
            if (isLiked) {
                delete likeState[targetId];
                update_ui(targetId, false);
                if (likeElement) {
                    likeElement.innerHTML = parseInt(likeElement.innerHTML) - 1;
                }
            }
            else {
                likeState[targetId] = data[targetId];
                update_ui(targetId, true);
                if (likeElement) {
                    likeElement.innerHTML = data[targetId];
                }
            }
        })
        .catch(error => console.error("Network error:", error));

    });
});

function update_ui(post_id, liked) {
    const likeBtn = document.getElementById(`like-btn-img-${post_id}`);
    if (likeBtn) {
        likeBtn.src = liked ? HEART_LIKED : HEART_UNLIKED;
    }
}