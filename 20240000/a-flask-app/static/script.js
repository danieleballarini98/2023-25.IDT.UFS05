document.addEventListener('DOMContentLoaded', () => {
    const sections = document.querySelectorAll('.section');
    let currentImageIndex = 0;

    const observer = new IntersectionObserver(entries => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                entry.target.classList.add('active');
                observer.unobserve(entry.target);
            }
        });
    }, {
        threshold: 0.1
    });

    sections.forEach(section => {
        observer.observe(section);
    });

    const changeBackgroundImage = () => {
        currentImageIndex = (currentImageIndex + 1) % images.length;
        document.body.style.backgroundImage = `url(${images[currentImageIndex]})`;
    };

    setInterval(changeBackgroundImage, 5000); // Cambia immagine ogni 5 secondi
});