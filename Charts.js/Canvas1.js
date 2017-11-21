//For making the chart
new Chart(document.getElementById("doughnut-chart"), {
    type: 'doughnut',
    data: {
      labels: ["Enjoyment", "Anger", "Disgust", "Sadness", "Fear", "Neutral"],
      datasets: [
        {
          label: "Emotions",
          backgroundColor: ["#3e95cd", "#8e5ea2", "#3cba9f", "#e8c3b9", "#c45850", "#989898"],
          data: [11.2, 25.3, 22.8, 11.4, 20, 9.7]
        }
      ]
    },
    options: {
      title: {
        display: true,
        text: 'Emotions'
       
      }
    }
});