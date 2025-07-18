function uptBySelID(selectId, buttonId) { // 동적 버튼 id 할당
        const select = document.getElementById(selectId);
        const button = document.getElementById(buttonId);

        function updateButtonDataset() {
            button.dataset.productId = select.value;
        }

        // 초기화
        updateButtonDataset();

        // select 변경 시 dataset 갱신
        select.addEventListener("change", updateButtonDataset);
}
function showLoadingSpinner(show = true) {
  const spinner = document.getElementById("loadingSpinner");
  spinner.style.display = show ? "block" : "none";
}
function get_sentiment(){
    const btn = document.getElementById("analyze");

    btn.addEventListener("click" ,function(){
        const pr_id = this.dataset.productId;
        if (!pr_id) {
            alert("제품을 선택해주세요.");
            return;
        }

        showLoadingSpinner(true);
        fetch(`api/admins/${pr_id}/get_sent`)
            .then(resp => resp.json())
            .then(data => {
                showLoadingSpinner(false);
                if(data.sentiment_ratio){
                    renderSentimentPieChart(data.sentiment_ratio,pr_id);
                    
                }else{
                    alert(data.msg);
                    init_sentiment(pr_id);
                }
            })
            .catch(err => {
                console.log("에러 발생",err);
            })

    })
}

function init_sentiment(pr_id){
    showLoadingSpinner(true);
    fetch(`api/admins/${pr_id}/sent_ratio`)
        .then(resp => resp.json())
        .then(data => {
            showLoadingSpinner(false);
            if(data.sentiment_ratio){
                console.log(data.sentiment_ratio);
                renderSentimentPieChart(data.sentiment_ratio,pr_id);
            }
            
        })
        .catch(err => {
            console.log("분석 실패 ",err)
        })
}



let sentimentChart = null;

function renderSentimentPieChart(ratioData,pr_id) {
  FetchReviewTrend(pr_id); 
  const ctx = document.getElementById("myPieChart").getContext("2d");

  const labels = Object.keys(ratioData);
  const data = Object.values(ratioData);

  if (sentimentChart) {
    sentimentChart.destroy();
  }

  sentimentChart = new Chart(ctx, {
    type: "pie",
    data: {
      labels: labels,
      datasets: [{
        label: "감성 비율",
        data: data,
        backgroundColor: [
          "rgba(75, 192, 192, 0.6)",  // 긍정
          "rgba(255, 205, 86, 0.6)",  // 애매
          "rgba(255, 99, 132, 0.6)"   // 부정
        ],
        borderWidth: 1
      }]
    },
    options: {
      responsive: true,
      plugins: {
        legend: {
          position: "bottom"
        },
        tooltip: {
          callbacks: {
            label: function (context) {
              return `${context.label}: ${context.parsed}%`;
            }
          }
        }
      }
    }
  });
}




function FetchReviewTrend(pr_id){
    showLoadingSpinner(true)
    fetch(`api/admins/${pr_id}/get_trend`)
        .then(resp =>  resp.json())
        .then(data => { if (data.trend){renderReviewTrend(data.trend); showLoadingSpinner(false)}} )
        .catch(err => {
            console.log("실패" ,err)
        })
}
let trendChart = null;
function renderReviewTrend(trendData){
    const ctx = document.getElementById("reviewTrendChart").getContext("2d");

    const labels = Object.keys(trendData);        // 날짜
    const data = Object.values(trendData);        // 리뷰 수

    if (trendChart) {
        trendChart.destroy(); // 기존 차트 제거
    }

    trendChart = new Chart(ctx, {
        type: "line",
        data: {
        labels: labels,
        datasets: [{
            label: "리뷰 수",
            data: data,
            fill: false,
            borderColor: "rgba(75, 192, 192, 1)",
            tension: 0.1
        }]
        },
        options: {
        responsive: true,
        plugins: {
            legend: {
            display: true
            },
            tooltip: {
            callbacks: {
                label: function(context) {
                return `${context.parsed.y}건`;
                }
            }
            }
        },
        scales: {
            x: {
            title: {
                display: true,
                text: "날짜"
            }
            },
            y: {
            title: {
                display: true,
                text: "리뷰 수"
            },
            beginAtZero: true,
            precision: 0
            }
        }
        }
    });
    
}


document.addEventListener("DOMContentLoaded", function(){
    uptBySelID("productSelect", "analyze");
    
    get_sentiment();
});
