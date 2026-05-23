(function() {
    const canvas = document.getElementById('kaleidoscope');
    if (!canvas) return; // Если canvas нет — тихо выходим

    const ctx = canvas.getContext('2d');
    let width, height;
    const segments = 12;
    let time = 0;

    function resize() {
        width = canvas.width = window.innerWidth;
        height = canvas.height = window.innerHeight;
    }
    window.addEventListener('resize', resize);
    resize();

    function draw() {
        time += 0.005;
        const cx = width / 2;
        const cy = height / 2;
        const radius = Math.min(width, height) * 0.45;

        ctx.clearRect(0, 0, width, height);
        ctx.save();
        ctx.translate(cx, cy);

        // Рисуем симметричные лепестки
        for (let i = 0; i < segments; i++) {
            const angle = (i / segments) * Math.PI * 2;
            ctx.save();
            ctx.rotate(angle);
            ctx.scale(1, -1); // отражение для калейдоскопического эффекта

            for (let j = 0; j < 3; j++) {
                const r = radius * (0.4 + 0.25 * Math.sin(time * 2.5 + j));
                const x = Math.cos(time * 0.7 + j) * 65;
                const y = Math.sin(time * 1.1 + j) * 65;
                const hue = (time * 40 + i * 30 + j * 50) % 360;

                // Основной круг
                ctx.beginPath();
                ctx.arc(x, y, r * 0.35, 0, Math.PI * 2);
                ctx.fillStyle = `hsla(${hue}, 80%, 70%, 0.5)`;
                ctx.fill();

                // Дополнительный овал
                ctx.beginPath();
                ctx.ellipse(x * 1.6, y * 0.5, r * 0.28, r * 0.18, time, 0, Math.PI * 2);
                ctx.fillStyle = `hsla(${(hue + 60) % 360}, 70%, 65%, 0.4)`;
                ctx.fill();
            }
            ctx.restore();
        }

        ctx.restore();
        requestAnimationFrame(draw);
    }

    draw();
})();