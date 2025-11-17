document.addEventListener('DOMContentLoaded', () => {
    //https://developer.mozilla.org/en-US/docs/Web/Security/Attacks/CSRF
    const getCookie = (name) => {
    return document.cookie
        .split('; ')
        .map(cookie => cookie.split('='))
        .find(([key]) => key === name)?.[1] || null;
    };

    const modal = document.getElementById('commentModal');
    let currPostId = null;

    modal.addEventListener('show.bs.modal', (e) => {
        const button = e.relatedTarget;
        currPostId = button.getAttribute('data-post-id');

        load_comment_modal(currPostId);
    });
    modal.addEventListener('hidden.bs.modal', () => {
        currPostId = null;
        modal.querySelector('.modal-body').innerHTML = '';
    })

    document.getElementById('commentModalBody').addEventListener('submit', async (e) => {
        if (e.target && e.target.id === 'comment-compose-form') {
            e.preventDefault();

            const comment_text = e.target.querySelector('textarea[name="comment"]').value;

            const response =await fetch(`/comment/${currPostId}`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': getCookie('csrftoken')
                },
                body: JSON.stringify({comment: comment_text})
            });

            if (response.ok) {
                e.target.querySelector('textarea[name="comment"]').value = '';
                load_comment_modal(currPostId);
            }
            else {
                console.error("Error commenting");
            }

        }
    });
});

function load_comment_modal(postId) {
    const modal = document.getElementById('commentModal');
    const modal_content = modal.querySelector('.modal-body');

    fetch(`/comment/${postId}/modal`)
    .then(response => {
        if (!response.ok) {
            throw new Error("Failed to load Comments");
        }
        return response.text();
    })
    .then(html => {
        modal_content.innerHTML = html;
        modal.style.display = 'block';
    })
    .catch(error => console.error(error));
}