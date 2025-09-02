import * as LocalAuthentication from 'expo-local-authentication';
import { Alert } from 'react-native';
import { storageService } from './storage';

class BiometricService {
  private isAvailable: boolean | null = null;
  private supportedTypes: LocalAuthentication.AuthenticationType[] = [];

  async initialize(): Promise<boolean> {
    try {
      // Check if device supports biometric authentication
      const hasHardware = await LocalAuthentication.hasHardwareAsync();
      if (!hasHardware) {
        console.log('Biometric hardware not available');
        this.isAvailable = false;
        return false;
      }

      // Check if biometric records are enrolled
      const isEnrolled = await LocalAuthentication.isEnrolledAsync();
      if (!isEnrolled) {
        console.log('No biometric records enrolled');
        this.isAvailable = false;
        return false;
      }

      // Get supported authentication types
      this.supportedTypes = await LocalAuthentication.supportedAuthenticationTypesAsync();
      this.isAvailable = true;
      
      console.log('Biometric authentication available:', this.supportedTypes);
      return true;
    } catch (error) {
      console.error('Failed to initialize biometric service:', error);
      this.isAvailable = false;
      return false;
    }
  }

  async isBiometricAvailable(): Promise<boolean> {
    if (this.isAvailable === null) {
      await this.initialize();
    }
    return this.isAvailable || false;
  }

  async getSupportedTypes(): Promise<LocalAuthentication.AuthenticationType[]> {
    if (this.supportedTypes.length === 0) {
      await this.initialize();
    }
    return this.supportedTypes;
  }

  getBiometricTypeLabel(type: LocalAuthentication.AuthenticationType): string {
    switch (type) {
      case LocalAuthentication.AuthenticationType.FINGERPRINT:
        return 'Fingerprint';
      case LocalAuthentication.AuthenticationType.FACIAL_RECOGNITION:
        return 'Face ID';
      case LocalAuthentication.AuthenticationType.IRIS:
        return 'Iris';
      default:
        return 'Biometric';
    }
  }

  async authenticate(
    promptMessage?: string, 
    cancelLabel?: string,
    disableDeviceFallback?: boolean
  ): Promise<{ success: boolean; error?: string }> {
    try {
      const available = await this.isBiometricAvailable();
      if (!available) {
        return { success: false, error: 'Biometric authentication not available' };
      }

      const authTypes = await this.getSupportedTypes();
      const primaryType = authTypes[0];
      const typeLabel = this.getBiometricTypeLabel(primaryType);

      const result = await LocalAuthentication.authenticateAsync({
        promptMessage: promptMessage || `Use ${typeLabel} to authenticate`,
        cancelLabel: cancelLabel || 'Cancel',
        disableDeviceFallback: disableDeviceFallback || false,
        fallbackLabel: 'Use Passcode',
      });

      if (result.success) {
        return { success: true };
      } else {
        return { 
          success: false, 
          error: result.error === 'user_cancel' ? 'Authentication cancelled' : 'Authentication failed'
        };
      }
    } catch (error: any) {
      console.error('Biometric authentication error:', error);
      return { success: false, error: error.message || 'Authentication error' };
    }
  }

  async authenticateForLogin(): Promise<{ success: boolean; error?: string }> {
    const types = await this.getSupportedTypes();
    const primaryType = types[0];
    const typeLabel = this.getBiometricTypeLabel(primaryType);

    return this.authenticate(
      `Sign in with ${typeLabel}`,
      'Use Password Instead',
      true
    );
  }

  async authenticateForSensitiveAction(action: string): Promise<{ success: boolean; error?: string }> {
    const types = await this.getSupportedTypes();
    const primaryType = types[0];
    const typeLabel = this.getBiometricTypeLabel(primaryType);

    return this.authenticate(
      `Use ${typeLabel} to ${action}`,
      'Cancel',
      true
    );
  }

  // Check if biometric login is enabled
  async isBiometricLoginEnabled(): Promise<boolean> {
    try {
      const enabled = await storageService.getBiometricEnabled();
      return enabled && await this.isBiometricAvailable();
    } catch {
      return false;
    }
  }

  // Enable/disable biometric login
  async setBiometricLoginEnabled(enabled: boolean): Promise<{ success: boolean; error?: string }> {
    try {
      if (enabled) {
        // Verify biometric authentication before enabling
        const authResult = await this.authenticate(
          'Authenticate to enable biometric login',
          'Cancel',
          true
        );

        if (!authResult.success) {
          return authResult;
        }
      }

      await storageService.setBiometricEnabled(enabled);
      return { success: true };
    } catch (error: any) {
      return { success: false, error: error.message || 'Failed to update setting' };
    }
  }

  // Quick login with biometric
  async quickLogin(): Promise<{ success: boolean; error?: string }> {
    try {
      const enabled = await this.isBiometricLoginEnabled();
      if (!enabled) {
        return { success: false, error: 'Biometric login not enabled' };
      }

      // Check if we have stored credentials
      const hasCredentials = await storageService.hasBiometricCredentials();
      if (!hasCredentials) {
        return { success: false, error: 'No stored credentials for biometric login' };
      }

      // Authenticate with biometric
      const authResult = await this.authenticateForLogin();
      if (!authResult.success) {
        return authResult;
      }

      // Get stored credentials
      const credentials = await storageService.getBiometricCredentials();
      if (!credentials) {
        return { success: false, error: 'Failed to retrieve credentials' };
      }

      return { success: true };
    } catch (error: any) {
      return { success: false, error: error.message || 'Quick login failed' };
    }
  }

  // Store credentials for biometric login
  async storeBiometricCredentials(email: string, encryptedPassword: string): Promise<boolean> {
    try {
      // First authenticate to confirm biometric works
      const authResult = await this.authenticate(
        'Authenticate to save login credentials',
        'Cancel',
        true
      );

      if (!authResult.success) {
        return false;
      }

      await storageService.storeBiometricCredentials(email, encryptedPassword);
      return true;
    } catch (error) {
      console.error('Failed to store biometric credentials:', error);
      return false;
    }
  }

  // Clear biometric credentials
  async clearBiometricCredentials(): Promise<void> {
    try {
      await storageService.clearBiometricCredentials();
      await storageService.setBiometricEnabled(false);
    } catch (error) {
      console.error('Failed to clear biometric credentials:', error);
    }
  }

  // Show biometric setup dialog
  async showBiometricSetupDialog(): Promise<boolean> {
    return new Promise((resolve) => {
      Alert.alert(
        'Enable Biometric Login',
        'Would you like to use biometric authentication for quick and secure login?',
        [
          {
            text: 'Not Now',
            style: 'cancel',
            onPress: () => resolve(false),
          },
          {
            text: 'Enable',
            onPress: async () => {
              const result = await this.setBiometricLoginEnabled(true);
              resolve(result.success);
            },
          },
        ]
      );
    });
  }

  // Check if device supports biometric and show appropriate prompt
  async checkAndPromptBiometricSetup(): Promise<void> {
    try {
      const available = await this.isBiometricAvailable();
      if (!available) return;

      const enabled = await this.isBiometricLoginEnabled();
      if (enabled) return;

      const hasPrompted = await storageService.hasBiometricPromptShown();
      if (hasPrompted) return;

      // Show setup dialog
      const setupResult = await this.showBiometricSetupDialog();
      
      // Mark as prompted regardless of choice
      await storageService.setBiometricPromptShown(true);
    } catch (error) {
      console.error('Error in biometric setup check:', error);
    }
  }
}

export const biometricService = new BiometricService();