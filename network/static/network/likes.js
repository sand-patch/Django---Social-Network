const likeState = {};

document.addEventListener('DOMContentLoaded', () => {
    //https://developer.mozilla.org/en-US/docs/Web/Security/Attacks/CSRF
    const getCookie = (name) => {
        return document.cookie
        .split('; ')
        .map(cookie => cookie.split('='))
        .find(([key]) => key === name)?.[1] || null;
    };

    fetch("/like/all")
    .then(response => (response.ok && response.headers.get("content-type")?.includes("application/json")) ? response.json() : {})
    .then(data => {
        Object.assign(likeState, data);

        for (let postId in likeState) {
            update_ui(postId, true);
            const likeElement = document.getElementById(`like-count-${postId}`);
            if (likeElement) {
                likeElement.innerHTML = likeState[postId];
            }
        }
    })
    .catch( error => console.error("Could not fetch likes, ignoring for now:", error));

    const likeButtons = document.querySelectorAll(".like-button");

    likeButtons.forEach((btn) => {
        btn.addEventListener("click", () => {
            const targetId = btn.getAttribute("data-target");
            const likeElement = document.getElementById(`like-count-${targetId}`);
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
                throw new Error("Bad response");
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

});

function update_ui(post_id, liked) {
    const likeBtn = document.getElementById(`like-btn-img-${post_id}`);
    if (likeBtn) {
        likeBtn.src = liked ? HEART_LIKED : HEART_UNLIKED;
    }
}