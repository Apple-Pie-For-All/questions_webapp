function toggleComment(commentId) {
    let content = document.getElementById("comment-" + commentId);
    content.classList.toggle("hidden");
}