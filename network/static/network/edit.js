document.addEventListener('DOMContentLoaded', () => {

    const getCookie = (name) => {
        return document.cookie
            .split('; ')
            .map(cookie => cookie.split('='))
            .find(([key]) => key === name)?.[1] || null;
    };

    const edits = document.querySelectorAll('.btn.btn-primary.edit-post-button');

    edits.forEach((edtBtn) => {
        const postAuthId = edtBtn.getAttribute('data-auth-id');
        if (REQUEST_USER === postAuthId) {
            const postId = edtBtn.getAttribute('data-edit-post'); 
            const postTitle = document.getElementById(`post-title-${postId}`);
            const body_content = document.getElementById(`post-${postId}`);
            const postBodyWrapper = body_content.parentElement; // .card-text-wrapper
            const saveBtn = document.getElementById(`save-${postId}`);
            const cancelBtn = document.getElementById(`cancel-${postId}`);
            const readMoreElement = document.querySelector(`.read-more[data-target="post-${postId}"]`);

            const titleBar = document.createElement('input');
            titleBar.classList.add("form-control");

            const bodyTextarea = document.createElement('textarea');
            bodyTextarea.classList.add("form-control");
            bodyTextarea.name = "post-body";
            bodyTextarea.rows = 3;

            edtBtn.addEventListener('click', (e) => {
                e.preventDefault();

                postTitle.style.display = 'none';
                body_content.style.display = 'none';
                edtBtn.style.display = 'none';
                saveBtn.style.display = 'inline-block';
                cancelBtn.style.display = 'inline-block';
                readMoreElement.style.display = 'none';

                titleBar.value = postTitle.innerText;
                bodyTextarea.value = body_content.innerText;

                if (!postBodyWrapper.contains(titleBar)) {
                    postBodyWrapper.appendChild(titleBar);
                }
                if (!postBodyWrapper.contains(bodyTextarea)) {
                    postBodyWrapper.appendChild(bodyTextarea);
                } 
            });

            saveBtn.addEventListener('click', async (e) => {
                e.preventDefault();

                try {
                    const response = await fetch(`/edit/${postId}`, {
                        method: "PUT",
                        headers: {
                            "X-CSRFToken": getCookie('csrftoken'),
                            "Content-Type": "application/json",
                            "Accept": "application/json"
                        },
                        body: JSON.stringify({ 
                            title: titleBar.value,
                            body: bodyTextarea.value 
                        })
                    });

                    if (response.ok) {
                        const data = await response.json();
                        //console.log(data);

                        postTitle.innerText = titleBar.value;
                        body_content.innerText = bodyTextarea.value;

                        postTitle.style.display = 'block';
                        body_content.style.display = 'block';
                        edtBtn.style.display = 'block';
                        saveBtn.style.display = 'none';
                        cancelBtn.style.display = 'none';
                        readMoreElement.style.display = 'block';

                        titleBar.remove();
                        bodyTextarea.remove();
                    } else {
                        console.error("Error Editing");
                        alert("Could not save changes. Please try again.");
                    }
                } catch (err) {
                    console.error("Network error:", err);
                    alert("Network error.");
                }
            });

            cancelBtn.addEventListener('click', () => {
                postTitle.style.display = 'block';
                body_content.style.display = 'block';
                edtBtn.style.display = 'block';
                saveBtn.style.display = 'none';
                cancelBtn.style.display = 'none';
                readMoreElement.style.display = 'block';

                titleBar.remove();
                bodyTextarea.remove();
            });
        }
    });

});
