// Load and display districts on the map
function loadDistricts() {
  // Clear existing markers and polygons
  clearMapFeatures();

  if (!districtData || districtData.length === 0) {
    displayErrorMessage("No district data available to display");
    return;
  }

  // Create markers and polygons for each district
  districtData.forEach((district, index) => {
    // Generate coordinates since we don't have real ones in the demo
    const coordinates = generateRandomCoordinates(index);
    district.latitude = coordinates.lat;
    district.longitude = coordinates.lng;

    // Apply filters before creating map features
    if (shouldDisplayDistrict(district)) {
      // Create marker
      createDistrictMarker(district, coordinates);

      // Create district boundary polygon
      const polygonCoords = generateDistrictPolygon(
        coordinates,
        district.district_type,
      );
      createDistrictPolygon(district, polygonCoords);
    }
  });

  // Update the displayed count
  updateDistrictCount();
}

// Check if a district should be displayed based on current filters
function shouldDisplayDistrict(district) {
  // If no filters are active, show all districts
  if (filterSettings.districtTypes.length === 0) {
    return true;
  }

  // Otherwise, check if the district type is in the active filters
  return filterSettings.districtTypes.includes(district.district_type);
}

// Update the display count based on visible districts
function updateDistrictCount() {
  const countElement = document.getElementById("displayed-district-count");
  if (countElement) {
    countElement.textContent = districtMarkers.length;
  }

  const totalElement = document.getElementById("total-district-count");
  if (totalElement) {
    totalElement.textContent = districtData.length;
  }
}

// Apply filters to the map
function applyFilters() {
  // Get selected district types
  filterSettings.districtTypes = [];
  document.querySelectorAll(".filter-badge:not(.inactive)").forEach((badge) => {
    const type = badge.getAttribute("data-type");
    if (type) {
      filterSettings.districtTypes.push(type);
    }
  });

  // Reload the districts with filters applied
  loadDistricts();
}

// Setup filter listeners
function setupFilterListeners() {
  // Add click handler for filter badges
  document.querySelectorAll(".filter-badge").forEach((badge) => {
    badge.addEventListener("click", function () {
      // Toggle active/inactive state
      this.classList.toggle("inactive");

      // Apply filters
      applyFilters();
    });
  });

  // Reset filters button
  const resetButton = document.getElementById("resetFilters");
  if (resetButton) {
    resetButton.addEventListener("click", function () {
      // Reset all filters to active
      document.querySelectorAll(".filter-badge").forEach((badge) => {
        badge.classList.remove("inactive");
      });

      // Clear filter settings
      filterSettings.districtTypes = [];

      // Reload districts
      loadDistricts();
    });
  }
}

// Setup UI interactions for the map
function setupUIInteractions() {
  // Map control buttons
  const zoomInBtn = document.getElementById("zoomInBtn");
  const zoomOutBtn = document.getElementById("zoomOutBtn");
  const resetMapBtn = document.getElementById("resetMapBtn");

  if (zoomInBtn) {
    zoomInBtn.addEventListener("click", function () {
      map.setZoom(map.getZoom() + 1);
    });
  }

  if (zoomOutBtn) {
    zoomOutBtn.addEventListener("click", function () {
      map.setZoom(map.getZoom() - 1);
    });
  }

  if (resetMapBtn) {
    resetMapBtn.addEventListener("click", function () {
      map.setCenter({ lat: 46.25, lng: -119.3 });
      map.setZoom(10);
    });
  }

  // Carousel toggle
  const carouselToggle = document.getElementById("carouselToggle");
  const districtCarousel = document.getElementById("districtCarousel");

  if (carouselToggle && districtCarousel) {
    carouselToggle.addEventListener("click", function () {
      districtCarousel.classList.toggle("expanded");
      carouselToggle.classList.toggle("expanded");

      if (districtCarousel.classList.contains("expanded")) {
        carouselToggle.textContent = "Collapse Cards";
      } else {
        carouselToggle.textContent = "Expand Cards";
      }
    });
  }

  // Info panel close button (dynamically added)
  document.addEventListener("click", function (e) {
    if (e.target.closest(".info-close-btn")) {
      const infoPanel = document.getElementById("districtInfoPanel");
      if (infoPanel) {
        infoPanel.classList.remove("active");
      }
    }
  });
}

// Cycle through animation effects for markers
function cycleMarkerAnimations() {
  const animationTypes = [
    "pulse-effect",
    "glow-effect",
    "bounce-effect",
    "spin-effect",
  ];
  let currentIndex = 0;

  // Every minute, cycle the animation effects
  setInterval(() => {
    currentIndex = (currentIndex + 1) % animationTypes.length;

    // Update all markers
    districtMarkers.forEach((markerObj) => {
      if (markerObj.overlay && markerObj.overlay.div_) {
        // Get the current animation
        const currentAnimation = markerObj.overlay.div_.getAttribute(
          "data-animation-type",
        );

        // Remove current animation class
        if (currentAnimation) {
          markerObj.overlay.div_.classList.remove(currentAnimation);
        }

        // Apply new animation based on district type or cyclically
        let newAnimation;
        const districtType = markerObj.district.district_type;

        if (districtType === "SCHOOL") {
          newAnimation = animationTypes[currentIndex];
        } else if (districtType === "CITY") {
          newAnimation = animationTypes[(currentIndex + 1) % 4];
        } else if (districtType === "FIRE") {
          newAnimation = animationTypes[(currentIndex + 2) % 4];
        } else if (districtType === "COUNTY") {
          newAnimation = animationTypes[(currentIndex + 3) % 4];
        } else {
          // Random for other types
          newAnimation =
            animationTypes[Math.floor(Math.random() * animationTypes.length)];
        }

        // Apply new animation class
        markerObj.overlay.div_.classList.add(newAnimation);
        markerObj.overlay.div_.setAttribute(
          "data-animation-type",
          newAnimation,
        );
      }
    });
  }, 60000); // Cycle every 60 seconds
}
