// Sri Lankan Design Theme - Colors, Typography, and Cultural Elements

export const SriLankanColors = {
  // Primary Sri Lankan flag colors
  primary: {
    saffron: '#FF6B35',      // Saffron/Orange from flag
    darkSaffron: '#E55A2B',  // Darker saffron
    lightSaffron: '#FF8A65',  // Lighter saffron
  },
  
  // Secondary colors from Sri Lankan flag
  secondary: {
    green: '#00A86B',        // Green from flag
    darkGreen: '#008A57',    // Darker green
    lightGreen: '#4CAF50',   // Lighter green
    maroon: '#8B0000',       // Dark red/maroon from flag
    gold: '#FFD700',         // Gold accent
  },

  // Traditional Sri Lankan colors
  traditional: {
    coconutBrown: '#8B4513',     // Traditional coconut husk
    cinnamon: '#D2691E',         // Ceylon cinnamon
    teaGreen: '#87A96B',         // Ceylon tea plantation
    sapphireBlue: '#0F52BA',     // Ceylon sapphire
    ivory: '#FFFFF0',            // Traditional ivory
    spiceRed: '#CC5500',         // Traditional spice red
  },

  // Modern interpretation
  modern: {
    warmWhite: '#FEFEFE',
    softGray: '#F5F5F5',
    mediumGray: '#9E9E9E',
    darkGray: '#424242',
    charcoal: '#212121',
  },

  // Status colors with Sri Lankan touch
  status: {
    success: '#4CAF50',      // Green success
    warning: '#FF9800',      // Amber warning  
    error: '#F44336',        // Red error
    info: '#2196F3',         // Blue info
  },

  // Transport mode colors
  transport: {
    bus: '#FF6B35',          // Primary saffron
    train: '#00A86B',        // Secondary green
    tuk: '#FFD700',          // Gold
    walk: '#87A96B',         // Tea green
    any: '#0F52BA',          // Sapphire blue
  }
};

export const SriLankanGradients = {
  sunset: ['#FF6B35', '#FFD700', '#FF8A65'],    // Saffron to gold sunset
  nature: ['#00A86B', '#87A96B', '#4CAF50'],    // Green nature gradient
  heritage: ['#8B0000', '#D2691E', '#CC5500'],  // Heritage red to cinnamon
  ocean: ['#0F52BA', '#2196F3', '#87CEEB'],     // Sri Lankan ocean blues
  primary: ['#FF6B35', '#E55A2B'],              // Primary gradient
  welcome: ['#1e40af', '#3b82f6', '#60a5fa'],  // Welcome screen (keep existing)
};

export const SriLankanTypography = {
  fontSizes: {
    xs: 12,
    sm: 14,
    base: 16,
    lg: 18,
    xl: 20,
    '2xl': 24,
    '3xl': 30,
    '4xl': 36,
  },
  
  fontWeights: {
    normal: '400',
    medium: '500',
    semibold: '600',
    bold: '700',
  },

  // Traditional Sri Lankan script support
  scripts: {
    sinhala: {
      fontFamily: 'NotoSansSinhala',
      lineHeight: 1.6,
    },
    tamil: {
      fontFamily: 'NotoSansTamil', 
      lineHeight: 1.6,
    },
    english: {
      fontFamily: 'System',
      lineHeight: 1.5,
    },
  },
};

export const SriLankanSpacing = {
  xs: 4,
  sm: 8,
  base: 16,
  lg: 24,
  xl: 32,
  '2xl': 48,
  '3xl': 64,
};

export const SriLankanBorderRadius = {
  sm: 8,
  base: 12,
  lg: 16,
  xl: 24,
  '2xl': 32,
  full: 9999,
};

export const SriLankanShadows = {
  sm: {
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 1 },
    shadowOpacity: 0.1,
    shadowRadius: 2,
    elevation: 2,
  },
  base: {
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 2 },
    shadowOpacity: 0.15,
    shadowRadius: 4,
    elevation: 4,
  },
  lg: {
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 4 },
    shadowOpacity: 0.2,
    shadowRadius: 8,
    elevation: 8,
  },
};

// Cultural design patterns
export const SriLankanPatterns = {
  // Traditional motifs (can be used as background patterns)
  lotus: '🪷',
  elephant: '🐘', 
  peacock: '🦚',
  temple: '🛕',
  tea: '🍃',
  coconut: '🥥',
  cinnamon: '🌿',
  
  // Transport icons with Sri Lankan touch
  transportIcons: {
    bus: '🚌',
    train: '🚂', 
    tuk: '🛺',
    walk: '🚶',
    boat: '🚤', // For coastal areas
  },
};

// Dark theme colors
export const SriLankanDarkColors = {
  background: '#121212',
  surface: '#1E1E1E',
  surfaceVariant: '#2D2D2D',
  
  primary: SriLankanColors.primary.saffron,
  secondary: SriLankanColors.secondary.green,
  
  text: {
    primary: '#FFFFFF',
    secondary: '#B0B0B0',
    disabled: '#666666',
  },
  
  border: '#333333',
  divider: '#2D2D2D',
};

// Component-specific styling
export const SriLankanComponents = {
  button: {
    primary: {
      backgroundColor: SriLankanColors.primary.saffron,
      borderRadius: SriLankanBorderRadius.lg,
      paddingVertical: 12,
      paddingHorizontal: 24,
    },
    secondary: {
      backgroundColor: SriLankanColors.secondary.green,
      borderRadius: SriLankanBorderRadius.lg,
      paddingVertical: 12,
      paddingHorizontal: 24,
    },
  },
  
  card: {
    backgroundColor: SriLankanColors.modern.warmWhite,
    borderRadius: SriLankanBorderRadius.xl,
    padding: SriLankanSpacing.lg,
    ...SriLankanShadows.base,
  },
  
  input: {
    backgroundColor: SriLankanColors.modern.softGray,
    borderRadius: SriLankanBorderRadius.lg,
    borderWidth: 1,
    borderColor: SriLankanColors.modern.mediumGray,
    paddingVertical: 12,
    paddingHorizontal: 16,
  },
};