document.addEventListener('DOMContentLoaded', () => {
    const getCookie = (name) => {
        return document.cookie
            .split('; ')
            .map(cookie => cookie.split('='))
            .find(([key]) => key === name)?.[1] || null;
    };

    const userId = document.getElementById('follow-button').getAttribute('data-user-id');
    const followForm = document.getElementById('profile-follow-form');
    const unfollowForm = document.getElementById('profile-unfollow-form');
    const followBtn = document.getElementById('profile-follow');   
    const unfollowBtn = document.getElementById('profile-unfollow'); 
    const followerCnt = document.getElementById('followers_cnt');

    fetch(`/follow/${userId}`, {
        method: 'GET',
        headers: { 'Accept': 'application/json' }
    })
    .then(response => (response.ok && response.headers.get("Content-Type")?.includes("application/json")) ? response.json() : {})
    .then(data => {
        if (data.isFollower) {
            followBtn.style.display = 'none';
            unfollowBtn.style.display = 'block';
        } else {
            followBtn.style.display = 'block';
            unfollowBtn.style.display = 'none';
        }
    })
    .catch(error => console.error("Network error:", error));

    followForm.addEventListener('submit', async (e) => {
        e.preventDefault();
        try {
            const response = await fetch(`/follow/${userId}`, {
                method: 'PUT',
                headers: {
                    'X-CSRFToken': getCookie('csrftoken'),
                    'Accept': 'application/json'
                }
            });

            if (response.ok) {
                const data = await response.json();
                console.log("Followed:", data);
                followBtn.style.display = 'none';
                unfollowBtn.style.display = 'block';
                followerCnt.innerHTML = `<span><strong>Followers: </strong></span>${data.followerCnt}`;
            } else {
                console.error("Error following");
            }
        } catch (error) {
            console.error("Network error:", error);
        }
    });

    unfollowForm.addEventListener('submit', async (e) => {
        e.preventDefault();
        try {
            const response = await fetch(`/follow/${userId}`, {
                method: 'DELETE',
                headers: {
                    'X-CSRFToken': getCookie('csrftoken'),
                    'Accept': 'application/json'
                }
            });

            if (response.ok) {
                const data = await response.json();
                console.log("Unfollowed:", data);
                followBtn.style.display = 'block';
                unfollowBtn.style.display = 'none';
                followerCnt.innerHTML = `<span><strong>Followers: </strong></span>${data.followerCnt}`;
            } else {
                console.error("Error unfollowing");
            }
        } catch (error) {
            console.error("Network error:", error);
        }
    });
});
