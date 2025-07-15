function initReviewSummaryButtons() {
    const buttons = document.querySelectorAll(".r-sum-btn");

    buttons.forEach(button => {
        button.addEventListener("click", function () {
            const productId = this.dataset.productId;

            // productId가 일치하는 summary-box를 직접 선택
            const box = document.querySelector(`.summary-box[data-product-id="${productId}"]`);
            if (!box) return;

            box.innerHTML = "요약 중...";

            fetch(`/api/product/${productId}/summary/`)
                .then(response => response.json())
                .then(data => {
                    box.innerHTML = `<p>${data.summary.replace(/\n/g, "<br>")}</p>`;
                })
                .catch(error => {
                    box.innerHTML = "요약 실패 😢";
                    console.error("요약 오류", error);
                });
        });
    });
}

document.addEventListener("DOMContentLoaded", initReviewSummaryButtons);
