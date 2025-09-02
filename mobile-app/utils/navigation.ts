import { router } from 'expo-router';

export const navigateToMap = async () => {
  console.log('🗺️ Navigation utility called');
  
  const routes = [
    '/(tabs)/map',
    '/map', 
    'map',
    '(tabs)/map',
  ];
  
  for (const route of routes) {
    try {
      console.log(`🗺️ Attempting navigation to: ${route}`);
      router.push(route as any);
      console.log(`✅ Navigation successful: ${route}`);
      return true;
    } catch (error) {
      console.log(`❌ Route ${route} failed:`, error);
    }
  }
  
  console.error('❌ All navigation routes failed');
  return false;
};

export const navigateToTab = (tabName: string) => {
  try {
    console.log(`🎯 Navigating to tab: ${tabName}`);
    router.push(`/(tabs)/${tabName}` as any);
    return true;
  } catch (error) {
    console.error(`❌ Tab navigation to ${tabName} failed:`, error);
    return false;
  }
};