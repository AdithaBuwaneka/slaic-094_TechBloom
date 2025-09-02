/**
 * Polyline decoder for Google Maps encoded polylines
 * Converts encoded polyline strings to coordinate arrays for map display
 */

export interface LatLng {
  latitude: number;
  longitude: number;
}

/**
 * Decodes a Google Maps encoded polyline string into an array of coordinates
 * @param encoded - Encoded polyline string from Google Maps API
 * @returns Array of coordinate objects with latitude and longitude
 */
export function decodePolyline(encoded: string): LatLng[] {
  if (!encoded || encoded.length === 0) {
    return [];
  }

  const coordinates: LatLng[] = [];
  let index = 0;
  let lat = 0;
  let lng = 0;

  while (index < encoded.length) {
    let shift = 0;
    let result = 0;
    let byte: number;

    // Decode latitude
    do {
      byte = encoded.charCodeAt(index++) - 63;
      result |= (byte & 0x1f) << shift;
      shift += 5;
    } while (byte >= 0x20);

    const deltaLat = (result & 1) ? ~(result >> 1) : result >> 1;
    lat += deltaLat;

    shift = 0;
    result = 0;

    // Decode longitude
    do {
      byte = encoded.charCodeAt(index++) - 63;
      result |= (byte & 0x1f) << shift;
      shift += 5;
    } while (byte >= 0x20);

    const deltaLng = (result & 1) ? ~(result >> 1) : result >> 1;
    lng += deltaLng;

    coordinates.push({
      latitude: lat / 1e5,
      longitude: lng / 1e5,
    });
  }

  return coordinates;
}

/**
 * Generates mock coordinates for a straight line between two points
 * Used when actual polyline data is not available
 */
export function generateStraightLinePolyline(
  start: LatLng,
  end: LatLng,
  segments: number = 10
): LatLng[] {
  const coordinates: LatLng[] = [];
  
  for (let i = 0; i <= segments; i++) {
    const ratio = i / segments;
    coordinates.push({
      latitude: start.latitude + (end.latitude - start.latitude) * ratio,
      longitude: start.longitude + (end.longitude - start.longitude) * ratio,
    });
  }
  
  return coordinates;
}

/**
 * Gets mock polyline data for common Sri Lankan routes
 * This is used when backend returns mock polyline identifiers
 */
export function getMockPolylineCoordinates(polylineId: string): LatLng[] {
  const mockPolylines: { [key: string]: LatLng[] } = {
    mock_polyline_colombo_kandy_train: [
      { latitude: 6.9271, longitude: 79.8612 }, // Colombo Fort
      { latitude: 7.0167, longitude: 79.9000 }, // Ragama
      { latitude: 7.1500, longitude: 80.1000 }, // Gampaha
      { latitude: 7.2000, longitude: 80.3000 }, // Peradeniya
      { latitude: 7.2906, longitude: 80.6337 }, // Kandy
    ],
    mock_polyline_colombo_kandy_bus: [
      { latitude: 6.9271, longitude: 79.8612 }, // Colombo
      { latitude: 7.0000, longitude: 79.9500 }, // Kelaniya
      { latitude: 7.1000, longitude: 80.2000 }, // Kegalle
      { latitude: 7.2906, longitude: 80.6337 }, // Kandy
    ],
    mock_polyline_colombo_galle: [
      { latitude: 6.9271, longitude: 79.8612 }, // Colombo
      { latitude: 6.8000, longitude: 79.9000 }, // Mount Lavinia
      { latitude: 6.4500, longitude: 79.9500 }, // Kalutara
      { latitude: 6.2000, longitude: 80.1000 }, // Bentota
      { latitude: 6.0329, longitude: 80.2168 }, // Galle
    ],
    mock_polyline_kandy_nuwara_eliya: [
      { latitude: 7.2906, longitude: 80.6337 }, // Kandy
      { latitude: 7.2500, longitude: 80.7000 }, // Gampola
      { latitude: 7.1000, longitude: 80.7500 }, // Nawalapitiya
      { latitude: 6.9497, longitude: 80.7891 }, // Nuwara Eliya
    ],
    mock_polyline_default: [
      { latitude: 6.9271, longitude: 79.8612 },
      { latitude: 7.2906, longitude: 80.6337 },
    ],
  };

  return mockPolylines[polylineId] || [];
}