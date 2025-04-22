/**
 * TerraFusion component functionality adapted for LevyMaster
 */

document.addEventListener("DOMContentLoaded", function () {
  console.log("TerraFusion JS initialized");

  // Animate all elements with tf-animate-in class
  animateElements();

  // Initialize stat cards
  initStatCards();

  // Initialize notifications
  initNotifications();

  // Set up dashboard cards hover effects
  setupCardHoverEffects();
});

/**
 * Animate elements with the tf-animate-in class
 */
function animateElements() {
  const animatedElements = document.querySelectorAll(".tf-animate-in");

  if (animatedElements.length === 0) return;

  // Create a staggered animation effect
  animatedElements.forEach((element, index) => {
    // Add a slight delay based on the element's index
    setTimeout(() => {
      element.style.opacity = "1";
      element.style.transform = "translateY(0)";
    }, 100 * index);
  });
}

/**
 * Initialize dashboard stat cards
 */
function initStatCards() {
  const statCards = document.querySelectorAll(".tf-stat-card");

  if (statCards.length === 0) return;

  statCards.forEach((card) => {
    // Add animation class if not already present
    if (!card.classList.contains("tf-animate-in")) {
      card.classList.add("tf-animate-in");
    }

    // Add hover effect
    card.addEventListener("mouseenter", () => {
      card.style.transform = "translateY(-5px)";
      card.style.boxShadow = "0 8px 24px rgba(0, 0, 0, 0.15)";
      card.style.borderColor = "var(--tf-primary)";
    });

    card.addEventListener("mouseleave", () => {
      card.style.transform = "";
      card.style.boxShadow = "";
      card.style.borderColor = "";
    });

    // Add progress bar animation if present
    const progressBar = card.querySelector(".tf-progress-bar");
    if (progressBar) {
      const targetWidth = progressBar.getAttribute("data-value") + "%";
      setTimeout(() => {
        progressBar.style.width = targetWidth;
      }, 300);
    }
  });
}

/**
 * Initialize notification toast system
 */
function initNotifications() {
  // Create notification container if it doesn't exist
  let notificationContainer = document.querySelector(
    ".tf-notification-container",
  );

  if (!notificationContainer) {
    notificationContainer = document.createElement("div");
    notificationContainer.className = "tf-notification-container";
    notificationContainer.style.position = "fixed";
    notificationContainer.style.top = "20px";
    notificationContainer.style.right = "20px";
    notificationContainer.style.zIndex = "1000";
    document.body.appendChild(notificationContainer);
  }

  // Add global method to show notifications
  window.showNotification = function (message, type = "info", duration = 5000) {
    const notification = document.createElement("div");
    notification.className = `tf-notification tf-notification-${type} tf-animate-in`;
    notification.style.opacity = "0";
    notification.style.transform = "translateY(20px)";
    notification.style.backgroundColor = "var(--tf-medium-blue)";
    notification.style.color = "var(--tf-text-light)";
    notification.style.borderLeft = "4px solid var(--tf-primary)";
    notification.style.padding = "1rem";
    notification.style.marginBottom = "0.5rem";
    notification.style.borderRadius = "4px";
    notification.style.boxShadow = "0 4px 12px rgba(0, 0, 0, 0.1)";
    notification.style.transition = "all 0.3s ease";
    notification.style.display = "flex";
    notification.style.alignItems = "center";
    notification.style.justifyContent = "space-between";

    const messageElement = document.createElement("div");
    messageElement.textContent = message;

    const closeButton = document.createElement("button");
    closeButton.innerHTML = "&times;";
    closeButton.style.background = "none";
    closeButton.style.border = "none";
    closeButton.style.color = "var(--tf-primary)";
    closeButton.style.fontSize = "1.25rem";
    closeButton.style.cursor = "pointer";
    closeButton.style.marginLeft = "1rem";

    notification.appendChild(messageElement);
    notification.appendChild(closeButton);

    notificationContainer.appendChild(notification);

    // Animate in
    setTimeout(() => {
      notification.style.opacity = "1";
      notification.style.transform = "translateY(0)";
    }, 10);

    // Set up auto-dismiss
    const dismissTimeout = setTimeout(() => {
      dismissNotification(notification);
    }, duration);

    // Set up manual dismiss
    closeButton.addEventListener("click", () => {
      clearTimeout(dismissTimeout);
      dismissNotification(notification);
    });
  };

  function dismissNotification(notification) {
    notification.style.opacity = "0";
    notification.style.transform = "translateY(-20px)";

    setTimeout(() => {
      notification.remove();
    }, 300);
  }
}

/**
 * Add hover effects to dashboard cards
 */
function setupCardHoverEffects() {
  const cards = document.querySelectorAll(".tf-card");

  if (cards.length === 0) return;

  cards.forEach((card) => {
    card.addEventListener("mouseenter", () => {
      card.style.transform = "translateY(-5px)";
      card.style.boxShadow = "0 8px 24px rgba(0, 0, 0, 0.15)";
      card.style.borderColor = "var(--tf-primary)";
    });

    card.addEventListener("mouseleave", () => {
      card.style.transform = "";
      card.style.boxShadow = "";
      card.style.borderColor = "";
    });
  });
}

/**
 * Create and initialize a progress bar
 */
function createProgressBar(container, value, label = null) {
  const progressContainer = document.createElement("div");
  progressContainer.className = "tf-progress-container";

  const progressBar = document.createElement("div");
  progressBar.className = "tf-progress-bar";
  progressBar.setAttribute("data-value", value);
  progressBar.style.width = "0%"; // Start at 0 for animation

  progressContainer.appendChild(progressBar);

  if (label) {
    const labelElement = document.createElement("div");
    labelElement.className = "tf-progress-label";
    labelElement.style.display = "flex";
    labelElement.style.justifyContent = "space-between";
    labelElement.style.fontSize = "0.75rem";
    labelElement.style.color = "var(--tf-primary-70)";
    labelElement.style.marginTop = "0.25rem";

    const labelText = document.createElement("span");
    labelText.textContent = label;

    const valueText = document.createElement("span");
    valueText.textContent = value + "%";

    labelElement.appendChild(labelText);
    labelElement.appendChild(valueText);

    progressContainer.appendChild(labelElement);
  }

  container.appendChild(progressContainer);

  // Animate progress bar
  setTimeout(() => {
    progressBar.style.width = value + "%";
  }, 300);
}

// Export functions for global use
window.tfAnimation = {
  animateElements,
  createProgressBar,
};

window.tfNotification = {
  show: window.showNotification,
};
