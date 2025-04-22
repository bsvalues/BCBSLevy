/**
 * Immersive Map Interface for Benton County Tax Districts
 *
 * Interactive 3D map with district visualization, card carousels,
 * and modern UI controls
 */

class ImmersiveMap {
  constructor(options = {}) {
    this.mapElement = document.getElementById(
      options.mapElementId || "map-canvas",
    );
    this.districtsData = options.districtsData || [];
    this.mapOptions = options.mapOptions || {};

    // State variables
    this.activeDistrict = null;
    this.markers = [];
    this.map = null;
    this.carouselInstance = null;
    this.viewMode = "map"; // 'map' or 'cards'

    // Initialize the map
    this.initMap();

    // Initialize UI controls
    this.initControls();

    // Initialize event listeners
    this.initEventListeners();
  }

  /**
   * Initialize the map component
   */
  initMap() {
    // Basic map configuration
    const defaultOptions = {
      center: { lat: 46.2577, lng: -119.2339 }, // Benton County, WA
      zoom: 10,
      styles: this.getMapStyles(),
      mapTypeControl: false,
      streetViewControl: false,
      fullscreenControl: false,
      zoomControlOptions: {
        position: google.maps.ControlPosition.RIGHT_CENTER,
      },
    };

    // Create the map instance
    this.map = new google.maps.Map(this.mapElement, {
      ...defaultOptions,
      ...this.mapOptions,
    });

    // Add district markers when map is ready
    google.maps.event.addListenerOnce(this.map, "idle", () => {
      this.addDistrictMarkers();
    });
  }

  /**
   * Initialize UI controls and panels
   */
  initControls() {
    // Initialize collapsible panels
    document.querySelectorAll(".collapsible-panel").forEach((panel) => {
      const header = panel.querySelector(".panel-header");
      header.addEventListener("click", () => {
        panel.classList.toggle("collapsed");

        // Update icon
        const icon = header.querySelector("i");
        if (icon) {
          icon.classList.toggle("bi-chevron-down");
          icon.classList.toggle("bi-chevron-up");
        }
      });
    });

    // Initialize view toggle
    const mapViewBtn = document.getElementById("map-view-btn");
    const cardViewBtn = document.getElementById("card-view-btn");

    if (mapViewBtn && cardViewBtn) {
      mapViewBtn.addEventListener("click", () => this.switchView("map"));
      cardViewBtn.addEventListener("click", () => this.switchView("cards"));
    }

    // Initialize search functionality
    const searchInput = document.getElementById("district-search");
    if (searchInput) {
      searchInput.addEventListener("input", (e) => {
        this.filterDistricts(e.target.value);
      });
    }

    // Initialize filter chips
    document.querySelectorAll(".filter-chip").forEach((chip) => {
      chip.addEventListener("click", () => {
        chip.classList.toggle("active");
        this.applyFilters();
      });
    });

    // Initialize range sliders
    document
      .querySelectorAll('.range-slider-3d input[type="range"]')
      .forEach((slider) => {
        const valueDisplay =
          slider.parentElement.querySelector(".value-display");

        // Set initial value
        if (valueDisplay) {
          valueDisplay.textContent = slider.value;
        }

        // Update value on change
        slider.addEventListener("input", (e) => {
          if (valueDisplay) {
            valueDisplay.textContent = e.target.value;
          }
          this.applyFilters();
        });
      });

    // Initialize the carousel if it exists
    const carouselElement = document.querySelector(".keras-carousel");
    if (carouselElement) {
      this.carouselInstance = new KerasCarousel(carouselElement, {
        slidesToShow: 3,
        slidesToScroll: 1,
        responsive: [
          {
            breakpoint: 1200,
            settings: { slidesToShow: 2 },
          },
          {
            breakpoint: 768,
            settings: { slidesToShow: 1 },
          },
        ],
        onCardClick: (card, index) => {
          const districtId = card.dataset.districtId;
          if (districtId) {
            this.selectDistrict(districtId);
          }
        },
      });
    }
  }

  /**
   * Initialize event listeners
   */
  initEventListeners() {
    // Resize handler
    window.addEventListener("resize", () => {
      if (this.carouselInstance) {
        this.carouselInstance.refresh();
      }
    });

    // Map interaction events
    if (this.map) {
      // Zoom changed event
      this.map.addListener("zoom_changed", () => {
        this.updateMarkerSize();
      });
    }
  }

  /**
   * Add markers for each district on the map
   */
  addDistrictMarkers() {
    // Clear existing markers
    this.clearMarkers();

    // Add a marker for each district
    this.districtsData.forEach((district, index) => {
      // Skip if no location data
      if (
        !district.location ||
        !district.location.lat ||
        !district.location.lng
      ) {
        return;
      }

      // Create marker element
      const markerElement = document.createElement("div");
      markerElement.className = "map-marker";
      markerElement.textContent = (index + 1).toString();

      // Create advanced marker
      const marker = new google.maps.marker.AdvancedMarkerView({
        position: district.location,
        map: this.map,
        content: markerElement,
        title: district.name,
      });

      // Add click event to marker
      google.maps.MotionTransition.addEventListener(marker, "click", () => {
        this.selectDistrict(district.id);
      });

      // Store marker reference
      this.markers.push({
        marker: marker,
        districtId: district.id,
      });
    });
  }

  /**
   * Clear all markers from the map
   */
  clearMarkers() {
    this.markers.forEach(({ marker }) => {
      marker.map = null;
    });
    this.markers = [];
  }

  /**
   * Select a district by ID
   */
  selectDistrict(districtId) {
    // Find the district data
    const district = this.districtsData.find((d) => d.id == districtId);
    if (!district) return;

    // Set active district
    this.activeDistrict = district;

    // Update markers to highlight selected district
    this.updateMarkerStates();

    // Center map on district
    if (district.location) {
      this.map.panTo(district.location);
      this.map.setZoom(12);
    }

    // Update carousel to show the active district card
    if (this.carouselInstance) {
      const cards = document.querySelectorAll(".keras-card");
      cards.forEach((card, index) => {
        if (card.dataset.districtId == districtId) {
          this.carouselInstance.goToSlide(index);
          card.classList.add("active");
        } else {
          card.classList.remove("active");
        }
      });
    }

    // Trigger custom event
    const event = new CustomEvent("districtSelected", { detail: district });
    document.dispatchEvent(event);
  }

  /**
   * Update marker states based on active district
   */
  updateMarkerStates() {
    this.markers.forEach(({ marker, districtId }) => {
      const content = marker.content;

      if (districtId == this.activeDistrict?.id) {
        content.classList.add("active");
      } else {
        content.classList.remove("active");
      }
    });
  }

  /**
   * Update marker size based on zoom level
   */
  updateMarkerSize() {
    const zoom = this.map.getZoom();
    const scale = Math.min(1.5, Math.max(0.5, zoom / 15));

    this.markers.forEach(({ marker }) => {
      if (marker.content) {
        marker.content.style.transform = `scale(${scale})`;
      }
    });
  }

  /**
   * Filter districts by search query
   */
  filterDistricts(query) {
    if (!query) {
      // Show all districts
      this.markers.forEach(({ marker }) => {
        marker.map = this.map;
      });

      // Reset district cards
      document.querySelectorAll(".keras-card").forEach((card) => {
        card.style.display = "";
      });

      return;
    }

    query = query.toLowerCase();

    // Filter markers on map
    this.markers.forEach(({ marker, districtId }) => {
      const district = this.districtsData.find((d) => d.id == districtId);
      if (!district) return;

      const isMatch =
        district.name.toLowerCase().includes(query) ||
        district.code.toLowerCase().includes(query);

      marker.map = isMatch ? this.map : null;
    });

    // Filter cards in carousel
    document.querySelectorAll(".keras-card").forEach((card) => {
      const districtId = card.dataset.districtId;
      const district = this.districtsData.find((d) => d.id == districtId);
      if (!district) return;

      const isMatch =
        district.name.toLowerCase().includes(query) ||
        district.code.toLowerCase().includes(query);

      card.style.display = isMatch ? "" : "none";
    });

    // Refresh carousel
    if (this.carouselInstance) {
      this.carouselInstance.refresh();
    }
  }

  /**
   * Apply all active filters
   */
  applyFilters() {
    // Get active filter types
    const activeFilters = [];
    document.querySelectorAll(".filter-chip.active").forEach((chip) => {
      activeFilters.push(chip.dataset.filter);
    });

    // Get rate range
    const rateSlider = document.querySelector("#rate-range");
    const maxRate = rateSlider ? parseFloat(rateSlider.value) : 10;

    // Apply filters to markers and cards
    this.markers.forEach(({ marker, districtId }) => {
      const district = this.districtsData.find((d) => d.id == districtId);
      if (!district) return;

      // Check if district type matches active filters
      const typeMatch =
        activeFilters.length === 0 || activeFilters.includes(district.type);

      // Check if rate is within range
      const rateMatch = district.rate <= maxRate;

      // Apply combined filter
      marker.map = typeMatch && rateMatch ? this.map : null;
    });

    // Apply filters to carousel cards
    document.querySelectorAll(".keras-card").forEach((card) => {
      const districtId = card.dataset.districtId;
      const district = this.districtsData.find((d) => d.id == districtId);
      if (!district) return;

      // Check if district type matches active filters
      const typeMatch =
        activeFilters.length === 0 || activeFilters.includes(district.type);

      // Check if rate is within range
      const rateMatch = district.rate <= maxRate;

      // Apply combined filter
      card.style.display = typeMatch && rateMatch ? "" : "none";
    });

    // Refresh carousel
    if (this.carouselInstance) {
      this.carouselInstance.refresh();
    }
  }

  /**
   * Switch between map and card view modes
   */
  switchView(mode) {
    this.viewMode = mode;

    // Update UI
    document
      .getElementById("map-view-btn")
      .classList.toggle("active", mode === "map");
    document
      .getElementById("card-view-btn")
      .classList.toggle("active", mode === "cards");

    const mapContainer = document.querySelector(".immersive-map-container");
    const cardsContainer = document.querySelector(".keras-carousel-container");

    if (mode === "map") {
      mapContainer.style.opacity = "1";
      cardsContainer.classList.remove("full-view");
    } else {
      mapContainer.style.opacity = "0.2";
      cardsContainer.classList.add("full-view");

      // Refresh carousel in card view
      if (this.carouselInstance) {
        this.carouselInstance.refresh();
      }
    }
  }

  /**
   * Get map styles for a sophisticated dark theme
   */
  getMapStyles() {
    return [
      {
        featureType: "all",
        elementType: "labels.text.fill",
        stylers: [{ color: "#ffffff" }],
      },
      {
        featureType: "all",
        elementType: "labels.text.stroke",
        stylers: [{ color: "#000000" }, { lightness: 13 }],
      },
      {
        featureType: "administrative",
        elementType: "geometry.fill",
        stylers: [{ color: "#000000" }],
      },
      {
        featureType: "administrative",
        elementType: "geometry.stroke",
        stylers: [{ color: "#144b53" }, { lightness: 14 }, { weight: 1.4 }],
      },
      {
        featureType: "landscape",
        elementType: "all",
        stylers: [{ color: "#0c2126" }],
      },
      {
        featureType: "poi",
        elementType: "geometry",
        stylers: [{ color: "#0c4152" }, { lightness: 5 }],
      },
      {
        featureType: "road.highway",
        elementType: "geometry.fill",
        stylers: [{ color: "#156a8a" }],
      },
      {
        featureType: "road.highway",
        elementType: "geometry.stroke",
        stylers: [{ color: "#0b434f" }, { lightness: 25 }],
      },
      {
        featureType: "road.arterial",
        elementType: "geometry.fill",
        stylers: [{ color: "#0c3d4a" }],
      },
      {
        featureType: "road.arterial",
        elementType: "geometry.stroke",
        stylers: [{ color: "#0c3d4a" }, { lightness: 16 }],
      },
      {
        featureType: "road.local",
        elementType: "geometry",
        stylers: [{ color: "#0c3d4a" }],
      },
      {
        featureType: "transit",
        elementType: "all",
        stylers: [{ color: "#0c3d4a" }],
      },
      {
        featureType: "water",
        elementType: "all",
        stylers: [{ color: "#00465b" }],
      },
    ];
  }
}

/**
 * District data adapter to format backend data for map interface
 */
class DistrictDataAdapter {
  static formatForMap(districts) {
    return districts.map((district) => {
      return {
        id: district.id,
        name: district.district_name || "Unknown District",
        code: district.district_code || "",
        type: district.district_type || "Other",
        rate: district.levy_rate || 0,
        amount: district.levy_amount || 0,
        year: district.year,
        location: this.getDistrictLocation(district),
        description: district.description || "",
        taxCodes: district.tax_codes || [],
      };
    });
  }

  static getDistrictLocation(district) {
    // If district has explicit coordinates, use them
    if (district.latitude && district.longitude) {
      return {
        lat: parseFloat(district.latitude),
        lng: parseFloat(district.longitude),
      };
    }

    // For demo purposes, generate random coordinates near Benton County
    // In production, these would be actual geocoded locations
    const bentonCountyCenter = { lat: 46.2577, lng: -119.2339 };
    return {
      lat: bentonCountyCenter.lat + (Math.random() * 0.2 - 0.1),
      lng: bentonCountyCenter.lng + (Math.random() * 0.2 - 0.1),
    };
  }
}

/**
 * Initialize the immersive map interface when DOM is loaded
 */
document.addEventListener("DOMContentLoaded", function () {
  // Get district data from the page
  const districtsDataElement = document.getElementById("districts-data");
  let districtsData = [];

  if (districtsDataElement) {
    try {
      const rawData = JSON.parse(districtsDataElement.textContent);
      districtsData = DistrictDataAdapter.formatForMap(rawData);
    } catch (error) {
      console.error("Error parsing districts data:", error);
    }
  }

  // Initialize map if the element exists
  const mapCanvas = document.getElementById("map-canvas");
  if (mapCanvas) {
    // Check if Google Maps API is loaded
    if (typeof google !== "undefined" && google.maps) {
      // Initialize the map
      window.immersiveMap = new ImmersiveMap({
        mapElementId: "map-canvas",
        districtsData: districtsData,
      });
    } else {
      console.error("Google Maps API not loaded");
      // Show error message
      mapCanvas.innerHTML =
        '<div class="alert alert-danger">Google Maps could not be loaded. Please check your internet connection and try again.</div>';
    }
  }

  // Initialize collapsible panels
  document.querySelectorAll(".collapsible-panel").forEach((panel) => {
    const header = panel.querySelector(".panel-header");
    if (header) {
      header.addEventListener("click", () => {
        panel.classList.toggle("collapsed");
      });
    }
  });
});
