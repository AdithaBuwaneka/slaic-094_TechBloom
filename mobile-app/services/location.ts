import * as Location from 'expo-location';
import { APP_CONFIG, SRI_LANKA_CONFIG } from '@/constants/Config';
import type { Location as LocationType } from '@/types';

class LocationService {
  private currentLocation: LocationType | null = null;
  private watchId: Location.LocationSubscription | null = null;

  async requestPermissions(): Promise<boolean> {
    try {
      const { status } = await Location.requestForegroundPermissionsAsync();
      return status === 'granted';
    } catch (error) {
      console.error('Failed to request location permissions:', error);
      return false;
    }
  }

  async getCurrentLocation(): Promise<LocationType | null> {
    try {
      const hasPermission = await this.requestPermissions();
      if (!hasPermission) {
        throw new Error('Location permission not granted');
      }

      const location = await Location.getCurrentPositionAsync({
        accuracy: Location.Accuracy.Balanced,
        timeout: APP_CONFIG.LOCATION_TIMEOUT,
      });

      const result: LocationType = {
        latitude: location.coords.latitude,
        longitude: location.coords.longitude,
        accuracy: location.coords.accuracy || undefined,
      };

      // Get address if possible
      try {
        const addresses = await Location.reverseGeocodeAsync({
          latitude: result.latitude,
          longitude: result.longitude,
        });

        if (addresses.length > 0) {
          const address = addresses[0];
          result.address = [
            address.streetNumber,
            address.street,
            address.city,
            address.region,
          ].filter(Boolean).join(', ');
        }
      } catch (geocodeError) {
        console.warn('Failed to get address:', geocodeError);
      }

      this.currentLocation = result;
      return result;
    } catch (error) {
      console.error('Failed to get current location:', error);
      // Return Sri Lanka center as fallback
      return {
        latitude: SRI_LANKA_CONFIG.DEFAULT_CENTER.latitude,
        longitude: SRI_LANKA_CONFIG.DEFAULT_CENTER.longitude,
        address: 'Sri Lanka',
      };
    }
  }

  async startLocationTracking(callback: (location: LocationType) => void): Promise<boolean> {
    try {
      const hasPermission = await this.requestPermissions();
      if (!hasPermission) {
        return false;
      }

      this.watchId = await Location.watchPositionAsync(
        {
          accuracy: Location.Accuracy.Balanced,
          timeInterval: 30000, // Update every 30 seconds
          distanceInterval: 100, // Or when moved 100 meters
        },
        (location) => {
          const result: LocationType = {
            latitude: location.coords.latitude,
            longitude: location.coords.longitude,
            accuracy: location.coords.accuracy || undefined,
          };

          this.currentLocation = result;
          callback(result);
        }
      );

      return true;
    } catch (error) {
      console.error('Failed to start location tracking:', error);
      return false;
    }
  }

  stopLocationTracking(): void {
    if (this.watchId) {
      this.watchId.remove();
      this.watchId = null;
    }
  }

  getCachedLocation(): LocationType | null {
    return this.currentLocation;
  }

  async searchLocation(query: string): Promise<LocationType[]> {
    try {
      const results = await Location.geocodeAsync(query);
      
      return results.map((result) => ({
        latitude: result.latitude,
        longitude: result.longitude,
        address: query, // Use the search query as address
      }));
    } catch (error) {
      console.error('Failed to search location:', error);
      return [];
    }
  }

  async getAddressFromCoordinates(latitude: number, longitude: number): Promise<string> {
    try {
      const addresses = await Location.reverseGeocodeAsync({
        latitude,
        longitude,
      });

      if (addresses.length > 0) {
        const address = addresses[0];
        return [
          address.streetNumber,
          address.street,
          address.city,
          address.region,
        ].filter(Boolean).join(', ');
      }
      
      return `${latitude.toFixed(4)}, ${longitude.toFixed(4)}`;
    } catch (error) {
      console.error('Failed to get address from coordinates:', error);
      return `${latitude.toFixed(4)}, ${longitude.toFixed(4)}`;
    }
  }

  calculateDistance(loc1: LocationType, loc2: LocationType): number {
    const R = 6371; // Earth's radius in kilometers
    const dLat = (loc2.latitude - loc1.latitude) * Math.PI / 180;
    const dLon = (loc2.longitude - loc1.longitude) * Math.PI / 180;
    const a = 
      Math.sin(dLat/2) * Math.sin(dLat/2) +
      Math.cos(loc1.latitude * Math.PI / 180) * Math.cos(loc2.latitude * Math.PI / 180) * 
      Math.sin(dLon/2) * Math.sin(dLon/2);
    const c = 2 * Math.atan2(Math.sqrt(a), Math.sqrt(1-a));
    return R * c; // Distance in kilometers
  }

  isInSriLanka(location: LocationType): boolean {
    // Rough bounding box for Sri Lanka
    const bounds = {
      north: 9.8,
      south: 5.9,
      east: 81.9,
      west: 79.5,
    };

    return (
      location.latitude >= bounds.south &&
      location.latitude <= bounds.north &&
      location.longitude >= bounds.west &&
      location.longitude <= bounds.east
    );
  }

  getNearestPopularCity(location: LocationType): { name: string; coordinates: LocationType } {
    let nearest = SRI_LANKA_CONFIG.POPULAR_CITIES[0];
    let minDistance = this.calculateDistance(location, nearest.coordinates);

    for (const city of SRI_LANKA_CONFIG.POPULAR_CITIES) {
      const distance = this.calculateDistance(location, city.coordinates);
      if (distance < minDistance) {
        minDistance = distance;
        nearest = city;
      }
    }

    return nearest;
  }
}

export const locationService = new LocationService();