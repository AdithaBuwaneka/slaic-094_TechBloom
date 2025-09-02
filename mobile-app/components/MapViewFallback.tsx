import React, { useState } from 'react';
import { View, Text, TouchableOpacity, StyleSheet, ScrollView, Alert } from 'react-native';
import { Ionicons } from '@expo/vector-icons';
import { useApp } from '@/context/AppContext';
import { SriLankanColors } from '@/constants/SriLankanTheme';
import type { Location, RouteOption } from '@/types';

interface RouteMapFallbackProps {
  origin?: Location;
  destination?: Location;
  route?: RouteOption;
  showUserLocation?: boolean;
  onLocationSelect?: (coordinate: { latitude: number; longitude: number }) => void;
  height?: number;
}

export default function RouteMapFallback({
  origin,
  destination,
  route,
  showUserLocation = true,
  onLocationSelect,
  height = 300,
}: RouteMapFallbackProps) {
  const { currentLocation, theme, getCurrentLocation } = useApp();
  const [isGettingLocation, setIsGettingLocation] = useState(false);

  const isDark = theme === 'dark';

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

  const handleRandomLocation = () => {
    // Generate random Sri Lankan coordinates for demo
    const sriLankanBounds = {
      north: 9.8315,
      south: 5.9188,
      east: 81.8789,
      west: 79.6528,
    };

    const randomLat = sriLankanBounds.south + 
      Math.random() * (sriLankanBounds.north - sriLankanBounds.south);
    const randomLng = sriLankanBounds.west + 
      Math.random() * (sriLankanBounds.east - sriLankanBounds.west);

    if (onLocationSelect) {
      onLocationSelect({
        latitude: randomLat,
        longitude: randomLng,
      });
    }
  };

  return (
    <View style={[styles.container, { height }, { backgroundColor: isDark ? '#1f2937' : '#f3f4f6' }]}>
      {/* Map Placeholder */}
      <View style={[styles.mapPlaceholder, { backgroundColor: isDark ? '#374151' : '#e5e7eb' }]}>
        <Ionicons name="map-outline" size={64} color={isDark ? '#9ca3af' : '#6b7280'} />
        <Text style={[styles.placeholderTitle, { color: isDark ? '#f9fafb' : '#374151' }]}>
          Map View (Development Build Required)
        </Text>
        <Text style={[styles.placeholderSubtitle, { color: isDark ? '#d1d5db' : '#6b7280' }]}>
          Full map functionality requires a development build
        </Text>
        <Text style={[styles.placeholderInfo, { color: isDark ? '#9ca3af' : '#9ca3af' }]}>
          Maps are not fully supported in Expo Go
        </Text>
      </View>

      {/* Location Information Cards */}
      <ScrollView style={styles.infoContainer} showsVerticalScrollIndicator={false}>
        {/* Current Location */}
        {showUserLocation && (
          <View style={[styles.locationCard, { backgroundColor: isDark ? '#374151' : 'white' }]}>
            <View style={styles.cardHeader}>
              <View style={styles.locationIcon}>
                <Ionicons name="locate" size={20} color={SriLankanColors.secondary.green} />
              </View>
              <Text style={[styles.cardTitle, { color: isDark ? '#f9fafb' : '#374151' }]}>
                Current Location
              </Text>
            </View>
            {currentLocation ? (
              <View style={styles.coordinateContainer}>
                <Text style={[styles.coordinateText, { color: isDark ? '#d1d5db' : '#6b7280' }]}>
                  Lat: {currentLocation.latitude.toFixed(6)}
                </Text>
                <Text style={[styles.coordinateText, { color: isDark ? '#d1d5db' : '#6b7280' }]}>
                  Lng: {currentLocation.longitude.toFixed(6)}
                </Text>
                {currentLocation.address && (
                  <Text style={[styles.addressText, { color: isDark ? '#9ca3af' : '#9ca3af' }]}>
                    {currentLocation.address}
                  </Text>
                )}
              </View>
            ) : (
              <TouchableOpacity
                style={[styles.actionButton, { backgroundColor: SriLankanColors.secondary.green }]}
                onPress={handleGetLocation}
                disabled={isGettingLocation}
              >
                <Ionicons name="location" size={16} color="white" />
                <Text style={styles.buttonText}>
                  {isGettingLocation ? 'Getting Location...' : 'Get Current Location'}
                </Text>
              </TouchableOpacity>
            )}
          </View>
        )}

        {/* Origin */}
        {origin && (
          <View style={[styles.locationCard, { backgroundColor: isDark ? '#374151' : 'white' }]}>
            <View style={styles.cardHeader}>
              <View style={[styles.locationIcon, { backgroundColor: `${SriLankanColors.secondary.green}20` }]}>
                <Ionicons name="radio-button-on" size={20} color={SriLankanColors.secondary.green} />
              </View>
              <Text style={[styles.cardTitle, { color: isDark ? '#f9fafb' : '#374151' }]}>
                Origin
              </Text>
            </View>
            <View style={styles.coordinateContainer}>
              <Text style={[styles.coordinateText, { color: isDark ? '#d1d5db' : '#6b7280' }]}>
                Lat: {origin.latitude.toFixed(6)}
              </Text>
              <Text style={[styles.coordinateText, { color: isDark ? '#d1d5db' : '#6b7280' }]}>
                Lng: {origin.longitude.toFixed(6)}
              </Text>
              {origin.address && (
                <Text style={[styles.addressText, { color: isDark ? '#9ca3af' : '#9ca3af' }]}>
                  {origin.address}
                </Text>
              )}
            </View>
          </View>
        )}

        {/* Destination */}
        {destination && (
          <View style={[styles.locationCard, { backgroundColor: isDark ? '#374151' : 'white' }]}>
            <View style={styles.cardHeader}>
              <View style={[styles.locationIcon, { backgroundColor: `${SriLankanColors.primary.saffron}20` }]}>
                <Ionicons name="location" size={20} color={SriLankanColors.primary.saffron} />
              </View>
              <Text style={[styles.cardTitle, { color: isDark ? '#f9fafb' : '#374151' }]}>
                Destination
              </Text>
            </View>
            <View style={styles.coordinateContainer}>
              <Text style={[styles.coordinateText, { color: isDark ? '#d1d5db' : '#6b7280' }]}>
                Lat: {destination.latitude.toFixed(6)}
              </Text>
              <Text style={[styles.coordinateText, { color: isDark ? '#d1d5db' : '#6b7280' }]}>
                Lng: {destination.longitude.toFixed(6)}
              </Text>
              {destination.address && (
                <Text style={[styles.addressText, { color: isDark ? '#9ca3af' : '#9ca3af' }]}>
                  {destination.address}
                </Text>
              )}
            </View>
          </View>
        )}

        {/* Route Information */}
        {route && (
          <View style={[styles.locationCard, { backgroundColor: isDark ? '#374151' : 'white' }]}>
            <View style={styles.cardHeader}>
              <View style={[styles.locationIcon, { backgroundColor: `${SriLankanColors.primary.saffron}20` }]}>
                <Ionicons name="trail-sign" size={20} color={SriLankanColors.primary.saffron} />
              </View>
              <Text style={[styles.cardTitle, { color: isDark ? '#f9fafb' : '#374151' }]}>
                Route Details
              </Text>
            </View>
            <View style={styles.routeDetails}>
              <View style={styles.routeDetailRow}>
                <Ionicons name="time" size={16} color="#6b7280" />
                <Text style={[styles.routeDetailText, { color: isDark ? '#d1d5db' : '#6b7280' }]}>
                  Duration: {route.total_duration}
                </Text>
              </View>
              <View style={styles.routeDetailRow}>
                <Ionicons name="resize" size={16} color="#6b7280" />
                <Text style={[styles.routeDetailText, { color: isDark ? '#d1d5db' : '#6b7280' }]}>
                  Distance: {route.total_distance}
                </Text>
              </View>
              {route.total_cost && (
                <View style={styles.routeDetailRow}>
                  <Ionicons name="card" size={16} color="#6b7280" />
                  <Text style={[styles.routeDetailText, { color: isDark ? '#d1d5db' : '#6b7280' }]}>
                    Cost: LKR {route.total_cost}
                  </Text>
                </View>
              )}
              {route.legs && route.legs.length > 0 && (
                <View style={styles.legsContainer}>
                  <Text style={[styles.legsTitle, { color: isDark ? '#f9fafb' : '#374151' }]}>
                    Route Steps:
                  </Text>
                  {route.legs.map((leg, index) => (
                    <View key={index} style={styles.legItem}>
                      <Ionicons
                        name={
                          leg.transport_mode === 'bus' ? 'bus' :
                          leg.transport_mode === 'train' ? 'train' :
                          leg.transport_mode === 'walking' ? 'walk' : 'arrow-forward'
                        }
                        size={14}
                        color={SriLankanColors.secondary.gold}
                      />
                      <Text style={[styles.legText, { color: isDark ? '#9ca3af' : '#9ca3af' }]}>
                        {leg.instruction || `${leg.transport_mode} - ${leg.duration}`}
                      </Text>
                    </View>
                  ))}
                </View>
              )}
            </View>
          </View>
        )}

        {/* Demo Actions */}
        <View style={[styles.locationCard, { backgroundColor: isDark ? '#374151' : 'white' }]}>
          <View style={styles.cardHeader}>
            <View style={[styles.locationIcon, { backgroundColor: `${SriLankanColors.secondary.gold}20` }]}>
              <Ionicons name="settings" size={20} color={SriLankanColors.secondary.gold} />
            </View>
            <Text style={[styles.cardTitle, { color: isDark ? '#f9fafb' : '#374151' }]}>
              Demo Actions
            </Text>
          </View>
          <View style={styles.actionContainer}>
            <TouchableOpacity
              style={[styles.actionButton, { backgroundColor: SriLankanColors.secondary.gold }]}
              onPress={handleRandomLocation}
            >
              <Ionicons name="shuffle" size={16} color="white" />
              <Text style={styles.buttonText}>Random Sri Lankan Location</Text>
            </TouchableOpacity>
          </View>
        </View>
      </ScrollView>

      {/* Development Build Info */}
      <View style={[styles.devBuildInfo, { backgroundColor: isDark ? '#1e40af' : '#3b82f6' }]}>
        <Ionicons name="information-circle" size={16} color="white" />
        <Text style={styles.devBuildText}>
          Install development build for full map functionality
        </Text>
      </View>
    </View>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    borderRadius: 16,
    overflow: 'hidden',
  },
  mapPlaceholder: {
    flex: 0.4,
    justifyContent: 'center',
    alignItems: 'center',
    margin: 16,
    borderRadius: 12,
    borderWidth: 2,
    borderStyle: 'dashed',
    borderColor: '#d1d5db',
  },
  placeholderTitle: {
    fontSize: 16,
    fontWeight: '600',
    marginTop: 12,
    textAlign: 'center',
  },
  placeholderSubtitle: {
    fontSize: 14,
    marginTop: 4,
    textAlign: 'center',
  },
  placeholderInfo: {
    fontSize: 12,
    marginTop: 8,
    textAlign: 'center',
    fontStyle: 'italic',
  },
  infoContainer: {
    flex: 0.6,
    padding: 16,
  },
  locationCard: {
    borderRadius: 12,
    padding: 16,
    marginBottom: 12,
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 2 },
    shadowOpacity: 0.1,
    shadowRadius: 4,
    elevation: 3,
  },
  cardHeader: {
    flexDirection: 'row',
    alignItems: 'center',
    marginBottom: 12,
  },
  locationIcon: {
    width: 32,
    height: 32,
    borderRadius: 16,
    backgroundColor: '#f3f4f6',
    justifyContent: 'center',
    alignItems: 'center',
    marginRight: 12,
  },
  cardTitle: {
    fontSize: 16,
    fontWeight: '600',
  },
  coordinateContainer: {
    marginLeft: 44,
  },
  coordinateText: {
    fontSize: 14,
    fontFamily: 'monospace',
    marginBottom: 2,
  },
  addressText: {
    fontSize: 12,
    marginTop: 4,
    lineHeight: 16,
  },
  actionContainer: {
    marginLeft: 44,
  },
  actionButton: {
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'center',
    paddingVertical: 8,
    paddingHorizontal: 16,
    borderRadius: 8,
    marginTop: 8,
  },
  buttonText: {
    color: 'white',
    fontSize: 14,
    fontWeight: '500',
    marginLeft: 6,
  },
  routeDetails: {
    marginLeft: 44,
  },
  routeDetailRow: {
    flexDirection: 'row',
    alignItems: 'center',
    marginBottom: 6,
  },
  routeDetailText: {
    fontSize: 14,
    marginLeft: 8,
  },
  legsContainer: {
    marginTop: 12,
    paddingTop: 12,
    borderTopWidth: 1,
    borderTopColor: '#e5e7eb',
  },
  legsTitle: {
    fontSize: 14,
    fontWeight: '600',
    marginBottom: 8,
  },
  legItem: {
    flexDirection: 'row',
    alignItems: 'center',
    marginBottom: 4,
  },
  legText: {
    fontSize: 12,
    marginLeft: 8,
    flex: 1,
  },
  devBuildInfo: {
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'center',
    paddingVertical: 8,
    paddingHorizontal: 12,
  },
  devBuildText: {
    color: 'white',
    fontSize: 12,
    fontWeight: '500',
    marginLeft: 6,
  },
});