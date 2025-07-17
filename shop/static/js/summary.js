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


function liveSearch(search_input,target_selector,searchUrl = "/"){
    const input = document.querySelector(search_input);
    const container = document.querySelector(target_selector);

    if (!search_input || !container){
        console.warn("입력창 또는 결과 영역 사라짐");
        return;
    }

    let timeOut = null;

    input.addEventListener("input",function(){
        const query = input.value.trim();

        if(query.length < 1) return;

        clearTimeout(timeOut);
        debouncTimeout = setTimeout(() => {
            fetch(`${searchUrl}?q=${encodeURIComponent(query)}&partial=true`)
                .then(resp => {
                    if(!resp.ok) throw new Error("서버오류");
                    return resp.text();
                })
                .then(html => {
                    container.innerHTML = html;
                    initReviewSummaryButtons();
                })
                .catch(err => {
                    console.error("검색 실패" ,err);
                    container.innerHTML = "<p>검색중 오류 발생</p>";

                });
        },20);

    });
}
document.addEventListener("DOMContentLoaded", function () {
  initReviewSummaryButtons();  // ✅ 기존 리뷰 요약 버튼 이벤트
  liveSearch("#search-input", "#product-container");  // ✅ 실시간 검색 초기화
});
