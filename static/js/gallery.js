document.addEventListener("DOMContentLoaded", async () => {
    const galleryContainer = document.getElementById("communityGalleryGrid");
    if (!galleryContainer) return;

    const res = await API.get("/api/posts");
    if (!res.ok || !res.data.success || res.data.posts.length === 0) {
        galleryContainer.innerHTML = `
            <div style="grid-column: 1/-1; background:#fff; border-radius:12px; padding:40px; text-align:center; box-shadow:var(--card-shadow);">
                <i class="fas fa-images" style="font-size:42px; color:var(--gray); margin-bottom:12px;"></i>
                <h3 style="margin-bottom:8px;">No community posts yet</h3>
                <p style="color:var(--gray);">Be the first one to share a photo on the platform!</p>
            </div>
        `;
        return;
    }

    galleryContainer.innerHTML = res.data.posts.map(post => {
        const initial = post.username ? post.username.charAt(0).toUpperCase() : "U";
        return `
            <div class="gallery-card">
                <div class="gallery-img-wrapper">
                    <img src="${post.image_path}" alt="Post by ${escapeHtml(post.username)}">
                </div>
                <div class="gallery-card-info">
                    <div class="gallery-user">
                        <div class="gallery-user-avatar">${initial}</div>
                        <div>
                            <div style="font-weight:600; font-size:13px;">${escapeHtml(post.username)}</div>
                            <div style="font-size:11px; color:var(--gray);">${escapeHtml(post.created_at)}</div>
                        </div>
                    </div>
                    <div style="display:flex; gap:12px; font-size:13px; color:var(--gray);">
                        <span><i class="fas fa-heart" style="color:var(--danger)"></i> ${post.like_count}</span>
                        <span><i class="fas fa-comment" style="color:var(--primary)"></i> ${post.comment_count}</span>
                    </div>
                </div>
            </div>
        `;
    }).join("");
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
