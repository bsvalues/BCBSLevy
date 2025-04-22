/**
 * Keras-style Carousel Cards
 *
 * A modern, interactive card carousel with swipe gestures,
 * keyboard navigation, and responsive behavior
 */

class KerasCarousel {
  constructor(container, options = {}) {
    // Main elements
    this.container =
      typeof container === "string"
        ? document.querySelector(container)
        : container;
    if (!this.container) return;

    // Get all required elements
    this.track = this.container.querySelector(".keras-carousel-track");
    this.cards = Array.from(this.track.querySelectorAll(".keras-card"));
    this.dotsContainer = this.container.querySelector(".keras-carousel-dots");

    // Default options
    this.options = {
      slidesToShow: options.slidesToShow || 3,
      slidesToScroll: options.slidesToScroll || 1,
      autoplay: options.autoplay || false,
      autoplaySpeed: options.autoplaySpeed || 3000,
      responsive: options.responsive || [
        {
          breakpoint: 992,
          settings: {
            slidesToShow: 2,
          },
        },
        {
          breakpoint: 576,
          settings: {
            slidesToShow: 1,
          },
        },
      ],
      onCardClick: options.onCardClick || null,
    };

    // State variables
    this.currentIndex = 0;
    this.cardWidth = 0;
    this.cardMargin = 0;
    this.slidesToShow = this.options.slidesToShow;
    this.autoplayInterval = null;
    this.touchStartX = 0;
    this.touchEndX = 0;

    // Initialize the carousel
    this.init();
  }

  init() {
    // Set up initial state
    this.calculateDimensions();
    this.createNavigation();
    this.createDots();
    this.setupEventListeners();
    this.updateCarousel();
    this.handleResponsive();

    // Set up autoplay if enabled
    if (this.options.autoplay) {
      this.startAutoplay();
    }

    // Add a resize observer to handle window size changes
    this.resizeObserver = new ResizeObserver(() => {
      this.handleResponsive();
      this.calculateDimensions();
      this.updateCarousel();
    });
    this.resizeObserver.observe(this.container);

    // Add entrance animation to cards
    this.cards.forEach((card, index) => {
      card.classList.add("keras-card-animated");
      card.style.animationDelay = `${index * 0.1}s`;
    });
  }

  calculateDimensions() {
    if (this.cards.length > 0) {
      const card = this.cards[0];
      const cardStyle = window.getComputedStyle(card);

      this.cardWidth = card.offsetWidth;
      this.cardMargin = parseInt(cardStyle.marginRight, 10);

      // Total width of each card including margin
      this.cardTotalWidth = this.cardWidth + this.cardMargin;
    }
  }

  createNavigation() {
    // Create previous button
    this.prevButton = document.createElement("div");
    this.prevButton.className = "keras-carousel-nav prev";
    this.prevButton.innerHTML = '<i class="bi bi-chevron-left"></i>';
    this.container.appendChild(this.prevButton);

    // Create next button
    this.nextButton = document.createElement("div");
    this.nextButton.className = "keras-carousel-nav next";
    this.nextButton.innerHTML = '<i class="bi bi-chevron-right"></i>';
    this.container.appendChild(this.nextButton);

    // Add click event listeners
    this.prevButton.addEventListener("click", () => this.prevSlide());
    this.nextButton.addEventListener("click", () => this.nextSlide());
  }

  createDots() {
    // Skip if no dots container
    if (!this.dotsContainer) return;

    // Clear existing dots
    this.dotsContainer.innerHTML = "";

    // Calculate how many dots we need
    const totalSlides = this.cards.length - this.slidesToShow + 1;

    // Create dots
    for (let i = 0; i < totalSlides; i++) {
      const dot = document.createElement("div");
      dot.className = "keras-carousel-dot";
      if (i === 0) dot.classList.add("active");

      // Add click handler
      dot.addEventListener("click", () => {
        this.goToSlide(i);
      });

      this.dotsContainer.appendChild(dot);
    }
  }

  setupEventListeners() {
    // Set up card click handlers
    this.cards.forEach((card, index) => {
      card.addEventListener("click", (e) => {
        if (typeof this.options.onCardClick === "function") {
          this.options.onCardClick(card, index, e);
        }
      });
    });

    // Add keyboard navigation
    document.addEventListener("keydown", (e) => {
      // Only handle events when the carousel is in the viewport
      const rect = this.container.getBoundingClientRect();
      const isInViewport = rect.top < window.innerHeight && rect.bottom > 0;

      if (isInViewport) {
        if (e.key === "ArrowLeft") {
          this.prevSlide();
        } else if (e.key === "ArrowRight") {
          this.nextSlide();
        }
      }
    });

    // Add touch support for mobile
    this.track.addEventListener(
      "touchstart",
      (e) => {
        this.touchStartX = e.changedTouches[0].screenX;
      },
      { passive: true },
    );

    this.track.addEventListener(
      "touchend",
      (e) => {
        this.touchEndX = e.changedTouches[0].screenX;
        this.handleTouchEnd();
      },
      { passive: true },
    );
  }

  handleTouchEnd() {
    // Calculate the swipe distance
    const swipeDistance = this.touchEndX - this.touchStartX;

    // Detect the swipe direction and navigate if significant swipe detected
    if (swipeDistance > 50) {
      // Swipe right (move to previous)
      this.prevSlide();
    } else if (swipeDistance < -50) {
      // Swipe left (move to next)
      this.nextSlide();
    }
  }

  startAutoplay() {
    // Clear any existing interval
    this.stopAutoplay();

    // Start a new interval
    this.autoplayInterval = setInterval(() => {
      this.nextSlide();
    }, this.options.autoplaySpeed);
  }

  stopAutoplay() {
    if (this.autoplayInterval) {
      clearInterval(this.autoplayInterval);
      this.autoplayInterval = null;
    }
  }

  updateCarousel() {
    // Calculate the transform value
    const translateX = -(this.currentIndex * this.cardTotalWidth);

    // Apply the transform to the track
    this.track.style.transform = `translateX(${translateX}px)`;

    // Update active dot
    if (this.dotsContainer) {
      const dots = this.dotsContainer.querySelectorAll(".keras-carousel-dot");
      dots.forEach((dot, index) => {
        dot.classList.toggle("active", index === this.currentIndex);
      });
    }

    // Update button states (disable prev/next if at the beginning/end)
    this.prevButton.classList.toggle("disabled", this.currentIndex === 0);
    this.nextButton.classList.toggle(
      "disabled",
      this.currentIndex >= this.cards.length - this.slidesToShow,
    );
  }

  prevSlide() {
    // Move to previous slide if possible
    if (this.currentIndex > 0) {
      this.currentIndex -= this.options.slidesToScroll;

      // Don't go past the first slide
      if (this.currentIndex < 0) {
        this.currentIndex = 0;
      }

      this.updateCarousel();
    }
  }

  nextSlide() {
    // Move to next slide if possible
    if (this.currentIndex < this.cards.length - this.slidesToShow) {
      this.currentIndex += this.options.slidesToScroll;

      // Don't go past the last visible slide
      if (this.currentIndex > this.cards.length - this.slidesToShow) {
        this.currentIndex = this.cards.length - this.slidesToShow;
      }

      this.updateCarousel();
    }
  }

  goToSlide(index) {
    // Go to a specific slide index
    if (index >= 0 && index <= this.cards.length - this.slidesToShow) {
      this.currentIndex = index;
      this.updateCarousel();
    }
  }

  handleResponsive() {
    // Get the current window width
    const windowWidth = window.innerWidth;

    // Default to the original settings
    this.slidesToShow = this.options.slidesToShow;

    // Check responsive breakpoints
    if (this.options.responsive) {
      // Sort responsive settings by breakpoint in descending order
      const sortedResponsive = [...this.options.responsive].sort(
        (a, b) => b.breakpoint - a.breakpoint,
      );

      // Find the first matching breakpoint
      for (const item of sortedResponsive) {
        if (windowWidth <= item.breakpoint) {
          this.slidesToShow = item.settings.slidesToShow;
        }
      }
    }

    // Update dots after the responsive changes
    this.createDots();
  }

  // Public methods for external control
  refresh() {
    this.calculateDimensions();
    this.createDots();
    this.updateCarousel();
  }

  destroy() {
    // Clean up event listeners
    this.prevButton.remove();
    this.nextButton.remove();

    if (this.resizeObserver) {
      this.resizeObserver.disconnect();
    }

    this.stopAutoplay();
  }
}

// Initialize all keras carousels on the page
document.addEventListener("DOMContentLoaded", function () {
  // Find all carousel containers
  const carousels = document.querySelectorAll(".keras-carousel");

  // Initialize each carousel
  carousels.forEach((carousel) => {
    // Get custom options if specified in data attributes
    const options = {
      slidesToShow: parseInt(carousel.dataset.slidesToShow || 3, 10),
      slidesToScroll: parseInt(carousel.dataset.slidesToScroll || 1, 10),
      autoplay: carousel.dataset.autoplay === "true",
      autoplaySpeed: parseInt(carousel.dataset.autoplaySpeed || 3000, 10),
    };

    // Create the carousel instance
    new KerasCarousel(carousel, options);
  });
});
