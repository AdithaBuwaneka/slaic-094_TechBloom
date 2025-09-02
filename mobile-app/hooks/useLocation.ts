import { useState, useEffect, useCallback } from 'react';
import { Platform, Alert } from 'react-native';
import { locationService } from '@/services/location';
import { apiService } from '@/services/api';
import type { Location } from '@/types';

export interface UseLocationReturn {
  location: Location | null;
  isLoading: boolean;
  error: string | null;
  hasPermission: boolean;
  requestLocation: () => Promise<void>;
  startTracking: () => Promise<void>;
  stopTracking: () => void;
  searchLocations: (query: string) => Promise<Location[]>;
  getAddressFromCoords: (lat: number, lng: number) => Promise<string>;
}

export function useLocation(): UseLocationReturn {
  const [location, setLocation] = useState<Location | null>(null);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [hasPermission, setHasPermission] = useState(false);
  const [isTracking, setIsTracking] = useState(false);

  // Check permissions on mount
  useEffect(() => {
    checkPermissions();
  }, []);

  // Auto-request location on permission granted
  useEffect(() => {
    if (hasPermission && !location && !isLoading) {
      requestLocation();
    }
  }, [hasPermission]);

  const checkPermissions = async () => {
    try {
      const granted = await locationService.requestPermissions();
      setHasPermission(granted);
      
      if (!granted) {
        setError('Location permission is required for the app to work properly');
        Alert.alert(
          'Location Permission Required',
          'This app needs access to your location to provide transit directions and find nearby stops.',
          [
            { text: 'Cancel', style: 'cancel' },
            { text: 'Settings', onPress: () => {
              // In a real app, you'd open device settings
              console.log('Open device settings');
            }},
          ]
        );
      }
    } catch (err) {
      console.error('Permission check failed:', err);
      setError('Failed to check location permissions');
    }
  };

  const requestLocation = useCallback(async () => {
    if (isLoading) return;
    
    setIsLoading(true);
    setError(null);

    try {
      console.log('🗺️ Requesting current location...');
      const currentLocation = await locationService.getCurrentLocation();
      
      if (currentLocation) {
        setLocation(currentLocation);
        console.log('✅ Location obtained:', {
          lat: currentLocation.latitude.toFixed(4),
          lng: currentLocation.longitude.toFixed(4),
          address: currentLocation.address
        });

        // Check if location is in Sri Lanka
        if (!locationService.isInSriLanka(currentLocation)) {
          console.warn('⚠️ Location is outside Sri Lanka');
          Alert.alert(
            'Location Notice',
            'You appear to be outside Sri Lanka. The app is optimized for Sri Lankan public transport.',
            [{ text: 'OK' }]
          );
        } else {
          // Update backend with location
          try {
            await apiService.updateLocation({
              latitude: currentLocation.latitude,
              longitude: currentLocation.longitude
            });
            console.log('📍 Location updated on backend');
          } catch (apiError) {
            console.warn('Failed to update location on backend:', apiError);
            // Don't show error to user as this is not critical
          }
        }
      } else {
        throw new Error('Unable to get location');
      }
    } catch (err: any) {
      const errorMessage = err.message || 'Failed to get location';
      setError(errorMessage);
      console.error('❌ Location request failed:', errorMessage);
      
      // Show user-friendly error
      if (errorMessage.includes('permission')) {
        Alert.alert(
          'Permission Needed',
          'Please enable location access in your device settings to use this feature.'
        );
      } else {
        Alert.alert(
          'Location Error',
          'Unable to get your location. Please check your GPS settings and try again.'
        );
      }
    } finally {
      setIsLoading(false);
    }
  }, [isLoading]);

  const startTracking = useCallback(async () => {
    if (isTracking || !hasPermission) return;

    try {
      console.log('🎯 Starting location tracking...');
      const success = await locationService.startLocationTracking((newLocation) => {
        setLocation(newLocation);
        console.log('📍 Location updated:', {
          lat: newLocation.latitude.toFixed(4),
          lng: newLocation.longitude.toFixed(4)
        });

        // Update backend periodically (throttled)
        apiService.updateLocation({
          latitude: newLocation.latitude,
          longitude: newLocation.longitude
        }).catch(err => {
          console.warn('Failed to sync location with backend:', err);
        });
      });

      if (success) {
        setIsTracking(true);
        console.log('✅ Location tracking started');
      } else {
        throw new Error('Failed to start location tracking');
      }
    } catch (err: any) {
      const errorMessage = err.message || 'Failed to start location tracking';
      setError(errorMessage);
      console.error('❌ Location tracking failed:', errorMessage);
    }
  }, [isTracking, hasPermission]);

  const stopTracking = useCallback(() => {
    if (!isTracking) return;

    locationService.stopLocationTracking();
    setIsTracking(false);
    console.log('⏹️ Location tracking stopped');
  }, [isTracking]);

  const searchLocations = useCallback(async (query: string): Promise<Location[]> => {
    if (!query.trim()) return [];

    try {
      console.log('🔍 Searching locations for:', query);
      const results = await locationService.searchLocation(query);
      
      // Filter results to Sri Lankan locations only
      const sriLankanResults = results.filter(loc => 
        locationService.isInSriLanka(loc)
      );

      console.log(`✅ Found ${sriLankanResults.length} Sri Lankan locations`);
      return sriLankanResults;
    } catch (err) {
      console.error('❌ Location search failed:', err);
      return [];
    }
  }, []);

  const getAddressFromCoords = useCallback(async (lat: number, lng: number): Promise<string> => {
    try {
      return await locationService.getAddressFromCoordinates(lat, lng);
    } catch (err) {
      console.error('Failed to get address from coordinates:', err);
      return `${lat.toFixed(4)}, ${lng.toFixed(4)}`;
    }
  }, []);

  // Cleanup on unmount
  useEffect(() => {
    return () => {
      if (isTracking) {
        stopTracking();
      }
    };
  }, [isTracking, stopTracking]);

  return {
    location,
    isLoading,
    error,
    hasPermission,
    requestLocation,
    startTracking,
    stopTracking,
    searchLocations,
    getAddressFromCoords,
  };
}