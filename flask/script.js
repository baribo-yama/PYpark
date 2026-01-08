class Carousel3D {
    constructor() {
        this.carousel = document.querySelector('.carousel');
        this.carouselItems = this.carousel.querySelectorAll('.carousel__item');
        this.rotation = 0;
        this.angle = 360 / this.carouselItems.length;

        this.init();
    }

    init() {
        this.setUp();
        this.clickHandler();
        this.addPointerDragSupport();
    }

    setUp() {
        const scene = document.querySelector('.scene');
        const sceneSize = scene.clientWidth;
        const tz = sceneSize / 2 / Math.tan(Math.PI * this.angle / 180 / 2);

        scene.style.perspective = `${tz * 2}px`;

        this.carouselItems.forEach((item, i) => {
            item.style.setProperty('--hue', `${i * this.angle}deg`);
            item.style.setProperty('--rotateY', `${i * this.angle}deg`);
            item.style.setProperty('--tz', `${tz}px`);
        });
    }

    clickHandler() {
        const prevBtn = document.querySelector('.carousel__prev');
        const nextBtn = document.querySelector('.carousel__next');

        prevBtn.addEventListener('click', () => {
            this.rotation += this.angle;
            this.carousel.style.setProperty('--rotateY', `${this.rotation}deg`);
        });

        nextBtn.addEventListener('click', () => {
            this.rotation -= this.angle;
            this.carousel.style.setProperty('--rotateY', `${this.rotation}deg`);
        });
    }

    addPointerDragSupport() {
        const scene = document.querySelector('.scene');
        let isDragging = false;
        let startX = 0;
        let lastX = 0;
        let lastTime = 0;
        let velocity = 0;
        let animationFrameId = null;

        const onDragStart = (x) => {
            isDragging = true;
            startX = x;
            lastX = x;
            lastTime = performance.now();
            velocity = 0;
            this.carousel.style.transition = "none";

            if (animationFrameId) {
                cancelAnimationFrame(animationFrameId);
                animationFrameId = null;
            }
        };

        const onDragMove = (x) => {
            if (!isDragging) return;

            const now = performance.now();
            const delta = x - lastX;
            const dt = now - lastTime;

            // 回転
            this.rotation += delta * 0.3;
            this.carousel.style.setProperty('--rotateY', `${this.rotation}deg`);

            // 速度計算
            velocity = (delta / dt) * 16; // 16ms基準でスケーリング
            lastX = x;
            lastTime = now;
        };

        const onDragEnd = () => {
            if (!isDragging) return;
            isDragging = false;

            const decay = 0.95; // 慣性減衰率
            const step = () => {
                velocity *= decay;
                if (Math.abs(velocity) < 0.1) {
                    cancelAnimationFrame(animationFrameId);
                    animationFrameId = null;
                    this.carousel.style.transition = "transform 1s"; // 最後に滑らかに戻す
                    return;
                }
                this.rotation += velocity;
                this.carousel.style.setProperty('--rotateY', `${this.rotation}deg`);
                animationFrameId = requestAnimationFrame(step);
            };

            animationFrameId = requestAnimationFrame(step);
        };

        // --------------------------
        // Pointer Events（マウス + タッチ）
        // --------------------------
        scene.addEventListener("pointerdown", (e) => {
            if (e.pointerType === "touch" || e.pointerType === "mouse") {
                e.preventDefault();
                onDragStart(e.clientX);
            }
        }, { passive: false });

        scene.addEventListener("pointermove", (e) => {
            if (!isDragging) return;
            if (e.pointerType === "touch" || e.pointerType === "mouse") {
                e.preventDefault();
                onDragMove(e.clientX);
            }
        }, { passive: false });

        scene.addEventListener("pointerup", onDragEnd);
        scene.addEventListener("pointercancel", onDragEnd);
        scene.addEventListener("pointerleave", onDragEnd);

        item.addEventListener('click', () => {
            if (!this.isDragging) {
                window.location.href = urls[index];
            }
        });
    }
}

function updateTime() {
    const now = new Date();

    // 時刻
    const hours = now.getHours().toString().padStart(2, '0');
    const minutes = now.getMinutes().toString().padStart(2, '0');
    const seconds = now.getSeconds().toString().padStart(2, '0');
    document.getElementById("clock").textContent = `${hours}:${minutes}:${seconds}`;

    // 日付
    const year = now.getFullYear();
    const month = (now.getMonth() + 1).toString().padStart(2, '0');
    const day = now.getDate().toString().padStart(2, '0');
    const week = ["日", "月", "火", "水", "木", "金", "土"][now.getDay()];
    document.getElementById("date").textContent = `${year}年${month}月${day}日（${week}）`;
}

// 1秒ごとに更新
setInterval(updateTime, 1000);

// 初回実行
updateTime();


new Carousel3D();
