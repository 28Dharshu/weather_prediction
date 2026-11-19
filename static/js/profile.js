document.addEventListener("DOMContentLoaded", async () => {
    const res = await API.get("/api/profile");
    if (!res.ok || !res.data.success) {
        return;
    }

    const { user, stats, posts } = res.data;
    const initial = user.username ? user.username.charAt(0).toUpperCase() : "U";

    // Update avatar
    const avatarContainer = document.getElementById("profileAvatar");
    if (avatarContainer) {
        if (user.profile_picture) {
            avatarContainer.innerHTML = `<img src="${user.profile_picture}" alt="Profile">`;
        } else {
            avatarContainer.innerText = initial;
        }
    }

    // Update profile info
    const usernameEl = document.getElementById("profileUsername");
    if (usernameEl) usernameEl.innerText = user.username;

    const emailEl = document.getElementById("profileEmail");
    if (emailEl) emailEl.innerHTML = `<i class="fas fa-envelope"></i> ${escapeHtml(user.email)}`;

    const locationEl = document.getElementById("profileLocation");
    if (locationEl) locationEl.innerHTML = `<i class="fas fa-map-marker-alt"></i> ${escapeHtml(user.location || "Not specified")}`;

    // Update stats
    const postCountEl = document.getElementById("statPostsCount");
    if (postCountEl) postCountEl.innerText = stats.posts_count || posts.length;

    const followersEl = document.getElementById("statFollowersCount");
    if (followersEl) followersEl.innerText = stats.followers_count || 0;

    const followingEl = document.getElementById("statFollowingCount");
    if (followingEl) followingEl.innerText = stats.following_count || 0;

    // Render User's Gallery Grid
    const galleryContainer = document.getElementById("profileGalleryGrid");
    if (galleryContainer) {
        if (posts.length === 0) {
            galleryContainer.innerHTML = `
                <div style="grid-column: 1/-1; background:#fff; border-radius:12px; padding:30px; text-align:center; box-shadow:var(--card-shadow);">
                    <i class="fas fa-images" style="font-size:36px; color:var(--gray); margin-bottom:10px;"></i>
                    <p style="color:var(--gray);">You haven't uploaded any photos yet.</p>
                </div>
            `;
            return;
        }

        galleryContainer.innerHTML = posts.map(post => `
            <div class="gallery-card">
                <div class="gallery-img-wrapper">
                    <img src="${post.image_path}" alt="Post">
                </div>
                <div class="gallery-card-info">
                    <span style="font-size:12px; color:var(--gray);">
                        <i class="far fa-calendar-alt"></i> ${escapeHtml(post.created_at)}
                    </span>
                    <span style="font-size:12px; color:var(--gray); display:flex; gap:10px;">
                        <span><i class="fas fa-heart" style="color:var(--danger)"></i> ${post.like_count}</span>
                        <span><i class="fas fa-comment" style="color:var(--primary)"></i> ${post.comment_count}</span>
                    </span>
                </div>
            </div>
        `).join("");
    }
});

function escapeHtml(str) {
    if (!str) return "";
    return String(str)
        .replace(/&/g, "&amp;")
        .replace(/</g, "&lt;")
        .replace(/>/g, "&gt;")
        .replace(/"/g, "&quot;")
        .replace(/'/g, "&#039;");
}
