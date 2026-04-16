import React from "react";
import { View, Text, StyleSheet } from "react-native";

export default function App() {
  return (
    <View style={styles.container}>
      <Text style={styles.text}>Hello World - Landing Page Test</Text>
      <Text style={styles.subtext}>If you see this, React Native Web is working!</Text>
    </View>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: "#f6f8fb",
    justifyContent: "center",
    alignItems: "center",
    padding: 20,
  },
  text: {
    fontSize: 24,
    fontWeight: "bold",
    color: "#1a2433",
    marginBottom: 10,
  },
  subtext: {
    fontSize: 16,
    color: "#475569",
  },
});
