import React, { useState, useRef, useEffect, useCallback } from 'react';
import { View, Text, TouchableOpacity, StyleSheet, Alert, Platform } from 'react-native';
import { Ionicons } from '@expo/vector-icons';
import { useApp } from '@/context/AppContext';
import { SriLankanColors } from '@/constants/SriLankanTheme';
import { decodePolyline, getMockPolylineCoordinates, generateStraightLinePolyline } from '@/utils/polyline';
import type { Location, RouteOption } from '@/types';

// Import MapView conditionally
let MapView: any, Marker: any, Polyline: any, PROVIDER_GOOGLE: any, Region: any;
let hasNativeMaps = false;

try {
  const maps = require('react-native-maps');
  MapView = maps.default;
  Marker = maps.Marker;
  Polyline = maps.Polyline;
  PROVIDER_GOOGLE = maps.PROVIDER_GOOGLE;
  Region = maps.Region;
  // Temporarily force WebView for development builds until native maps are properly configured
  hasNativeMaps = false; // Change to true when native maps work properly
} catch (error) {
  // react-native-maps not available (Expo Go)
  hasNativeMaps = false;
}

// Fallback components
import RouteMapFallback from './MapViewFallback';
import SimpleMapView from './SimpleMapView';
import GoogleMapsWebView from './GoogleMapsWebView';

interface RouteMapProps {
  origin?: Location;
  destination?: Location;
  route?: RouteOption;
  showUserLocation?: boolean;
  onLocationSelect?: (coordinate: { latitude: number; longitude: number }) => void;
  height?: number;
}

export default function RouteMap({
  origin,
  destination,
  route,
  showUserLocation = true,
  onLocationSelect,
  height = 300,
}: RouteMapProps) {
  // If react-native-maps is not available (Expo Go), use Google Maps WebView
  if (!hasNativeMaps) {
    console.log('🌐 Using Google Maps WebView (native maps not available)');
    return (
      <GoogleMapsWebView
        origin={origin}
        destination={destination}
        route={route}
        showUserLocation={showUserLocation}
        onLocationSelect={onLocationSelect}
        height={height}
      />
    );
  }
  
  console.log('🗺️ Using native MapView');

  const { currentLocation, theme } = useApp();
  const mapRef = useRef<MapView>(null);
  const [mapReady, setMapReady] = useState(false);
  const [followUserLocation, setFollowUserLocation] = useState(true);

  const isDark = theme === 'dark';

  // Default to Sri Lanka center if no location
  const defaultRegion: Region = {
    latitude: 7.8731,
    longitude: 80.7718,
    latitudeDelta: 2.0,
    longitudeDelta: 2.0,
  };

  const initialRegion = currentLocation 
    ? {
        latitude: currentLocation.latitude,
        longitude: currentLocation.longitude,
        latitudeDelta: 0.0922,
        longitudeDelta: 0.0421,
      }
    : defaultRegion;

  const fitToCoordinates = useCallback(() => {
    if (!mapRef.current) return;

    const coordinates = [];
    if (origin) coordinates.push({ latitude: origin.latitude, longitude: origin.longitude });
    if (destination) coordinates.push({ latitude: destination.latitude, longitude: destination.longitude });
    if (currentLocation && showUserLocation) {
      coordinates.push({ latitude: currentLocation.latitude, longitude: currentLocation.longitude });
    }

    if (coordinates.length > 0) {
      mapRef.current.fitToCoordinates(coordinates, {
        edgePadding: { top: 50, right: 50, bottom: 50, left: 50 },
        animated: true,
      });
    }
  }, [origin, destination, currentLocation, showUserLocation]);

  useEffect(() => {
    if (mapReady && origin && destination) {
      fitToCoordinates();
    }
  }, [mapReady, origin, destination, fitToCoordinates]);

  const centerOnUserLocation = () => {
    if (!currentLocation || !mapRef.current) {
      Alert.alert('Location Error', 'Current location not available');
      return;
    }

    mapRef.current.animateToRegion({
      latitude: currentLocation.latitude,
      longitude: currentLocation.longitude,
      latitudeDelta: 0.01,
      longitudeDelta: 0.01,
    }, 1000);
  };

  // Get route coordinates from polyline or generate fallback
  const getRouteCoordinates = () => {
    if (!route?.polyline) {
      // If no polyline, create straight line between origin and destination
      if (origin && destination) {
        return generateStraightLinePolyline(
          { latitude: origin.latitude, longitude: origin.longitude },
          { latitude: destination.latitude, longitude: destination.longitude }
        );
      }
      return [];
    }

    // Check if it's a mock polyline identifier
    if (route.polyline.startsWith('mock_polyline_')) {
      return getMockPolylineCoordinates(route.polyline);
    }

    // Decode actual Google Maps polyline
    try {
      return decodePolyline(route.polyline);
    } catch (error) {
      console.warn('Failed to decode polyline:', error);
      // Fallback to straight line
      if (origin && destination) {
        return generateStraightLinePolyline(
          { latitude: origin.latitude, longitude: origin.longitude },
          { latitude: destination.latitude, longitude: destination.longitude }
        );
      }
      return [];
    }
  };

  const routeCoordinates = getRouteCoordinates();

  const mapStyle = isDark ? [
    {
      "elementType": "geometry",
      "stylers": [{ "color": "#212121" }]
    },
    {
      "elementType": "labels.icon",
      "stylers": [{ "visibility": "off" }]
    },
    {
      "elementType": "labels.text.fill",
      "stylers": [{ "color": "#757575" }]
    },
    {
      "elementType": "labels.text.stroke",
      "stylers": [{ "color": "#212121" }]
    },
    {
      "featureType": "administrative",
      "elementType": "geometry",
      "stylers": [{ "color": "#757575" }]
    },
    {
      "featureType": "road",
      "elementType": "geometry.fill",
      "stylers": [{ "color": "#2c2c2c" }]
    },
    {
      "featureType": "water",
      "elementType": "geometry",
      "stylers": [{ "color": "#000000" }]
    }
  ] : [];

  return (
    <View style={[styles.container, { height }]}>
      <MapView
        ref={mapRef}
        provider={PROVIDER_GOOGLE}
        style={styles.map}
        initialRegion={initialRegion}
        showsUserLocation={showUserLocation}
        showsMyLocationButton={false}
        followsUserLocation={followUserLocation}
        showsTraffic={true}
        showsBuildings={true}
        showsPointsOfInterests={true}
        customMapStyle={mapStyle}
        onMapReady={() => setMapReady(true)}
        onPress={(event) => {
          if (onLocationSelect) {
            onLocationSelect(event.nativeEvent.coordinate);
          }
        }}
      >
        {/* Origin Marker */}
        {origin && (
          <Marker
            coordinate={{ latitude: origin.latitude, longitude: origin.longitude }}
            title="Origin"
            description={origin.address || 'Starting point'}
            pinColor={SriLankanColors.secondary.green}
          >
            <View style={styles.originMarker}>
              <Ionicons name="radio-button-on" size={24} color={SriLankanColors.secondary.green} />
            </View>
          </Marker>
        )}

        {/* Destination Marker */}
        {destination && (
          <Marker
            coordinate={{ latitude: destination.latitude, longitude: destination.longitude }}
            title="Destination"
            description={destination.address || 'Destination point'}
            pinColor={SriLankanColors.primary.saffron}
          >
            <View style={styles.destinationMarker}>
              <Ionicons name="location" size={24} color={SriLankanColors.primary.saffron} />
            </View>
          </Marker>
        )}

        {/* Route Polyline */}
        {routeCoordinates.length > 1 && (
          <Polyline
            coordinates={routeCoordinates}
            strokeColor={SriLankanColors.primary.saffron}
            strokeWidth={4}
            lineDashPattern={[5, 5]}
          />
        )}

        {/* Transit Stops (based on route legs) */}
        {route?.legs?.map((leg, index) => {
          const coordinate = leg.start_location ? {
            latitude: leg.start_location.lat,
            longitude: leg.start_location.lng
          } : null;
          
          if (!coordinate) return null;
          
          const getTransportIcon = (mode: string) => {
            switch (mode.toLowerCase()) {
              case 'bus': return 'bus';
              case 'train': case 'transit': return 'train';
              case 'walking': return 'walk';
              case 'tuk_tuk': return 'car';
              default: return 'location';
            }
          };
          
          return (
            <Marker
              key={`stop-${index}`}
              coordinate={coordinate}
              title={`${leg.travel_mode} - ${leg.duration}`}
              description={leg.summary}
            >
              <View style={styles.transitStopMarker}>
                <Ionicons 
                  name={getTransportIcon(leg.travel_mode)} 
                  size={16} 
                  color="white" 
                />
              </View>
            </Marker>
          );
        })}
      </MapView>

      {/* Map Controls */}
      <View style={styles.controls}>
        <TouchableOpacity 
          style={[styles.controlButton, { backgroundColor: isDark ? '#1f2937' : 'white' }]}
          onPress={centerOnUserLocation}
        >
          <Ionicons name="locate" size={20} color={SriLankanColors.primary.saffron} />
        </TouchableOpacity>
        
        <TouchableOpacity 
          style={[styles.controlButton, { backgroundColor: isDark ? '#1f2937' : 'white' }]}
          onPress={fitToCoordinates}
        >
          <Ionicons name="resize" size={20} color={SriLankanColors.secondary.green} />
        </TouchableOpacity>
        
        <TouchableOpacity 
          style={[styles.controlButton, { backgroundColor: isDark ? '#1f2937' : 'white' }]}
          onPress={() => setFollowUserLocation(!followUserLocation)}
        >
          <Ionicons 
            name={followUserLocation ? "navigate" : "navigate-outline"} 
            size={20} 
            color={followUserLocation ? SriLankanColors.primary.saffron : '#6b7280'} 
          />
        </TouchableOpacity>
      </View>

      {/* Route Info Overlay */}
      {route && (
        <View style={[styles.routeInfo, { backgroundColor: isDark ? '#1f2937' : 'white' }]}>
          <View style={styles.routeInfoRow}>
            <View style={styles.routeInfoItem}>
              <Ionicons name="time" size={16} color="#6b7280" />
              <Text style={[styles.routeInfoText, { color: isDark ? 'white' : '#374151' }]}>
                {route.total_duration}
              </Text>
            </View>
            <View style={styles.routeInfoItem}>
              <Ionicons name="location" size={16} color="#6b7280" />
              <Text style={[styles.routeInfoText, { color: isDark ? 'white' : '#374151' }]}>
                {route.total_distance}
              </Text>
            </View>
            {route.total_cost && (
              <View style={styles.routeInfoItem}>
                <Ionicons name="card" size={16} color="#6b7280" />
                <Text style={[styles.routeInfoText, { color: isDark ? 'white' : '#374151' }]}>
                  LKR {route.total_cost}
                </Text>
              </View>
            )}
          </View>
        </View>
      )}
    </View>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    borderRadius: 16,
    overflow: 'hidden',
  },
  map: {
    flex: 1,
  },
  controls: {
    position: 'absolute',
    top: 16,
    right: 16,
    flexDirection: 'column',
    gap: 8,
  },
  controlButton: {
    width: 44,
    height: 44,
    borderRadius: 22,
    justifyContent: 'center',
    alignItems: 'center',
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 2 },
    shadowOpacity: 0.25,
    shadowRadius: 4,
    elevation: 4,
  },
  originMarker: {
    width: 32,
    height: 32,
    borderRadius: 16,
    backgroundColor: 'white',
    justifyContent: 'center',
    alignItems: 'center',
    borderWidth: 2,
    borderColor: SriLankanColors.secondary.green,
  },
  destinationMarker: {
    width: 32,
    height: 32,
    borderRadius: 16,
    backgroundColor: 'white',
    justifyContent: 'center',
    alignItems: 'center',
    borderWidth: 2,
    borderColor: SriLankanColors.primary.saffron,
  },
  transitStopMarker: {
    width: 24,
    height: 24,
    borderRadius: 12,
    backgroundColor: SriLankanColors.secondary.gold,
    justifyContent: 'center',
    alignItems: 'center',
  },
  routeInfo: {
    position: 'absolute',
    bottom: 16,
    left: 16,
    right: 16,
    borderRadius: 12,
    padding: 12,
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 2 },
    shadowOpacity: 0.25,
    shadowRadius: 4,
    elevation: 4,
  },
  routeInfoRow: {
    flexDirection: 'row',
    justifyContent: 'space-around',
  },
  routeInfoItem: {
    flexDirection: 'row',
    alignItems: 'center',
    gap: 4,
  },
  routeInfoText: {
    fontSize: 12,
    fontWeight: '500',
  },
});