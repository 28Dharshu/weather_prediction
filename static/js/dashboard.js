let currentUser = null;

document.addEventListener("DOMContentLoaded", async () => {
    // 1. Load User Info
    await loadCurrentUser();

    // 2. Load Dashboard Widgets
    loadWeather();
    loadNews();
    loadUserPosts();

    // 3. Setup Post Upload Form & Image Preview
    setupUploadForm();
});

async function loadCurrentUser() {
    const res = await API.get("/api/auth/me");
    if (res.ok && res.data.logged_in) {
        currentUser = res.data.user;
        const initial = currentUser.username ? currentUser.username.charAt(0).toUpperCase() : "U";

        // Update welcome header & avatars
        const welcomeName = document.getElementById("welcomeUsername");
        if (welcomeName) welcomeName.innerText = currentUser.username;

        const infoName = document.getElementById("infoUsername");
        if (infoName) infoName.innerText = currentUser.username;

        const infoEmail = document.getElementById("infoEmail");
        if (infoEmail) infoEmail.innerText = currentUser.email;

        const infoLocation = document.getElementById("infoLocation");
        if (infoLocation) infoLocation.innerText = currentUser.location || "Not set";

        document.querySelectorAll(".current-user-avatar").forEach(el => {
            if (currentUser.profile_picture) {
                el.innerHTML = `<img src="${currentUser.profile_picture}" alt="Avatar">`;
            } else {
                el.innerText = initial;
            }
        });
    }
}

async function loadWeather() {
    const weatherContainer = document.getElementById("weatherContent");
    if (!weatherContainer) return;

    const res = await API.get("/api/weather");
    if (!res.ok || !res.data.success || !res.data.current) {
        weatherContainer.innerHTML = `<p style="color:var(--gray);text-align:center;padding:20px 0;">Weather data not available for ${currentUser?.location || "location"}.</p>`;
        return;
    }

    const current = res.data.current;
    const forecast = res.data.forecast || [];
    const iconCode = current.weather?.[0]?.icon || "01d";
    const temp = Math.round(current.main?.temp ?? 0);
    const desc = current.weather?.[0]?.description || "";
    const humidity = current.main?.humidity ?? 0;
    const windSpeed = current.wind?.speed ?? 0;

    let forecastHtml = "";
    if (forecast.length > 0) {
        forecastHtml = `
            <div class="forecast-container">
                ${forecast.map(item => `
                    <div class="forecast-item">
                        <strong>${new Date(item.dt * 1000).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}</strong>
                        <img src="https://openweathermap.org/img/wn/${item.weather[0].icon}.png" alt="${item.weather[0].main}">
                        <div>${Math.round(item.main.temp)}°C</div>
                    </div>
                `).join("")}
            </div>
        `;
    }

    weatherContainer.innerHTML = `
        <div class="weather-card">
            <div style="text-align:center;">
                <img src="https://openweathermap.org/img/wn/${iconCode}@2x.png" alt="Weather" style="width:70px;height:70px;">
            </div>
            <div class="weather-temp">${temp}°C</div>
            <div class="weather-desc">${desc} - ${res.data.location}</div>
            <div class="weather-details">
                <div class="weather-detail"><i class="fas fa-tint"></i> Humidity: ${humidity}%</div>
                <div class="weather-detail"><i class="fas fa-wind"></i> Wind: ${windSpeed} m/s</div>
            </div>
            ${forecastHtml}
        </div>
    `;
}

async function loadNews() {
    const newsContainer = document.getElementById("newsContent");
    if (!newsContainer) return;

    const res = await API.get("/api/news");
    if (!res.ok || !res.data.success || !res.data.articles || res.data.articles.length === 0) {
        newsContainer.innerHTML = `<p style="color:var(--gray);padding:15px 0;">No news headlines available at the moment.</p>`;
        return;
    }

    const items = res.data.articles.map(article => `
        <div class="news-item">
            <div class="news-title">${escapeHtml(article.title)}</div>
            <div class="news-description">${escapeHtml(article.description || "")}</div>
            <div class="news-meta">
                <span>Source: ${escapeHtml(article.source?.name || "News")}</span>
                <a href="${escapeHtml(article.url)}" target="_blank" rel="noopener">Read more <i class="fas fa-external-link-alt" style="font-size:10px;"></i></a>
            </div>
        </div>
    `).join("");

    newsContainer.innerHTML = items;
}

function setupUploadForm() {
    const toggleBtn = document.getElementById("togglePostFormBtn");
    const formContainer = document.getElementById("postFormContainer");
    const imageInput = document.getElementById("postImageInput");
    const dropzone = document.getElementById("uploadDropzone");
    const preview = document.getElementById("imagePreview");
    const uploadForm = document.getElementById("createPostForm");

    if (toggleBtn && formContainer) {
        toggleBtn.addEventListener("click", () => {
            formContainer.classList.toggle("active");
            toggleBtn.innerHTML = formContainer.classList.contains("active") 
                ? '<i class="fas fa-times"></i> Cancel' 
                : '<i class="fas fa-plus"></i> Create New Post';
        });
    }

    if (dropzone && imageInput) {
        dropzone.addEventListener("click", () => imageInput.click());

        imageInput.addEventListener("change", (e) => {
            const file = e.target.files[0];
            if (file) {
                const reader = new FileReader();
                reader.onload = (event) => {
                    preview.src = event.target.result;
                    preview.style.display = "block";
                };
                reader.readAsDataURL(file);
            }
        });
    }

    if (uploadForm) {
        uploadForm.addEventListener("submit", async (e) => {
            e.preventDefault();
            const submitBtn = uploadForm.querySelector("button[type='submit']");
            const file = imageInput.files[0];
            if (!file) {
                alert("Please select an image to upload.");
                return;
            }

            const formData = new FormData();
            formData.append("post_image", file);
            const caption = document.getElementById("postCaption")?.value || "";
            formData.append("caption", caption);

            submitBtn.disabled = true;
            submitBtn.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Uploading...';

            const res = await API.request("/api/posts", {
                method: "POST",
                body: formData
            });

            submitBtn.disabled = false;
            submitBtn.innerHTML = '<i class="fas fa-cloud-upload-alt"></i> Publish Post';

            if (res.ok && res.data.success) {
                uploadForm.reset();
                if (preview) preview.style.display = "none";
                formContainer.classList.remove("active");
                if (toggleBtn) toggleBtn.innerHTML = '<i class="fas fa-plus"></i> Create New Post';
                // Reload user posts
                loadUserPosts();
            } else {
                alert(res.data.error || "Failed to upload image.");
            }
        });
    }
}

async function loadUserPosts() {
    const postsContainer = document.getElementById("userPostsContainer");
    if (!postsContainer) return;

    if (!currentUser) return;
    const res = await API.get(`/api/posts?user_id=${currentUser.id}`);

    if (!res.ok || !res.data.success || res.data.posts.length === 0) {
        postsContainer.innerHTML = `
            <div style="background:#fff;border-radius:12px;padding:30px;text-align:center;box-shadow:var(--card-shadow);">
                <i class="fas fa-camera" style="font-size:36px;color:var(--gray);margin-bottom:10px;"></i>
                <p style="color:var(--gray);">You haven't uploaded any posts yet. Click "Create New Post" to share your first photo!</p>
            </div>
        `;
        return;
    }

    postsContainer.innerHTML = res.data.posts.map(post => createPostCardHtml(post)).join("");

    // Load comments for each rendered post
    res.data.posts.forEach(post => {
        loadComments(post.id);
    });
}

function createPostCardHtml(post) {
    const initial = post.username ? post.username.charAt(0).toUpperCase() : "U";
    const likedClass = post.liked_by_user ? "active" : "";

    return `
        <div class="post" id="post-card-${post.id}">
            <div class="post-header">
                <div class="post-user-avatar">${initial}</div>
                <div class="post-info">
                    <h4>${escapeHtml(post.username)}</h4>
                    <div class="post-date">Posted on ${escapeHtml(post.created_at)}</div>
                </div>
            </div>

            <img src="${post.image_path}" alt="Post image" class="post-image">
            ${post.caption ? `<p style="margin-bottom:12px;font-size:14px;">${escapeHtml(post.caption)}</p>` : ""}

            <div class="post-actions">
                <div class="post-stats">
                    <div class="post-stat">
                        <i class="fas fa-heart" style="color:var(--danger)"></i>
                        <span id="like-count-${post.id}">${post.like_count} likes</span>
                    </div>
                    <div class="post-stat">
                        <i class="fas fa-comment" style="color:var(--primary)"></i>
                        <span id="comment-count-${post.id}">${post.comment_count} comments</span>
                    </div>
                </div>

                <div class="post-buttons">
                    <button class="btn btn-outline btn-sm ${likedClass}" id="like-btn-${post.id}" onclick="handleLikePost(${post.id})">
                        <i class="fas fa-heart"></i> Like
                    </button>
                    <button class="btn btn-danger btn-sm" onclick="handleDeletePost(${post.id})">
                        <i class="fas fa-trash"></i> Delete
                    </button>
                </div>
            </div>

            <!-- Comments Section -->
            <div class="comments-section">
                <form class="comment-form" onsubmit="handleAddComment(event, ${post.id})">
                    <input type="text" id="comment-input-${post.id}" placeholder="Write a comment..." required>
                    <button type="submit" class="btn btn-primary btn-sm">
                        <i class="fas fa-paper-plane"></i> Post
                    </button>
                </form>
                <div class="comments-list" id="comments-list-${post.id}">
                    <div style="font-size:12px;color:var(--gray);">Loading comments...</div>
                </div>
            </div>
        </div>
    `;
}

async function handleLikePost(postId) {
    const likeBtn = document.getElementById(`like-btn-${postId}`);
    const likeCountSpan = document.getElementById(`like-count-${postId}`);

    const res = await API.post(`/api/posts/${postId}/like`);
    if (res.ok && res.data.success) {
        if (res.data.liked) {
            likeBtn.classList.add("active");
        } else {
            likeBtn.classList.remove("active");
        }
        likeCountSpan.innerText = `${res.data.total_likes} likes`;
    }
}

async function handleDeletePost(postId) {
    if (!confirm("Are you sure you want to delete this post? This cannot be undone.")) {
        return;
    }

    const res = await API.delete(`/api/posts/${postId}`);
    if (res.ok && res.data.success) {
        const postCard = document.getElementById(`post-card-${postId}`);
        if (postCard) {
            postCard.style.transition = "opacity 0.3s";
            postCard.style.opacity = "0";
            setTimeout(() => postCard.remove(), 300);
        }
    } else {
        alert(res.data.error || "Failed to delete post.");
    }
}

async function loadComments(postId) {
    const container = document.getElementById(`comments-list-${postId}`);
    if (!container) return;

    const res = await API.get(`/api/posts/${postId}/comments`);
    if (!res.ok || !res.data.success || res.data.comments.length === 0) {
        container.innerHTML = `<div style="font-size:13px;color:var(--gray);padding:5px 0;">No comments yet.</div>`;
        return;
    }

    container.innerHTML = res.data.comments.map(c => `
        <div class="comment">
            <div class="comment-avatar">${c.username.charAt(0).toUpperCase()}</div>
            <div class="comment-body">
                <div class="comment-author">
                    <span>${escapeHtml(c.username)}</span>
                    <span style="font-size:11px;color:var(--gray);font-weight:normal;">${escapeHtml(c.created_at)}</span>
                </div>
                <div class="comment-text">${escapeHtml(c.comment)}</div>
            </div>
        </div>
    `).join("");
}

async function handleAddComment(e, postId) {
    e.preventDefault();
    const input = document.getElementById(`comment-input-${postId}`);
    const text = input.value.trim();
    if (!text) return;

    input.value = "";
    const res = await API.post(`/api/posts/${postId}/comments`, { comment_text: text });

    if (res.ok && res.data.success) {
        // Reload comments and update count
        loadComments(postId);
        const commentCountSpan = document.getElementById(`comment-count-${postId}`);
        if (commentCountSpan) {
            const currentCount = parseInt(commentCountSpan.innerText) || 0;
            commentCountSpan.innerText = `${currentCount + 1} comments`;
        }
    } else {
        alert(res.data.error || "Failed to post comment.");
    }
}

function escapeHtml(str) {
    if (!str) return "";
    return String(str)
        .replace(/&/g, "&amp;")
        .replace(/</g, "&lt;")
        .replace(/>/g, "&gt;")
        .replace(/"/g, "&quot;")
        .replace(/'/g, "&#039;");
}
