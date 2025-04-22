/**
 * Immersive Map View
 *
 * An interactive Google Maps-based visualization of tax districts with
 * custom markers, district boundary polygons, and interactive features.
 */

// Global variables
let map; // Google Map instance
let districtData = []; // District data from the server
let districtMarkers = []; // Array to track district markers
let districtPolygons = []; // Array to track district polygons
let activeInfoWindow = null; // Currently active info window
let mapInitialized = false; // Flag to track map initialization

// Filter settings
const filterSettings = {
  districtTypes: [], // Active district type filters
};

// Main initialization function called when the page loads
function initMap() {
  // Initialize the map
  map = new google.maps.Map(document.getElementById("map"), {
    center: { lat: 46.25, lng: -119.3 }, // Benton County, WA
    zoom: 10,
    mapTypeId: "terrain",
    mapTypeControl: true,
    mapTypeControlOptions: {
      style: google.maps.MapTypeControlStyle.DROPDOWN_MENU,
      position: google.maps.ControlPosition.TOP_RIGHT,
    },
    streetViewControl: false,
    fullscreenControl: true,
    fullscreenControlOptions: {
      position: google.maps.ControlPosition.RIGHT_BOTTOM,
    },
    zoomControl: false, // We'll use our custom zoom controls
    styles: [
      {
        featureType: "administrative.locality",
        elementType: "labels",
        stylers: [{ visibility: "on" }],
      },
      {
        featureType: "administrative.neighborhood",
        stylers: [{ visibility: "off" }],
      },
      {
        featureType: "poi",
        elementType: "labels",
        stylers: [{ visibility: "off" }],
      },
      {
        featureType: "road",
        elementType: "labels.icon",
        stylers: [{ visibility: "off" }],
      },
      {
        featureType: "transit",
        stylers: [{ visibility: "off" }],
      },
      {
        featureType: "water",
        elementType: "labels",
        stylers: [{ visibility: "off" }],
      },
    ],
  });

  // Flag map as initialized
  mapInitialized = true;

  // Load district data and set up event handlers
  fetchDistrictData()
    .then(() => {
      // Setup UI interactions
      setupUIInteractions();
      setupFilterListeners();

      // Start cycling animations
      cycleMarkerAnimations();

      // Check for district ID in URL for direct linking
      const urlParams = new URLSearchParams(window.location.search);
      const districtId = urlParams.get("district_id");

      if (districtId) {
        // Attempt to find and highlight the district
        highlightDistrictById(districtId);
      }
    })
    .catch((error) => {
      console.error("Error initializing map:", error);
      displayErrorMessage(
        "Failed to load district data. Please try refreshing the page.",
      );
    });
}

// Fetch district data from the server
function fetchDistrictData() {
  return new Promise((resolve, reject) => {
    // First check if data is already in the page
    const dataElement = document.getElementById("district-data");
    if (dataElement) {
      try {
        districtData = JSON.parse(dataElement.textContent);
        loadDistricts();
        resolve();
        return;
      } catch (e) {
        console.warn("Failed to parse embedded district data:", e);
        // Fall back to API call
      }
    }

    // If we don't have embedded data, fetch from API
    fetch("/api/districts")
      .then((response) => {
        if (!response.ok) {
          throw new Error("Network response was not ok");
        }
        return response.json();
      })
      .then((data) => {
        districtData = data;
        loadDistricts();
        resolve();
      })
      .catch((error) => {
        console.error("Error fetching district data:", error);
        reject(error);
      });
  });
}

// Clear all map features (markers and polygons)
function clearMapFeatures() {
  // Clear markers
  districtMarkers.forEach((marker) => {
    if (marker.overlay) {
      marker.overlay.setMap(null);
    }
  });
  districtMarkers = [];

  // Clear polygons
  districtPolygons.forEach((polyObj) => {
    polyObj.polygon.setMap(null);
  });
  districtPolygons = [];
}

// Create a custom marker for a district
function createDistrictMarker(district, coordinates) {
  // Determine the right animation type based on district type
  let animationType;
  switch (district.district_type) {
    case "SCHOOL":
      animationType = "pulse-effect";
      break;
    case "CITY":
      animationType = "glow-effect";
      break;
    case "FIRE":
      animationType = "bounce-effect";
      break;
    case "COUNTY":
      animationType = "spin-effect";
      break;
    default:
      animationType = "pulse-effect";
  }

  // Create the marker HTML with animations
  const markerContent = `
        <div class="district-marker marker-${district.district_type || "OTHER"} ${animationType}" 
             data-animation-type="${animationType}"
             title="${district.district_name}">
            ${district.district_name ? district.district_name.substring(0, 2) : "?"}
        </div>
    `;

  // Create a custom overlay
  const overlay = new CustomMarker(
    new google.maps.LatLng(coordinates.lat, coordinates.lng),
    map,
    markerContent,
    district,
  );

  // Add it to our collection
  districtMarkers.push({
    overlay,
    district,
    position: coordinates,
  });

  return overlay;
}

// Handle marker click to show district info
function showDistrictInfo(district) {
  // Get existing or create info panel
  let infoPanel = document.getElementById("districtInfoPanel");

  if (!infoPanel) {
    infoPanel = document.createElement("div");
    infoPanel.id = "districtInfoPanel";
    infoPanel.className = "district-info-panel";
    document.querySelector(".map-overlay").appendChild(infoPanel);
  }

  // Get tax code details if available
  const taxCodes = district.tax_codes || [];
  const latestTaxCode = taxCodes.length > 0 ? taxCodes[0] : null;

  // Format tax information
  let taxRateInfo = "No tax information available";
  let levyAmountInfo = "";
  let assessedValueInfo = "";

  if (latestTaxCode) {
    taxRateInfo = `${parseFloat(latestTaxCode.levy_rate || 0).toFixed(6)}`;
    levyAmountInfo = `$${parseFloat(latestTaxCode.levy_amount || 0).toLocaleString(undefined, { maximumFractionDigits: 2 })}`;
    assessedValueInfo = `$${parseFloat(latestTaxCode.total_assessed_value || 0).toLocaleString(undefined, { maximumFractionDigits: 2 })}`;
  }

  // Build the info panel content
  infoPanel.innerHTML = `
        <div class="info-panel-header">
            <h4>${district.district_name || "Unknown District"}</h4>
            <button class="info-close-btn">×</button>
        </div>
        <div class="info-panel-content">
            <div class="row mb-3">
                <div class="col">
                    <strong>District Type:</strong>
                    <span class="badge filter-${district.district_type}">${district.district_type || "OTHER"}</span>
                </div>
            </div>
            
            <div class="row mb-3">
                <div class="col-md-6">
                    <div class="card mb-2">
                        <div class="card-body p-2 text-center">
                            <small class="text-muted">Levy Rate</small>
                            <h5 class="mb-0">${taxRateInfo}</h5>
                        </div>
                    </div>
                </div>
                <div class="col-md-6">
                    <div class="card mb-2">
                        <div class="card-body p-2 text-center">
                            <small class="text-muted">Levy Amount</small>
                            <h5 class="mb-0">${levyAmountInfo}</h5>
                        </div>
                    </div>
                </div>
            </div>
            
            <div class="card mb-3">
                <div class="card-body p-2 text-center">
                    <small class="text-muted">Total Assessed Value</small>
                    <h5 class="mb-0">${assessedValueInfo}</h5>
                </div>
            </div>
            
            <div class="d-grid gap-2">
                <a href="/districts/${district.id}/detail" class="btn btn-primary">
                    <i class="fas fa-chart-bar me-1"></i> View District Details
                </a>
            </div>
        </div>
    `;

  // Show the panel
  infoPanel.classList.add("visible");

  // Add close button event listener
  infoPanel
    .querySelector(".info-close-btn")
    .addEventListener("click", function () {
      infoPanel.classList.remove("visible");

      // Deactivate all polygons
      districtPolygons.forEach((poly) => {
        removeClassFromPolygon(poly.polygon, "district-polygon-active");
        poly.isActive = false;
      });
    });
}

// Find and highlight a district by ID
function highlightDistrictById(districtId) {
  // Parse the ID to ensure it's an integer
  const id = parseInt(districtId, 10);

  // Find the district in our data
  const district = districtData.find((d) => d.id === id);

  if (district) {
    // Try to highlight the polygon first
    const highlighted = highlightDistrictPolygon(id);

    if (highlighted) {
      // Show the district info
      showDistrictInfo(district);
      return true;
    } else {
      console.warn(
        `District found but polygon could not be highlighted for ID: ${id}`,
      );
      return false;
    }
  } else {
    console.warn(`District not found for ID: ${id}`);
    return false;
  }
}

// Display error message on the map
function displayErrorMessage(message) {
  const errorElement = document.createElement("div");
  errorElement.className = "alert alert-danger map-error";
  errorElement.style.position = "absolute";
  errorElement.style.top = "50%";
  errorElement.style.left = "50%";
  errorElement.style.transform = "translate(-50%, -50%)";
  errorElement.style.zIndex = "1000";
  errorElement.style.padding = "15px 20px";
  errorElement.style.borderRadius = "5px";
  errorElement.style.boxShadow = "0 4px 15px rgba(0, 0, 0, 0.2)";
  errorElement.innerHTML = `
        <i class="fas fa-exclamation-triangle me-2"></i>
        ${message}
    `;

  // Add to the map container
  document.querySelector(".map-container").appendChild(errorElement);

  // Remove after 5 seconds
  setTimeout(() => {
    errorElement.remove();
  }, 5000);
}

// Custom marker overlay class for Google Maps
class CustomMarker extends google.maps.OverlayView {
  constructor(position, map, content, district) {
    super();
    this.position = position;
    this.content = content;
    this.district = district;
    this.div_ = null;
    this.setMap(map);
  }

  draw() {
    if (!this.div_) {
      this.div_ = document.createElement("div");
      this.div_.className = "district-marker-container";
      this.div_.innerHTML = this.content;
      this.div_.style.position = "absolute";
      this.div_.style.cursor = "pointer";

      // Add click listener
      this.div_.addEventListener("click", (e) => {
        e.stopPropagation();

        // Add ripple effect
        this.div_
          .querySelector(".district-marker")
          .classList.add("ripple-animation");

        // Remove ripple class after animation completes
        setTimeout(() => {
          const markerElement = this.div_.querySelector(".district-marker");
          if (markerElement) {
            markerElement.classList.remove("ripple-animation");
          }
        }, 1000);

        // Show district info
        showDistrictInfo(this.district);

        // Highlight the corresponding polygon
        if (this.district.id) {
          highlightDistrictPolygon(this.district.id);
        }
      });

      // Add to the overlay
      const panes = this.getPanes();
      panes.overlayMouseTarget.appendChild(this.div_);
    }

    // Position the element
    const point = this.getProjection().fromLatLngToDivPixel(this.position);
    if (point) {
      this.div_.style.left = point.x - 20 + "px"; // Half the width of the marker
      this.div_.style.top = point.y - 20 + "px"; // Half the height of the marker
    }
  }

  onRemove() {
    if (this.div_) {
      this.div_.parentNode.removeChild(this.div_);
      this.div_ = null;
    }
  }
}

// Add district carousel items
function addDistrictToCarousel(district) {
  const carousel = document.getElementById("districtCarousel");
  if (!carousel) return;

  // Get tax code details if available
  const taxCodes = district.tax_codes || [];
  const latestTaxCode = taxCodes.length > 0 ? taxCodes[0] : null;

  // Format tax information
  let taxRateInfo = "No tax rate";
  let levyAmountInfo = "No levy amount";

  if (latestTaxCode) {
    taxRateInfo = `${parseFloat(latestTaxCode.levy_rate || 0).toFixed(6)}`;
    levyAmountInfo = `$${parseFloat(latestTaxCode.levy_amount || 0).toLocaleString(undefined, { maximumFractionDigits: 2 })}`;
  }

  // Create card element
  const card = document.createElement("div");
  card.className = `district-card district-card-${district.district_type || "other"}`;
  card.innerHTML = `
        <div class="card-body p-3">
            <h6 class="mb-1">${district.district_name || "Unknown District"}</h6>
            <div class="d-flex justify-content-between align-items-center mb-2">
                <span class="badge filter-${district.district_type}">${district.district_type || "OTHER"}</span>
                <small class="text-muted">Rate: ${taxRateInfo}</small>
            </div>
            <div class="text-end">
                <small>${levyAmountInfo}</small>
            </div>
        </div>
    `;

  // Add click handler to show district info
  card.addEventListener("click", function () {
    showDistrictInfo(district);

    if (district.id) {
      // Highlight the district polygon
      highlightDistrictPolygon(district.id);

      // Pan to the district
      const districtMarker = districtMarkers.find(
        (m) => m.district.id === district.id,
      );
      if (districtMarker && districtMarker.position) {
        map.panTo(districtMarker.position);
      }
    }
  });

  // Add to carousel
  carousel.appendChild(card);
}

// loadDistricts function has been moved to immersive-map-load-districts.js file

// Document ready event
document.addEventListener("DOMContentLoaded", function () {
  // If Google Maps API is already loaded, initialize the map
  if (window.google && window.google.maps) {
    initMap();
  }
  // Otherwise, the callback in the Google Maps script tag will initialize the map
});
