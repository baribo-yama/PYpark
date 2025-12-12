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
}

new Carousel3D();