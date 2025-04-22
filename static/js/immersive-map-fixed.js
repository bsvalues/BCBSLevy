// Immersive Map Interactive Visualization
// This file is part of the Levy Calculation System
//
// Enhanced, immersive map interface for visualizing tax districts
// with interactive elements and animations.

// Global variables
let map;
let districtMarkers = [];
let districtPolygons = [];
let activeInfoWindow = null;
let districtData = [];
let filterSettings = {
  districtTypes: [],
};

// Initialize map when the page loads
document.addEventListener("DOMContentLoaded", function () {
  const mapContainer = document.getElementById("map-container");
  const districtsJson = document.getElementById("districts-data");

  if (mapContainer && districtsJson) {
    // Parse district data
    try {
      districtData = JSON.parse(districtsJson.textContent);
      initMap();
    } catch (e) {
      console.error("Error parsing district data:", e);
      displayErrorMessage(
        "Could not load district data. Please try again later.",
      );
    }
  }

  // Initialize filter listeners
  setupFilterListeners();
});

// Initialize Google Map with district data
function initMap() {
  // Check if Google Maps API is loaded
  if (!window.google || !window.google.maps) {
    console.error("Google Maps API not loaded");
    displayErrorMessage(
      "Map service is currently unavailable. Please try again later.",
    );
    return;
  }

  // Create the map centered on Benton County
  map = new google.maps.Map(document.getElementById("map-container"), {
    center: { lat: 46.25, lng: -119.3 }, // Benton County
    zoom: 10,
    styles: getMapStyles(),
    mapTypeControl: true,
    mapTypeControlOptions: {
      style: google.maps.MapTypeControlStyle.DROPDOWN_MENU,
      position: google.maps.ControlPosition.TOP_RIGHT,
    },
    zoomControl: true,
    zoomControlOptions: {
      position: google.maps.ControlPosition.RIGHT_CENTER,
    },
    streetViewControl: false,
    fullscreenControl: true,
    fullscreenControlOptions: {
      position: google.maps.ControlPosition.RIGHT_TOP,
    },
  });

  // Create custom controls
  addCustomControls();

  // Load district markers and polygons
  loadDistricts();

  // Set up UI interactions (filters, buttons, etc.)
  setupUIInteractions();

  // Start animation cycling
  cycleMarkerAnimations();
}

// Generate random coordinates within Benton County area
// This is a demo function - in a real app, you would get actual coordinates from database
function generateRandomCoordinates(index) {
  // Benton County approximate bounds
  const minLat = 46.0;
  const maxLat = 46.5;
  const minLng = -119.6;
  const maxLng = -119.0;

  // Use the index to distribute points more evenly
  const lat = minLat + (maxLat - minLat) * (0.2 + 0.6 * Math.sin(index * 0.5));
  const lng = minLng + (maxLng - minLng) * (0.2 + 0.6 * Math.cos(index * 0.5));

  return { lat, lng };
}

// Generate polygon coordinates for a district
function generateDistrictPolygon(center, districtType) {
  const points = [];
  const radius = 0.03 + Math.random() * 0.05; // Random radius between 0.03 and 0.08 degrees
  const edges =
    districtType === "CITY"
      ? 6
      : districtType === "SCHOOL"
        ? 5
        : districtType === "FIRE"
          ? 4
          : Math.floor(Math.random() * 4) + 4; // 4-7 edges for other types

  for (let i = 0; i < edges; i++) {
    const angle = (i / edges) * (2 * Math.PI);
    // Add some randomness to make the shape irregular
    const randomRadius = radius * (0.8 + Math.random() * 0.4);
    const point = {
      lat: center.lat + Math.sin(angle) * randomRadius,
      lng: center.lng + Math.cos(angle) * randomRadius,
    };
    points.push(point);
  }

  return points;
}

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

// Create a marker for a district
function createDistrictMarker(district, position) {
  const districtType = district.district_type || "OTHER";

  // Create marker
  const marker = new google.maps.Marker({
    position: position,
    map: map,
    title: district.district_name,
    icon: {
      path: google.maps.SymbolPath.CIRCLE,
      scale: 0,
      fillColor: "transparent",
      fillOpacity: 0,
      strokeWeight: 0,
    },
    optimized: false,
    zIndex: 10,
  });

  // Add custom HTML overlay for marker
  const markerOverlay = new google.maps.OverlayView();
  markerOverlay.draw = function () {
    if (!this.div_) {
      this.div_ = document.createElement("div");

      // Decide on animation effect based on district type or random selection
      let animationEffect = "";
      const effectTypes = [
        "pulse-effect",
        "glow-effect",
        "bounce-effect",
        "spin-effect",
      ];

      // Assign animation effect based on district type for a consistent experience
      switch (districtType) {
        case "SCHOOL":
          animationEffect = "pulse-effect";
          break;
        case "CITY":
          animationEffect = "glow-effect";
          break;
        case "FIRE":
          animationEffect = "bounce-effect";
          break;
        case "COUNTY":
          animationEffect = "spin-effect";
          break;
        default:
          // Random effect for other district types
          animationEffect =
            effectTypes[Math.floor(Math.random() * effectTypes.length)];
      }

      // Apply classes including the animation effect
      this.div_.className = `district-marker marker-${districtType} ${animationEffect}`;
      this.div_.innerHTML = district.district_code || districtType.charAt(0);
      this.div_.title = district.district_name;
      this.div_.setAttribute("data-district-id", district.id);
      this.div_.setAttribute("data-animation-type", animationEffect);

      // Append to the overlay's panes
      const panes = this.getPanes();
      panes.overlayImage.appendChild(this.div_);
    }

    // Position the div on the marker
    const point = this.getProjection().fromLatLngToDivPixel(
      marker.getPosition(),
    );
    if (point) {
      this.div_.style.left = point.x - 20 + "px";
      this.div_.style.top = point.y - 20 + "px";
    }
  };

  // Add to map and store in array
  markerOverlay.setMap(map);
  districtMarkers.push({ marker, overlay: markerOverlay, district });

  // Add click event to marker
  marker.addListener("click", function () {
    // Add ripple animation to marker on click
    if (markerOverlay.div_) {
      markerOverlay.div_.classList.add("ripple-animation");

      // Remove animation class after it completes
      setTimeout(() => {
        if (markerOverlay.div_) {
          markerOverlay.div_.classList.remove("ripple-animation");
        }
      }, 1000);
    }

    showDistrictInfo(district);
  });
}

// Create a polygon for a district boundary
function createDistrictPolygon(district, coordinates) {
  const districtType = district.district_type || "OTHER";

  // Determine color based on district type
  let fillColor, strokeColor;
  switch (districtType) {
    case "SCHOOL":
      fillColor = "#E57373";
      strokeColor = "#D32F2F";
      break;
    case "CITY":
      fillColor = "#64B5F6";
      strokeColor = "#1976D2";
      break;
    case "FIRE":
      fillColor = "#FFB74D";
      strokeColor = "#EF6C00";
      break;
    case "COUNTY":
      fillColor = "#81C784";
      strokeColor = "#388E3C";
      break;
    default:
      fillColor = "#9575CD";
      strokeColor = "#5E35B1";
  }

  // Create polygon
  const polygon = new google.maps.Polygon({
    paths: coordinates,
    strokeColor: strokeColor,
    strokeOpacity: 0.8,
    strokeWeight: 2,
    fillColor: fillColor,
    fillOpacity: 0.15,
    map: map,
    zIndex: 5,
  });

  // Store polygon reference
  districtPolygons.push({ polygon, district });

  // Add hover effect
  polygon.addListener("mouseover", function () {
    this.setOptions({
      fillOpacity: 0.4,
      strokeWeight: 3,
    });
  });

  polygon.addListener("mouseout", function () {
    this.setOptions({
      fillOpacity: 0.15,
      strokeWeight: 2,
    });
  });

  // Add click handler
  polygon.addListener("click", function () {
    showDistrictInfo(district);
  });
}

// Show district information in the sidebar
function showDistrictInfo(district) {
  const infoPanel = document.getElementById("district-info-panel");

  if (!infoPanel) {
    console.error("District info panel not found");
    return;
  }

  // Update panel with district info
  infoPanel.innerHTML = `
        <div class="district-info-card">
            <h3>${district.district_name}</h3>
            <div class="district-type-badge badge-${district.district_type || "OTHER"}">${district.district_type || "Unknown Type"}</div>
            <div class="district-details">
                <p><strong>District Code:</strong> ${district.district_code || "N/A"}</p>
                <p><strong>Levy Rate:</strong> ${district.levy_rate ? district.levy_rate.toFixed(3) : "N/A"}</p>
                <p><strong>Levy Amount:</strong> ${district.levy_amount ? "$" + district.levy_amount.toLocaleString() : "N/A"}</p>
                <p><strong>Year:</strong> ${district.year || "N/A"}</p>
            </div>
            <div class="district-action-buttons">
                <a href="/public/district/${district.id}" class="btn btn-sm btn-primary">View Details</a>
                <button class="btn btn-sm btn-outline-secondary zoom-to-district" data-district-id="${district.id}">Zoom To</button>
            </div>
        </div>
    `;

  // Show the panel
  infoPanel.classList.add("active");

  // Add event listener to zoom button
  const zoomBtn = infoPanel.querySelector(".zoom-to-district");
  if (zoomBtn) {
    zoomBtn.addEventListener("click", function () {
      zoomToDistrict(district.id);
    });
  }

  // Add close button
  const closeBtn = document.createElement("button");
  closeBtn.className = "close-info-panel btn btn-sm btn-link";
  closeBtn.innerHTML = '<i class="bi bi-x-lg"></i>';
  closeBtn.addEventListener("click", function () {
    infoPanel.classList.remove("active");
  });
  infoPanel.appendChild(closeBtn);
}

// Zoom to a specific district
function zoomToDistrict(districtId) {
  const marker = districtMarkers.find((m) => m.district.id === districtId);

  if (marker && marker.marker) {
    map.setZoom(13);
    map.setCenter(marker.marker.getPosition());
  }
}

// Clear all markers and polygons from the map
function clearMapFeatures() {
  // Clear markers
  districtMarkers.forEach((marker) => {
    marker.marker.setMap(null);
    marker.overlay.setMap(null);
  });
  districtMarkers = [];

  // Clear polygons
  districtPolygons.forEach((polyObj) => {
    polyObj.polygon.setMap(null);
  });
  districtPolygons = [];
}

// Add custom controls to the map
function addCustomControls() {
  // Filter control
  const filterControl = document.createElement("div");
  filterControl.className = "map-control filter-control card-3d";
  filterControl.innerHTML = `
        <button id="toggle-filter-panel" class="btn btn-sm btn-light">
            <i class="bi bi-funnel-fill"></i> Filters
        </button>
    `;
  map.controls[google.maps.ControlPosition.TOP_LEFT].push(filterControl);

  // Legend control
  const legendControl = document.createElement("div");
  legendControl.className = "map-control legend-control card-3d";
  legendControl.innerHTML = `
        <div class="legend-header">
            <i class="bi bi-list-ul"></i> District Types
        </div>
        <div class="legend-content">
            <div class="legend-item"><span class="legend-color" style="background-color: #E57373;"></span> School Districts</div>
            <div class="legend-item"><span class="legend-color" style="background-color: #64B5F6;"></span> Cities</div>
            <div class="legend-item"><span class="legend-color" style="background-color: #FFB74D;"></span> Fire Districts</div>
            <div class="legend-item"><span class="legend-color" style="background-color: #81C784;"></span> County</div>
            <div class="legend-item"><span class="legend-color" style="background-color: #9575CD;"></span> Other Districts</div>
        </div>
    `;
  map.controls[google.maps.ControlPosition.LEFT_BOTTOM].push(legendControl);

  // Back to list view button
  const backButton = document.createElement("div");
  backButton.className = "map-control back-control card-3d";
  backButton.innerHTML = `
        <a href="/public/districts" class="btn btn-sm btn-light">
            <i class="bi bi-arrow-left"></i> Back to List View
        </a>
    `;
  map.controls[google.maps.ControlPosition.BOTTOM_LEFT].push(backButton);
}

// Setup UI interactions for the map
function setupUIInteractions() {
  // Toggle filter panel
  document.addEventListener("click", function (e) {
    if (
      e.target.id === "toggle-filter-panel" ||
      e.target.closest("#toggle-filter-panel")
    ) {
      document.getElementById("filter-panel").classList.toggle("show");
    }
  });

  // Close district info panel when clicking outside
  document.addEventListener("click", function (e) {
    const infoPanel = document.getElementById("district-info-panel");
    const clickedInsidePanel = e.target.closest("#district-info-panel");
    const clickedMarker = e.target.closest(".district-marker");

    if (
      infoPanel &&
      infoPanel.classList.contains("active") &&
      !clickedInsidePanel &&
      !clickedMarker
    ) {
      infoPanel.classList.remove("active");
    }
  });

  // Handle filter form submission
  const filterForm = document.getElementById("district-filter-form");
  if (filterForm) {
    filterForm.addEventListener("submit", function (e) {
      e.preventDefault();
      applyFilters();
    });
  }
}

// Initialize filter listeners
function setupFilterListeners() {
  // District type checkboxes
  document.querySelectorAll(".district-type-filter").forEach((checkbox) => {
    checkbox.addEventListener("change", function () {
      applyFilters();
    });
  });

  // Reset filter button
  const resetBtn = document.getElementById("reset-filters");
  if (resetBtn) {
    resetBtn.addEventListener("click", function () {
      document.querySelectorAll(".district-type-filter").forEach((cb) => {
        cb.checked = true;
      });
      applyFilters();
    });
  }
}

// Apply map filters
function applyFilters() {
  // Get selected district types
  const selectedTypes = [];
  document
    .querySelectorAll(".district-type-filter:checked")
    .forEach((checkbox) => {
      selectedTypes.push(checkbox.value);
    });

  // Update filter settings
  filterSettings.districtTypes = selectedTypes;

  // Reload districts with new filters
  loadDistricts();

  // Optional: close the filter panel on small screens
  if (window.innerWidth < 768) {
    document.getElementById("filter-panel").classList.remove("show");
  }
}

// Check if a district should be displayed based on filter settings
function shouldDisplayDistrict(district) {
  // If no district types selected, show none
  if (filterSettings.districtTypes.length === 0) {
    return false;
  }

  // Check district type filter
  if (filterSettings.districtTypes.length > 0) {
    return filterSettings.districtTypes.includes(
      district.district_type || "OTHER",
    );
  }

  // Default to showing the district
  return true;
}

// Update the displayed district count
function updateDistrictCount() {
  const countElement = document.getElementById("district-count");
  if (countElement) {
    const visibleCount = districtMarkers.length;
    countElement.textContent = visibleCount;
  }
}

// Display error message
function displayErrorMessage(message) {
  const errorPanel = document.getElementById("error-message");
  if (errorPanel) {
    errorPanel.innerHTML = `
            <div class="alert alert-danger">
                <i class="bi bi-exclamation-triangle"></i> ${message}
            </div>
        `;
    errorPanel.style.display = "block";
  } else {
    console.error(message);
  }
}

// Map styles for a modern, clean look
function getMapStyles() {
  return [
    {
      featureType: "water",
      elementType: "geometry",
      stylers: [{ color: "#e9e9e9" }, { lightness: 17 }],
    },
    {
      featureType: "landscape",
      elementType: "geometry",
      stylers: [{ color: "#f5f5f5" }, { lightness: 20 }],
    },
    {
      featureType: "road.highway",
      elementType: "geometry.fill",
      stylers: [{ color: "#ffffff" }, { lightness: 17 }],
    },
    {
      featureType: "road.highway",
      elementType: "geometry.stroke",
      stylers: [{ color: "#ffffff" }, { lightness: 29 }, { weight: 0.2 }],
    },
    {
      featureType: "road.arterial",
      elementType: "geometry",
      stylers: [{ color: "#ffffff" }, { lightness: 18 }],
    },
    {
      featureType: "road.local",
      elementType: "geometry",
      stylers: [{ color: "#ffffff" }, { lightness: 16 }],
    },
    {
      featureType: "poi",
      elementType: "geometry",
      stylers: [{ color: "#f5f5f5" }, { lightness: 21 }],
    },
    {
      featureType: "poi.park",
      elementType: "geometry",
      stylers: [{ color: "#dedede" }, { lightness: 21 }],
    },
    {
      elementType: "labels.text.stroke",
      stylers: [{ visibility: "on" }, { color: "#ffffff" }, { lightness: 16 }],
    },
    {
      elementType: "labels.text.fill",
      stylers: [{ saturation: 36 }, { color: "#333333" }, { lightness: 40 }],
    },
    {
      elementType: "labels.icon",
      stylers: [{ visibility: "off" }],
    },
    {
      featureType: "transit",
      elementType: "geometry",
      stylers: [{ color: "#f2f2f2" }, { lightness: 19 }],
    },
    {
      featureType: "administrative",
      elementType: "geometry.fill",
      stylers: [{ color: "#fefefe" }, { lightness: 20 }],
    },
    {
      featureType: "administrative",
      elementType: "geometry.stroke",
      stylers: [{ color: "#fefefe" }, { lightness: 17 }, { weight: 1.2 }],
    },
  ];
}

// Periodically cycle through animation effects for each marker
function cycleMarkerAnimations() {
  const animationCycleInterval = 60000; // Change animations every 60 seconds
  const effectTypes = [
    "pulse-effect",
    "glow-effect",
    "bounce-effect",
    "spin-effect",
  ];

  setInterval(() => {
    // Get all marker elements
    const markerElements = document.querySelectorAll(".district-marker");

    markerElements.forEach((marker) => {
      // Remove all existing animation classes
      effectTypes.forEach((effect) => {
        marker.classList.remove(effect);
      });

      // Add a new random animation class
      const newEffect =
        effectTypes[Math.floor(Math.random() * effectTypes.length)];
      marker.classList.add(newEffect);
      marker.setAttribute("data-animation-type", newEffect);
    });
  }, animationCycleInterval);
}
