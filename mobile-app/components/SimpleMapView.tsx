import React, { useState } from 'react';
import { View, Text, TouchableOpacity, StyleSheet, ScrollView, Alert } from 'react-native';
import { Ionicons } from '@expo/vector-icons';
import { useApp } from '@/context/AppContext';
import { SriLankanColors } from '@/constants/SriLankanTheme';
import type { Location, RouteOption } from '@/types';

interface SimpleMapViewProps {
  origin?: Location;
  destination?: Location;
  route?: RouteOption;
  showUserLocation?: boolean;
  onLocationSelect?: (coordinate: { latitude: number; longitude: number }) => void;
  height?: number;
}

export default function SimpleMapView({
  origin,
  destination,
  route,
  showUserLocation = true,
  onLocationSelect,
  height = 400,
}: SimpleMapViewProps) {
  const { currentLocation, theme, getCurrentLocation } = useApp();
  const [isGettingLocation, setIsGettingLocation] = useState(false);
  const isDark = theme === 'dark';
  
  console.log('🗺️ SimpleMapView rendering with:', { origin, destination, route, currentLocation });

  const handleGetLocation = async () => {
    setIsGettingLocation(true);
    try {
      await getCurrentLocation();
      if (onLocationSelect && currentLocation) {
        onLocationSelect({
          latitude: currentLocation.latitude,
          longitude: currentLocation.longitude,
        });
      }
    } catch (error) {
      Alert.alert('Location Error', 'Unable to get current location');
    } finally {
      setIsGettingLocation(false);
    }
  };

  const generateMapUrl = () => {
    if (!origin && !destination) {
      return `https://www.google.com/maps/embed?pb=!1m14!1m12!1m3!1d2025756.7842871!2d80.7718!3d7.8731!2m3!1f0!2f0!3f0!3m2!1i1024!2i768!4f13.1!5e0!3m2!1sen!2slk`;
    }

    const waypoints: string[] = [];
    if (origin) {
      waypoints.push(`${origin.latitude},${origin.longitude}`);
    }
    if (destination && origin) {
      waypoints.push(`${destination.latitude},${destination.longitude}`);
    }

    if (waypoints.length === 0) return '';

    // Google Maps static image URL
    const apiKey = 'AIzaSyAcWZ_Oz910MrEwgz6J7-tjKcspQ0MmMYA';
    const size = '400x300';
    const zoom = waypoints.length === 1 ? 15 : 'auto';
    
    let markers = '';
    if (origin) {
      markers += `&markers=color:green%7Clabel:A%7C${origin.latitude},${origin.longitude}`;
    }
    if (destination) {
      markers += `&markers=color:red%7Clabel:B%7C${destination.latitude},${destination.longitude}`;
    }

    let path = '';
    if (origin && destination) {
      path = `&path=color:0x0000ff%7Cweight:3%7C${origin.latitude},${origin.longitude}%7C${destination.latitude},${destination.longitude}`;
    }

    return `https://maps.googleapis.com/maps/api/staticmap?size=${size}&zoom=${zoom}${markers}${path}&key=${apiKey}`;
  };

  const openInGoogleMaps = () => {
    let url = 'https://www.google.com/maps/';
    
    if (origin && destination) {
      url += `dir/${origin.latitude},${origin.longitude}/${destination.latitude},${destination.longitude}`;
    } else if (origin) {
      url += `@${origin.latitude},${origin.longitude},15z`;
    } else if (destination) {
      url += `@${destination.latitude},${destination.longitude},15z`;
    }
    
    // In a real app, you would use Linking.openURL(url)
    Alert.alert('Open in Google Maps', `Would open: ${url}`);
  };

  return (
    <View style={[styles.container, { height, backgroundColor: isDark ? '#1f2937' : '#f9fafb' }]}>
      <View style={[styles.mapContainer, { backgroundColor: isDark ? '#374151' : '#ffffff' }]}>
        <View style={styles.mapHeader}>
          <View style={styles.mapTitle}>
            <Ionicons name="map" size={20} color={SriLankanColors.primary.saffron} />
            <Text style={[styles.mapTitleText, { color: isDark ? '#f9fafb' : '#374151' }]}>
              Route Overview
            </Text>
          </View>
          <TouchableOpacity
            style={styles.fullMapButton}
            onPress={openInGoogleMaps}
          >
            <Ionicons name="open-outline" size={16} color={SriLankanColors.primary.saffron} />
            <Text style={[styles.fullMapText, { color: SriLankanColors.primary.saffron }]}>
              Open Map
            </Text>
          </TouchableOpacity>
        </View>

        {/* Visual Route Representation */}
        <View style={[styles.routeVisualization, { backgroundColor: isDark ? '#4b5563' : '#f3f4f6' }]}>
          <View style={styles.routeLine}>
            {/* Origin Point */}
            <View style={styles.pointContainer}>
              <View style={[styles.originPoint, { backgroundColor: SriLankanColors.secondary.green }]}>
                <Ionicons name="radio-button-on" size={16} color="white" />
              </View>
              <Text style={[styles.pointLabel, { color: isDark ? '#d1d5db' : '#6b7280' }]}>
                {origin?.address || 'Origin'}
              </Text>
            </View>

            {/* Route Path */}
            <View style={styles.pathContainer}>
              <View style={[styles.pathLine, { backgroundColor: SriLankanColors.primary.saffron }]} />
              {route && (
                <View style={styles.routeInfo}>
                  <Text style={[styles.routeInfoText, { color: isDark ? '#9ca3af' : '#6b7280' }]}>
                    {route.total_duration} • {route.total_distance}
                    {route.total_cost && ` • LKR ${route.total_cost}`}
                  </Text>
                </View>
              )}
            </View>

            {/* Destination Point */}
            <View style={styles.pointContainer}>
              <View style={[styles.destinationPoint, { backgroundColor: SriLankanColors.primary.saffron }]}>
                <Ionicons name="location" size={16} color="white" />
              </View>
              <Text style={[styles.pointLabel, { color: isDark ? '#d1d5db' : '#6b7280' }]}>
                {destination?.address || 'Destination'}
              </Text>
            </View>
          </View>
        </View>

        {/* Map Controls */}
        <View style={styles.mapControls}>
          {showUserLocation && (
            <TouchableOpacity
              style={[styles.controlButton, { backgroundColor: isDark ? '#4b5563' : '#ffffff' }]}
              onPress={handleGetLocation}
              disabled={isGettingLocation}
            >
              <Ionicons 
                name="locate" 
                size={16} 
                color={isGettingLocation ? '#9ca3af' : SriLankanColors.secondary.green} 
              />
              <Text style={[styles.controlButtonText, { color: isDark ? '#d1d5db' : '#374151' }]}>
                {isGettingLocation ? 'Locating...' : 'My Location'}
              </Text>
            </TouchableOpacity>
          )}
          
          {/* Debug button */}
          <TouchableOpacity
            style={[styles.controlButton, { backgroundColor: '#3b82f6', marginLeft: 8 }]}
            onPress={() => {
              console.log('🐛 Debug Map State:', {
                origin,
                destination, 
                route,
                currentLocation,
                showUserLocation
              });
              Alert.alert('Map Debug', `Origin: ${origin ? 'Set' : 'None'}\nDest: ${destination ? 'Set' : 'None'}\nRoute: ${route ? 'Set' : 'None'}\nLocation: ${currentLocation ? 'Set' : 'None'}`);
            }}
          >
            <Ionicons name="bug" size={16} color="white" />
            <Text style={[styles.controlButtonText, { color: 'white' }]}>Debug</Text>
          </TouchableOpacity>
        </View>
      </View>

      {/* Location Details */}
      <ScrollView style={styles.detailsContainer} showsVerticalScrollIndicator={false}>
        {/* Current Location Card */}
        {showUserLocation && currentLocation && (
          <View style={[styles.locationCard, { backgroundColor: isDark ? '#374151' : '#ffffff' }]}>
            <View style={styles.cardHeader}>
              <Ionicons name="locate" size={18} color={SriLankanColors.secondary.green} />
              <Text style={[styles.cardTitle, { color: isDark ? '#f9fafb' : '#374151' }]}>
                Current Location
              </Text>
            </View>
            <Text style={[styles.locationText, { color: isDark ? '#9ca3af' : '#6b7280' }]}>
              {currentLocation.address || `${currentLocation.latitude.toFixed(4)}, ${currentLocation.longitude.toFixed(4)}`}
            </Text>
          </View>
        )}

        {/* Route Steps */}
        {route?.legs && route.legs.length > 0 && (
          <View style={[styles.locationCard, { backgroundColor: isDark ? '#374151' : '#ffffff' }]}>
            <View style={styles.cardHeader}>
              <Ionicons name="list" size={18} color={SriLankanColors.primary.saffron} />
              <Text style={[styles.cardTitle, { color: isDark ? '#f9fafb' : '#374151' }]}>
                Journey Steps
              </Text>
            </View>
            {route.legs.map((leg, index) => (
              <View key={index} style={styles.legItem}>
                <View style={styles.stepNumber}>
                  <Text style={styles.stepNumberText}>{index + 1}</Text>
                </View>
                <View style={styles.stepContent}>
                  <View style={styles.stepHeader}>
                    <Ionicons 
                      name={
                        leg.travel_mode.toLowerCase() === 'walking' ? 'walk' :
                        leg.travel_mode.toLowerCase() === 'bus' ? 'bus' :
                        leg.travel_mode.toLowerCase() === 'train' ? 'train' :
                        'arrow-forward'
                      } 
                      size={16} 
                      color={SriLankanColors.secondary.gold} 
                    />
                    <Text style={[styles.stepMode, { color: isDark ? '#d1d5db' : '#374151' }]}>
                      {leg.travel_mode} • {leg.duration}
                    </Text>
                  </View>
                  <Text style={[styles.stepDescription, { color: isDark ? '#9ca3af' : '#6b7280' }]}>
                    {leg.summary}
                  </Text>
                </View>
              </View>
            ))}
          </View>
        )}

        {/* Coordinates Info */}
        {(origin || destination) && (
          <View style={[styles.locationCard, { backgroundColor: isDark ? '#374151' : '#ffffff' }]}>
            <View style={styles.cardHeader}>
              <Ionicons name="information-circle" size={18} color={SriLankanColors.secondary.gold} />
              <Text style={[styles.cardTitle, { color: isDark ? '#f9fafb' : '#374151' }]}>
                Coordinates
              </Text>
            </View>
            {origin && (
              <View style={styles.coordRow}>
                <Text style={[styles.coordLabel, { color: isDark ? '#9ca3af' : '#6b7280' }]}>
                  Origin:
                </Text>
                <Text style={[styles.coordValue, { color: isDark ? '#d1d5db' : '#374151' }]}>
                  {origin.latitude.toFixed(6)}, {origin.longitude.toFixed(6)}
                </Text>
              </View>
            )}
            {destination && (
              <View style={styles.coordRow}>
                <Text style={[styles.coordLabel, { color: isDark ? '#9ca3af' : '#6b7280' }]}>
                  Destination:
                </Text>
                <Text style={[styles.coordValue, { color: isDark ? '#d1d5db' : '#374151' }]}>
                  {destination.latitude.toFixed(6)}, {destination.longitude.toFixed(6)}
                </Text>
              </View>
            )}
          </View>
        )}
        
        {/* Test Route Button */}
        <View style={[styles.locationCard, { backgroundColor: isDark ? '#374151' : '#ffffff' }]}>
          <TouchableOpacity
            style={[styles.testButton, { backgroundColor: SriLankanColors.primary.saffron }]}
            onPress={() => {
              console.log('🎯 Test route button pressed');
              if (onLocationSelect) {
                // Set Colombo as origin
                onLocationSelect({
                  latitude: 6.9271,
                  longitude: 79.8612,
                });
                
                // Set Kandy as destination after a short delay
                setTimeout(() => {
                  if (onLocationSelect) {
                    onLocationSelect({
                      latitude: 7.2906,
                      longitude: 80.6337,
                    });
                  }
                }, 1000);
              }
            }}
          >
            <Ionicons name="map" size={16} color="white" />
            <Text style={[styles.buttonText, { color: 'white' }]}>Test Route: Colombo → Kandy</Text>
          </TouchableOpacity>
        </View>
      </ScrollView>
    </View>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    borderRadius: 16,
    overflow: 'hidden',
    minHeight: 300, // Ensure minimum height
  },
  mapContainer: {
    minHeight: 200, // Changed from flex to fixed minimum height
    margin: 12,
    borderRadius: 12,
    padding: 16,
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 2 },
    shadowOpacity: 0.1,
    shadowRadius: 4,
    elevation: 3,
  },
  mapHeader: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    marginBottom: 12,
  },
  mapTitle: {
    flexDirection: 'row',
    alignItems: 'center',
  },
  mapTitleText: {
    fontSize: 16,
    fontWeight: '600',
    marginLeft: 8,
  },
  fullMapButton: {
    flexDirection: 'row',
    alignItems: 'center',
    paddingVertical: 4,
    paddingHorizontal: 8,
    borderRadius: 6,
    borderWidth: 1,
    borderColor: SriLankanColors.primary.saffron,
  },
  fullMapText: {
    fontSize: 12,
    fontWeight: '500',
    marginLeft: 4,
  },
  routeVisualization: {
    flex: 1,
    borderRadius: 8,
    padding: 16,
  },
  routeLine: {
    flex: 1,
    justifyContent: 'space-between',
  },
  pointContainer: {
    alignItems: 'center',
  },
  originPoint: {
    width: 32,
    height: 32,
    borderRadius: 16,
    justifyContent: 'center',
    alignItems: 'center',
  },
  destinationPoint: {
    width: 32,
    height: 32,
    borderRadius: 16,
    justifyContent: 'center',
    alignItems: 'center',
  },
  pointLabel: {
    fontSize: 12,
    fontWeight: '500',
    marginTop: 4,
    textAlign: 'center',
    maxWidth: 120,
  },
  pathContainer: {
    flex: 1,
    alignItems: 'center',
    justifyContent: 'center',
    marginVertical: 16,
  },
  pathLine: {
    width: 3,
    flex: 1,
    borderRadius: 1.5,
  },
  routeInfo: {
    position: 'absolute',
    backgroundColor: 'rgba(255, 255, 255, 0.9)',
    paddingHorizontal: 8,
    paddingVertical: 4,
    borderRadius: 4,
  },
  routeInfoText: {
    fontSize: 10,
    fontWeight: '500',
  },
  mapControls: {
    flexDirection: 'row',
    marginTop: 12,
  },
  controlButton: {
    flexDirection: 'row',
    alignItems: 'center',
    paddingVertical: 8,
    paddingHorizontal: 12,
    borderRadius: 8,
    borderWidth: 1,
    borderColor: '#e5e7eb',
  },
  controlButtonText: {
    fontSize: 12,
    fontWeight: '500',
    marginLeft: 4,
  },
  detailsContainer: {
    flex: 1, // Take remaining space
    padding: 12,
  },
  locationCard: {
    borderRadius: 12,
    padding: 16,
    marginBottom: 12,
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 1 },
    shadowOpacity: 0.1,
    shadowRadius: 2,
    elevation: 2,
  },
  cardHeader: {
    flexDirection: 'row',
    alignItems: 'center',
    marginBottom: 8,
  },
  cardTitle: {
    fontSize: 14,
    fontWeight: '600',
    marginLeft: 8,
  },
  locationText: {
    fontSize: 14,
    lineHeight: 20,
  },
  legItem: {
    flexDirection: 'row',
    marginBottom: 12,
  },
  stepNumber: {
    width: 20,
    height: 20,
    borderRadius: 10,
    backgroundColor: SriLankanColors.primary.saffron,
    justifyContent: 'center',
    alignItems: 'center',
    marginRight: 12,
  },
  stepNumberText: {
    color: 'white',
    fontSize: 10,
    fontWeight: '600',
  },
  stepContent: {
    flex: 1,
  },
  stepHeader: {
    flexDirection: 'row',
    alignItems: 'center',
    marginBottom: 4,
  },
  stepMode: {
    fontSize: 12,
    fontWeight: '500',
    marginLeft: 6,
  },
  stepDescription: {
    fontSize: 12,
    lineHeight: 16,
  },
  coordRow: {
    flexDirection: 'row',
    marginBottom: 6,
  },
  coordLabel: {
    fontSize: 12,
    fontWeight: '500',
    width: 80,
  },
  coordValue: {
    fontSize: 12,
    fontFamily: 'monospace',
    flex: 1,
  },
  testButton: {
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'center',
    paddingVertical: 12,
    paddingHorizontal: 16,
    borderRadius: 8,
    marginTop: 8,
  },
  buttonText: {
    fontSize: 14,
    fontWeight: '500',
    marginLeft: 6,
  },
});