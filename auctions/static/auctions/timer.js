

//function formatTime(time) {
//  let hours = Math.floor(time / 3600);
//  let minutes = Math.floor((time % 3600) / 60);
//  let seconds = time % 60;
//
//  return `${String(hours).padStart(2, '0')}:${String(minutes).padStart(2, '0')}:${String(seconds).padStart(2, '0')}`;
//}
//
//// Функция для обратного отсчета и обновления таймера
//function startTimer(endTime) {
//  const timerElement = document.getElementById('timer');
//
//  function updateTimer() {
//    const now = Math.floor(Date.now() / 1000);
//    console.log(now);
//    const timeRemaining = Math.max(0, endTime - now);
//    timerElement.textContent = formatTime(timeRemaining);
//
//    if (timeRemaining === 0) {
//      clearInterval(timerInterval);
//      alert("Время вышло!");
//    }
//  }
//
//  // Обновляем таймер каждую секунду
//  updateTimer();
//  const timerInterval = setInterval(updateTimer, 1000);
//}
