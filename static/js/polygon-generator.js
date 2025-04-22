/**
 * Polygon Generator
 *
 * This module provides functions to generate random polygon shapes for district
 * boundaries on the map, creating a visually appealing representation of tax districts.
 */

// Base coordinates for Benton County area
const BENTON_COUNTY_CENTER = { lat: 46.25, lng: -119.3 };
const BENTON_COUNTY_BOUNDS = {
  north: 46.5, // Northern boundary
  south: 46.0, // Southern boundary
  east: -119.0, // Eastern boundary
  west: -119.6, // Western boundary
};

/**
 * Generate a random polygon around a center point
 *
 * @param {Object} center - The center point {lat, lng}
 * @param {String} districtType - The type of district
 * @returns {Array} Array of coordinates forming a polygon
 */
function generateDistrictPolygon(center, districtType) {
  // Number of sides for the polygon based on district type
  let sides;
  let irregularity;
  let sizeVariance;

  // Determine polygon characteristics based on district type
  switch (districtType) {
    case "SCHOOL":
      sides = getRandomInt(6, 8); // More complex shapes for school districts
      irregularity = 0.4; // Moderate irregularity
      sizeVariance = getRandomFloat(0.03, 0.06); // Medium size
      break;
    case "CITY":
      sides = getRandomInt(8, 12); // Complex city boundaries
      irregularity = 0.3; // Moderate irregularity for cities
      sizeVariance = getRandomFloat(0.02, 0.05); // Smaller but varied
      break;
    case "FIRE":
      sides = getRandomInt(5, 7); // Simpler shapes for fire districts
      irregularity = 0.2; // Less irregular
      sizeVariance = getRandomFloat(0.04, 0.08); // Larger districts
      break;
    case "COUNTY":
      sides = getRandomInt(10, 15); // Very complex for county boundaries
      irregularity = 0.5; // High irregularity
      sizeVariance = getRandomFloat(0.08, 0.12); // Largest districts
      break;
    case "LIBRARY":
      sides = getRandomInt(4, 6); // Simple shapes for library districts
      irregularity = 0.1; // Low irregularity
      sizeVariance = getRandomFloat(0.015, 0.03); // Small districts
      break;
    case "PORT":
      sides = getRandomInt(5, 8); // Waterfront-like shapes
      irregularity = 0.6; // High irregularity for natural boundaries
      sizeVariance = getRandomFloat(0.03, 0.06); // Medium size
      break;
    case "HOSPITAL":
      sides = getRandomInt(4, 6); // Simple shapes for hospital districts
      irregularity = 0.1; // Low irregularity
      sizeVariance = getRandomFloat(0.01, 0.025); // Smaller districts
      break;
    case "CEMETERY":
      sides = 4; // Rectangular for cemeteries
      irregularity = 0.05; // Very regular
      sizeVariance = getRandomFloat(0.005, 0.015); // Very small
      break;
    default:
      sides = getRandomInt(5, 8); // Default shape
      irregularity = 0.2; // Moderate irregularity
      sizeVariance = getRandomFloat(0.02, 0.04); // Medium-small size
  }

  // Generate the polygon coordinates
  return generateIrregularPolygon(center, sides, sizeVariance, irregularity);
}

/**
 * Generate an irregular polygon around a center point
 *
 * @param {Object} center - The center point {lat, lng}
 * @param {Number} sides - Number of sides for the polygon
 * @param {Number} avgSize - Average size/radius of the polygon
 * @param {Number} irregularity - How irregular the polygon should be (0-1)
 * @returns {Array} Array of coordinates forming a polygon
 */
function generateIrregularPolygon(center, sides, avgSize, irregularity) {
  const coordinates = [];
  const angleStep = (2 * Math.PI) / sides;

  // Generate points around the center
  for (let i = 0; i < sides; i++) {
    // Base angle for this vertex
    const angle = i * angleStep;

    // Add some randomness to the angle
    const angleVariance = angleStep * irregularity;
    const adjustedAngle =
      angle + getRandomFloat(-angleVariance / 2, angleVariance / 2);

    // Add some randomness to the distance from center
    const sizeVariance = avgSize * irregularity;
    const radius =
      avgSize + getRandomFloat(-sizeVariance / 2, sizeVariance / 2);

    // Calculate lat/lng and add to coordinates
    const lat = center.lat + radius * Math.sin(adjustedAngle);
    const lng = center.lng + radius * Math.cos(adjustedAngle);

    // Constrain to Benton County bounds
    const constrainedLat = Math.max(
      BENTON_COUNTY_BOUNDS.south,
      Math.min(BENTON_COUNTY_BOUNDS.north, lat),
    );
    const constrainedLng = Math.max(
      BENTON_COUNTY_BOUNDS.west,
      Math.min(BENTON_COUNTY_BOUNDS.east, lng),
    );

    coordinates.push({ lat: constrainedLat, lng: constrainedLng });
  }

  // Close the polygon by repeating the first point
  coordinates.push({ ...coordinates[0] });

  return coordinates;
}

/**
 * Generate random coordinates within Benton County
 *
 * @param {Number} index - Seed value to ensure consistent output for same index
 * @returns {Object} Latitude and longitude {lat, lng}
 */
function generateRandomCoordinates(index) {
  // Use a seeded random based on index to create stable coordinates
  const seed = index * 9999;
  const stableRandom = mulberry32(seed);

  // Generate coordinates within the bounds of Benton County
  const latRange = BENTON_COUNTY_BOUNDS.north - BENTON_COUNTY_BOUNDS.south;
  const lngRange = BENTON_COUNTY_BOUNDS.east - BENTON_COUNTY_BOUNDS.west;

  const lat = BENTON_COUNTY_BOUNDS.south + stableRandom() * latRange;
  const lng = BENTON_COUNTY_BOUNDS.west + stableRandom() * lngRange;

  return { lat, lng };
}

/**
 * Simple seeded random number generator
 *
 * @param {Number} seed - Seed value for the generator
 * @returns {Function} Function that returns a random number between 0 and 1
 */
function mulberry32(seed) {
  return function () {
    let t = (seed += 0x6d2b79f5);
    t = Math.imul(t ^ (t >>> 15), t | 1);
    t ^= t + Math.imul(t ^ (t >>> 7), t | 61);
    return ((t ^ (t >>> 14)) >>> 0) / 4294967296;
  };
}

/**
 * Generate a random integer between min and max (inclusive)
 *
 * @param {Number} min - Minimum value
 * @param {Number} max - Maximum value
 * @returns {Number} Random integer
 */
function getRandomInt(min, max) {
  min = Math.ceil(min);
  max = Math.floor(max);
  return Math.floor(Math.random() * (max - min + 1)) + min;
}

/**
 * Generate a random float between min and max
 *
 * @param {Number} min - Minimum value
 * @param {Number} max - Maximum value
 * @returns {Number} Random float
 */
function getRandomFloat(min, max) {
  return Math.random() * (max - min) + min;
}
