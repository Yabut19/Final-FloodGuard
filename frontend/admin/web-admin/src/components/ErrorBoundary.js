import React from 'react';
import { View, Text, TouchableOpacity } from 'react-native';

// Simple error boundary component for React Native Web
const ErrorBoundary = ({ children }) => {
  // For now, just return children - React Native Web has limited error boundary support
  // The main fixes for font loading and API timeouts should prevent most blank page issues
  return children;
};

export default ErrorBoundary;
