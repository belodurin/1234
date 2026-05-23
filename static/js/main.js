(function() {
    // Живые часы
    function updateClock() {
        const now = new Date();
        const options = {
            hour: '2-digit', minute: '2-digit', second: '2-digit',
            day: 'numeric', month: 'long', weekday: 'long'
        };
        document.getElementById('clock').textContent = now.toLocaleString('ru-RU', options);
    }
    updateClock();
    setInterval(updateClock, 1000);

    // Реальный онлайн (запрос к /api/online)
    async function updateOnline() {
        try {
            const resp = await fetch('/api/online');
            const data = await resp.json();
            document.getElementById('online-count').textContent = data.online;
        } catch (e) {
            document.getElementById('online-count').textContent = '...';
        }
    }
    updateOnline();
    setInterval(updateOnline, 10000); // обновляем каждые 10 секунд

    // Обратный отсчёт до запуска (30 дней от текущей даты)
    const launchDate = new Date();
    launchDate.setDate(launchDate.getDate() + 30);
    launchDate.setHours(0, 0, 0, 0);

    function updateCountdown() {
        const now = new Date();
        const diff = launchDate - now;
        if (diff <= 0) {
            document.querySelector('.countdown').innerHTML =
                '<p style="font-size:2rem">Мы запустились! 🎉</p>';
            return;
        }
        const days = Math.floor(diff / (1000 * 60 * 60 * 24));
        const hours = Math.floor((diff / (1000 * 60 * 60)) % 24);
        const minutes = Math.floor((diff / (1000 * 60)) % 60);
        const seconds = Math.floor((diff / 1000) % 60);

        document.getElementById('days').textContent = days;
        document.getElementById('hours').textContent = String(hours).padStart(2, '0');
        document.getElementById('minutes').textContent = String(minutes).padStart(2, '0');
        document.getElementById('seconds').textContent = String(seconds).padStart(2, '0');
    }
    updateCountdown();
    setInterval(updateCountdown, 1000);

    // Отправка формы подписки (пока заглушка)
    document.querySelector('.subscribe-form').addEventListener('submit', function(e) {
        e.preventDefault();
        const email = this.querySelector('input').value;
        alert(`Спасибо! Мы запомнили ${email} и сообщим о старте.`);
        this.reset();
    });
})();