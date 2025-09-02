import { Platform } from 'react-native';
import Constants from 'expo-constants';

// Check if we're running in Expo Go
const isExpoGo = Constants.appOwnership === 'expo';

// Dynamic imports to avoid loading expo-notifications in Expo Go
let Notifications: any = null;
let Device: any = null;

// Only import expo-notifications if not in Expo Go
if (!isExpoGo) {
  try {
    Notifications = require('expo-notifications');
    Device = require('expo-device');
  } catch (error) {
    console.warn('Failed to import expo-notifications:', error);
  }
}

export { Notifications, Device, isExpoGo };