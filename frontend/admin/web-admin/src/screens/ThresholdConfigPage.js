import React, { useState } from "react";
import { View, Text, ScrollView, TouchableOpacity, TextInput, StyleSheet } from "react-native";
import { Feather } from "@expo/vector-icons";
import { LinearGradient } from "expo-linear-gradient";
import { styles } from "../styles/globalStyles";
import AdminSidebar from "../components/AdminSidebar";
import RealTimeClock from "../components/RealTimeClock";

const ThresholdConfigPage = ({ onNavigate, onLogout, userRole = "superadmin" }) => {
    const [advisoryLevel, setAdvisoryLevel] = useState("1");
    const [warningLevel, setWarningLevel] = useState("2.5");
    const [criticalLevel, setCriticalLevel] = useState("3.5");
    const [cooldown, setCooldown] = useState("15");
    const [autoEscalation, setAutoEscalation] = useState("30");

    return (
        <View style={styles.dashboardRoot}>
            <AdminSidebar variant={userRole} activePage="threshold-config" onNavigate={onNavigate} onLogout={onLogout} />

            <View style={styles.dashboardMain}>
                <View style={styles.dashboardTopBar}>
                    <View>
                        <Text style={styles.dashboardTopTitle}>Threshold Configuration</Text>
                        <Text style={styles.dashboardTopSubtitle}>
                            Set and modify risk level parameters for flood alerts
                        </Text>
                    </View>
                    <View style={styles.dashboardTopRight}>
                        <View style={styles.dashboardStatusPill}>
                            <View style={styles.dashboardStatusDot} />
                            <Text style={styles.dashboardStatusText}>System Online</Text>
                        </View>
                        <RealTimeClock style={styles.dashboardTopDate} />
                    </View>
                </View>

                <ScrollView
                    style={styles.dashboardScroll}
                    contentContainerStyle={styles.dashboardScrollContent}
                    showsVerticalScrollIndicator={false}
                >
                    <View style={styles.configGrid}>
                        {/* Left Column: Input Thresholds */}
                        <View style={styles.configLeftCol}>
                            <View style={styles.configCard}>
                                <View style={styles.configCardHeader}>
                                    <Feather name="settings" size={24} color="#3b82f6" />
                                    <Text style={styles.configCardTitle}>Water Level Thresholds</Text>
                                </View>

                                {/* Advisory Input */}
                                <View style={styles.thresholdRow}>
                                    <View style={styles.thresholdLabelRow}>
                                        <Text style={styles.thresholdLabel}>Advisory Level</Text>
                                        <View style={styles.thresholdBadge}>
                                            <Text style={styles.thresholdBadgeText}>1m</Text>
                                        </View>
                                    </View>
                                    <TextInput
                                        style={styles.thresholdInputDisplay}
                                        value={advisoryLevel}
                                        onChangeText={setAdvisoryLevel}
                                        keyboardType="numeric"
                                    />
                                    <Text style={styles.thresholdDescription}>
                                        Water level that triggers advisory alerts to residents
                                    </Text>
                                </View>

                                {/* Warning Input */}
                                <View style={styles.thresholdRow}>
                                    <View style={styles.thresholdLabelRow}>
                                        <Text style={styles.thresholdLabel}>Warning Level</Text>
                                        <View style={[styles.thresholdBadge, { backgroundColor: "#fffbeb" }]}>
                                            <Text style={[styles.thresholdBadgeText, { color: "#d97706" }]}>2.5m</Text>
                                        </View>
                                    </View>
                                    <TextInput
                                        style={styles.thresholdInputDisplay}
                                        value={warningLevel}
                                        onChangeText={setWarningLevel}
                                        keyboardType="numeric"
                                    />
                                    <Text style={styles.thresholdDescription}>
                                        Water level that triggers warning alerts and preparation notices
                                    </Text>
                                </View>

                                {/* Critical Input */}
                                <View style={styles.thresholdRow}>
                                    <View style={styles.thresholdLabelRow}>
                                        <Text style={styles.thresholdLabel}>Critical Level</Text>
                                        <View style={[styles.thresholdBadge, { backgroundColor: "#fef2f2" }]}>
                                            <Text style={[styles.thresholdBadgeText, { color: "#dc2626" }]}>3.5m</Text>
                                        </View>
                                    </View>
                                    <TextInput
                                        style={styles.thresholdInputDisplay}
                                        value={criticalLevel}
                                        onChangeText={setCriticalLevel}
                                        keyboardType="numeric"
                                    />
                                    <Text style={styles.thresholdDescription}>
                                        Water level that triggers critical alerts and evacuation orders
                                    </Text>
                                </View>

                                <TouchableOpacity style={styles.saveConfigButton}>
                                    <Feather name="save" size={18} color="#64748b" />
                                    <Text style={styles.saveConfigButtonText}>Save Configuration</Text>
                                </TouchableOpacity>
                            </View>

                            {/* Additional Settings */}
                            <View style={styles.configCard}>
                                <View style={styles.configCardHeader}>
                                    <Text style={styles.configCardTitle}>Additional Alert Settings</Text>
                                </View>
                                <View style={{ flexDirection: "row", gap: 24 }}>
                                    <View style={styles.settingInputGroup}>
                                        <Text style={styles.settingInputLabel}>Alert Cooldown Period (minutes)</Text>
                                        <TextInput
                                            style={styles.settingInput}
                                            value={cooldown}
                                            onChangeText={setCooldown}
                                            keyboardType="numeric"
                                        />
                                    </View>
                                    <View style={styles.settingInputGroup}>
                                        <Text style={styles.settingInputLabel}>Auto-Escalation Time (minutes)</Text>
                                        <TextInput
                                            style={styles.settingInput}
                                            value={autoEscalation}
                                            onChangeText={setAutoEscalation}
                                            keyboardType="numeric"
                                        />
                                    </View>
                                </View>
                            </View>
                        </View>

                        {/* Right Column: Visual Reference */}
                        <View style={styles.configRightCol}>
                            <View style={styles.configCard}>
                                <View style={styles.configCardHeader}>
                                    <Text style={styles.configCardTitle}>Visual Reference</Text>
                                </View>

                                <View style={styles.visualRefContainer}>
                                    <LinearGradient
                                        colors={['#84cc16', '#eab308', '#ef4444', '#7f1d1d']}
                                        style={styles.visualGradient}
                                        start={{ x: 0, y: 0 }}
                                        end={{ x: 0, y: 1 }}
                                    />
                                    <View style={styles.visualLabelOverlay}>
                                        <View style={styles.visualLabelItem}>
                                            <Text style={styles.visualLabelText}>WARNING  1m - 2.5m</Text>
                                        </View>
                                        <View style={styles.visualLabelItem}>
                                            <Text style={styles.visualLabelText}>ADVISORY ≤ 1m</Text>
                                        </View>
                                        <View style={styles.visualLabelItem}>
                                            <Text style={styles.visualLabelText}>CRITICAL ≥ 3.5m</Text>
                                        </View>
                                    </View>
                                </View>

                                <View style={styles.warningNote}>
                                    <Feather name="alert-triangle" size={20} color="#b45309" style={{ marginTop: 2 }} />
                                    <View style={{ flex: 1 }}>
                                        <Text style={styles.warningNoteTitle}>Important Note</Text>
                                        <Text style={styles.warningNoteText}>
                                            Changes to threshold levels will affect all automated alert systems.
                                            Make sure to test thoroughly before applying to production.
                                        </Text>
                                    </View>
                                </View>
                            </View>
                        </View>
                    </View>
                </ScrollView>
            </View>
        </View>
    );
};

export default ThresholdConfigPage;
