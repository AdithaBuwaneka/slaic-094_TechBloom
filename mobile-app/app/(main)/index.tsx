import React, { useEffect } from 'react';
import { Redirect } from 'expo-router';

export default function MainIndex() {
  return <Redirect href="/(main)/(tabs)/home" />;
}
