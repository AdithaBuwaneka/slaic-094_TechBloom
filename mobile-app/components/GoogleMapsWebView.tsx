import React, { useRef, useEffect } from 'react';
import { View, StyleSheet, ActivityIndicator, Text } from 'react-native';
import { WebView } from 'react-native-webview';
import type { Location, RouteOption } from '@/types';

interface GoogleMapsWebViewProps {
  origin?: Location;
  destination?: Location;
  route?: RouteOption;
  showUserLocation?: boolean;
  onLocationSelect?: (coordinate: { latitude: number; longitude: number }) => void;
  height?: number;
}

export default function GoogleMapsWebView({
  origin,
  destination,
  route,
  showUserLocation = true,
  height,
}: GoogleMapsWebViewProps) {
  const webViewRef = useRef<WebView>(null);

  const generateMapHTML = () => {
    const apiKey = 'AIzaSyAcWZ_Oz910MrEwgz6J7-tjKcspQ0MmMYA';
    
    // Default to Sri Lanka center if no points
    const center = origin ? 
      `${origin.latitude}, ${origin.longitude}` : 
      '7.8731, 80.7718'; // Sri Lanka center
    
    const zoom = (origin && destination) ? 10 : 12;
    
    let markers = '';
    if (origin) {
      markers += `
        new google.maps.Marker({
          position: { lat: ${origin.latitude}, lng: ${origin.longitude} },
          map: map,
          title: 'Origin: ${origin.address || 'Starting Point'}',
          icon: {
            url: 'http://maps.google.com/mapfiles/ms/icons/green-dot.png'
          }
        });
      `;
    }
    
    if (destination) {
      markers += `
        new google.maps.Marker({
          position: { lat: ${destination.latitude}, lng: ${destination.longitude} },
          map: map,
          title: 'Destination: ${destination.address || 'End Point'}',
          icon: {
            url: 'http://maps.google.com/mapfiles/ms/icons/red-dot.png'
          }
        });
      `;
    }
    
    let routeCode = '';
    console.log('🗺️ GoogleMapsWebView received route:', route);
    console.log('🗺️ Route polyline:', route?.polyline);
    
    if (route && route.polyline && route.polyline.trim() !== '') {
      console.log('🛤️ Drawing route with polyline:', route.polyline);
      console.log('🛤️ Polyline length:', route.polyline.length);
      
      // Always use Google polyline decoding for proper routes
      routeCode = `
        function decodePolyline(encoded) {
          if (!encoded || typeof encoded !== 'string') {
            console.warn('⚠️ Invalid polyline string:', encoded);
            return [];
          }
          
          const poly = [];
          let index = 0;
          const len = encoded.length;
          let lat = 0, lng = 0;
          
          try {
            while (index < len) {
              let b, shift = 0, result = 0;
              // Decode latitude
              do {
                if (index >= len) break;
                b = encoded.charCodeAt(index++) - 63;
                result |= (b & 0x1f) << shift;
                shift += 5;
              } while (b >= 0x20);
              const dlat = ((result & 1) ? ~(result >> 1) : (result >> 1));
              lat += dlat;
              
              // Reset for longitude
              shift = 0;
              result = 0;
              // Decode longitude
              do {
                if (index >= len) break;
                b = encoded.charCodeAt(index++) - 63;
                result |= (b & 0x1f) << shift;
                shift += 5;
              } while (b >= 0x20);
              const dlng = ((result & 1) ? ~(result >> 1) : (result >> 1));
              lng += dlng;
              
              // Convert to decimal degrees and add to path
              const point = { 
                lat: lat / 1e5, 
                lng: lng / 1e5 
              };
              poly.push(point);
            }
            
            console.log('✅ Successfully decoded', poly.length, 'polyline points');
            return poly;
          } catch (error) {
            console.error('❌ Polyline decoding error:', error);
            return [];
          }
        }
        
        try {
          console.log('🔄 Decoding polyline: ${route.polyline}');
          const decodedPath = decodePolyline('${route.polyline}');
          console.log('✅ Decoded', decodedPath.length, 'points');
          
          if (decodedPath.length > 0) {
            const routePolyline = new google.maps.Polyline({
              path: decodedPath,
              geodesic: false,  // This ensures road-following curves, not straight earth curves
              strokeColor: '#FF8C00',
              strokeOpacity: 0.9,
              strokeWeight: 5,
              map: map
            });
            
            // Add direction arrows
            const icons = [{
              icon: {
                path: google.maps.SymbolPath.FORWARD_CLOSED_ARROW,
                scale: 3,
                strokeColor: '#FF8C00'
              },
              offset: '50%',
              repeat: '100px'
            }];
            routePolyline.set('icons', icons);
            
            console.log('✅ Route polyline drawn');
          } else {
            console.warn('⚠️ No points decoded from polyline');
          }
        } catch (error) {
          console.error('❌ Polyline decode error:', error);
        }
      `;
    } else if (origin && destination) {
      console.log('⚠️ No polyline provided, falling back to Google Directions API');
      // If no route polyline, try Google Directions API
      routeCode = `
        const directionsService = new google.maps.DirectionsService();
        const directionsRenderer = new google.maps.DirectionsRenderer({
          polylineOptions: {
            strokeColor: '#FF8C00',
            strokeOpacity: 0.8,
            strokeWeight: 4
          },
          suppressMarkers: true // We already have custom markers
        });
        
        directionsRenderer.setMap(map);
        
        // Try multiple travel modes
        const tryDirections = async () => {
          // First try transit
          try {
            const transitRequest = {
              origin: { lat: ${origin.latitude}, lng: ${origin.longitude} },
              destination: { lat: ${destination.latitude}, lng: ${destination.longitude} },
              travelMode: google.maps.TravelMode.TRANSIT,
              transitOptions: {
                modes: [google.maps.TransitMode.BUS, google.maps.TransitMode.RAIL],
                routingPreference: google.maps.TransitRoutePreference.FEWER_TRANSFERS
              }
            };
            
            directionsService.route(transitRequest, (result, status) => {
              if (status === 'OK') {
                directionsRenderer.setDirections(result);
                console.log('✅ Transit route found');
              } else {
                console.log('⚠️ Transit failed, trying driving route');
                // Fallback to driving
                const drivingRequest = {
                  origin: { lat: ${origin.latitude}, lng: ${origin.longitude} },
                  destination: { lat: ${destination.latitude}, lng: ${destination.longitude} },
                  travelMode: google.maps.TravelMode.DRIVING
                };
                
                directionsService.route(drivingRequest, (result, status) => {
                  if (status === 'OK') {
                    directionsRenderer.setDirections(result);
                    console.log('✅ Driving route found');
                  } else {
                    console.log('❌ All routing failed, drawing geodesic line');
                    // Final fallback: geodesic line (curved, not straight)
                    // Create a basic straight line as last resort (this should rarely be used)
                    new google.maps.Polyline({
                      path: [
                        { lat: ${origin.latitude}, lng: ${origin.longitude} },
                        { lat: ${destination.latitude}, lng: ${destination.longitude} }
                      ],
                      geodesic: false,  // Use straight line rather than curved earth line
                      strokeColor: '#FF8C00',
                      strokeOpacity: 0.6,
                      strokeWeight: 3,
                      strokeDashArray: [10, 10],  // Dashed to indicate it's not a real route
                      icons: [{
                        icon: { path: google.maps.SymbolPath.FORWARD_CLOSED_ARROW },
                        offset: '100%'
                      }],
                      map: map
                    });
                    console.log('⚠️ Using fallback straight line - no route found');
                  }
                });
              }
            });
          } catch (error) {
            console.error('Directions error:', error);
          }
        };
        
        tryDirections();
      `;
    }

    return `
      <!DOCTYPE html>
      <html>
      <head>
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <style>
          body, html { 
            margin: 0; 
            padding: 0; 
            height: 100%; 
            font-family: Arial, sans-serif;
          }
          #map { 
            height: 100%; 
            width: 100%; 
          }
          .info-panel {
            position: absolute;
            top: 10px;
            left: 10px;
            background: white;
            padding: 10px;
            border-radius: 8px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.3);
            font-size: 12px;
            z-index: 1000;
            max-width: 200px;
          }
          .loading {
            position: absolute;
            top: 50%;
            left: 50%;
            transform: translate(-50%, -50%);
            background: white;
            padding: 20px;
            border-radius: 8px;
            text-align: center;
          }
        </style>
      </head>
      <body>
        <div class="loading" id="loading">
          🗺️ Loading Google Maps...
        </div>
        
        <div class="info-panel">
          <strong>🇱🇰 Sri Lankan Transit</strong><br>
          ${origin ? `📍 From: ${origin.address}<br>` : ''}
          ${destination ? `🎯 To: ${destination.address}<br>` : ''}
          <small>Powered by Google Maps</small>
        </div>
        
        <div id="map"></div>
        
        <script async defer 
          src="https://maps.googleapis.com/maps/api/js?key=${apiKey}&callback=initMap&libraries=geometry">
        </script>
        
        <script>
          function initMap() {
            document.getElementById('loading').style.display = 'none';
            
            const map = new google.maps.Map(document.getElementById('map'), {
              zoom: ${zoom},
              center: { lat: ${center.split(',')[0]}, lng: ${center.split(',')[1]} },
              mapTypeControl: true,
              streetViewControl: false,
              fullscreenControl: false,
              styles: [
                {
                  featureType: "transit",
                  elementType: "all",
                  stylers: [{ visibility: "on" }]
                },
                {
                  featureType: "transit.station.bus",
                  elementType: "all",
                  stylers: [{ visibility: "on" }]
                },
                {
                  featureType: "transit.station.rail",
                  elementType: "all",
                  stylers: [{ visibility: "on" }]
                }
              ]
            });
            
            ${markers}
            ${routeCode}
            
            // Adjust map bounds if we have both points
            ${origin && destination ? `
            const bounds = new google.maps.LatLngBounds();
            bounds.extend({ lat: ${origin.latitude}, lng: ${origin.longitude} });
            bounds.extend({ lat: ${destination.latitude}, lng: ${destination.longitude} });
            map.fitBounds(bounds);
            ` : ''}
          }
        </script>
      </body>
      </html>
    `;
  };

  return (
    <View style={[styles.container, height ? { height } : { flex: 1 }]}>
      <WebView
        ref={webViewRef}
        source={{ html: generateMapHTML() }}
        style={styles.webview}
        startInLoadingState={true}
        renderLoading={() => (
          <View style={styles.loadingContainer}>
            <ActivityIndicator size="large" color="#FF8C00" />
            <Text style={styles.loadingText}>Loading Google Maps...</Text>
          </View>
        )}
        javaScriptEnabled={true}
        domStorageEnabled={true}
        allowsInlineMediaPlayback={true}
        showsHorizontalScrollIndicator={false}
        showsVerticalScrollIndicator={false}
      />
    </View>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    borderRadius: 12,
    overflow: 'hidden',
    backgroundColor: '#f0f0f0',
  },
  webview: {
    flex: 1,
  },
  loadingContainer: {
    position: 'absolute',
    top: 0,
    left: 0,
    right: 0,
    bottom: 0,
    justifyContent: 'center',
    alignItems: 'center',
    backgroundColor: 'white',
  },
  loadingText: {
    marginTop: 10,
    fontSize: 16,
    color: '#666',
  },
});