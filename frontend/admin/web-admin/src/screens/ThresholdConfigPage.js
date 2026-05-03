import React, { useState, useEffect } from "react";
import { View, Text, ScrollView, TouchableOpacity, TextInput, ActivityIndicator, Alert } from "react-native";
import { Feather } from "@expo/vector-icons";
import { LinearGradient } from "expo-linear-gradient";
import { styles } from "../styles/globalStyles";
import AdminSidebar from "../components/AdminSidebar";
import RealTimeClock from "../components/RealTimeClock";
import { API_BASE_URL } from "../config/api";
import { getSystemStatus, getSystemStatusColor } from "../utils/dateUtils";
import { authFetch, areValuesEqual } from "../utils/helpers";
import useDataSync from "../utils/useDataSync";
import TopRightStatusIndicator from "../components/TopRightStatusIndicator";

const ThresholdConfigPage = ({ onNavigate, onLogout, userRole = "superadmin" }) => {
    const [advisoryLevel, setAdvisoryLevel] = useState("15");
    const [warningLevel, setWarningLevel] = useState("30");
    const [criticalLevel, setCriticalLevel] = useState("50");
    const [measurementUnit, setMeasurementUnit] = useState("cm");
    const [isLoading, setIsLoading] = useState(true);
    const [isSaving, setIsSaving] = useState(false);
    const [successMessage, setSuccessMessage] = useState("");
    const [errorMessage, setErrorMessage] = useState("");
    const [infoMessage, setInfoMessage] = useState("");
    const [initialThresholds, setInitialThresholds] = useState({ advisory: "15", warning: "30", critical: "50", unit: "cm" });
    const [onlineSensors, setOnlineSensors] = useState(0);

    useEffect(() => {
        const fetchSystemStatus = async () => {
            try {
                const res = await authFetch(`${API_BASE_URL}/api/iot/sensors/status-all`);
                if (res.ok) {
                    const data = await res.json();
                    const online = data.filter(s => !s.is_offline).length;
                    setOnlineSensors(online);
                }
            } catch (e) {
                console.error("Status fetch error:", e);
            }
        };

        fetchThresholds();
        fetchSystemStatus();
        const interval = setInterval(fetchSystemStatus, 30000);
        return () => clearInterval(interval);
    }, []);

    // ── Helper: Convert from CM to Display Unit ──
    const toDisplay = (val, unit) => {
        if (!val) return "0";
        if (unit === "m") return (parseFloat(val) / 100).toString();
        return val.toString();
    };

    // ── Helper: Convert from Display Unit to CM ──
    const fromDisplay = (val, unit) => {
        if (!val) return 0;
        if (unit === "m") return Math.round(parseFloat(val) * 100);
        return parseInt(val);
    };

    // ── Real-time Data Synchronization ──
    useDataSync({
        onThresholdUpdate: (data) => {
            console.log("[ThresholdConfig] Thresholds updated by another user, syncing...");
            const unit = data.measurement_unit || "cm";
            setMeasurementUnit(unit);
            setAdvisoryLevel(toDisplay(data.advisory_level, unit));
            setWarningLevel(toDisplay(data.warning_level, unit));
            setCriticalLevel(toDisplay(data.critical_level, unit));
            setInitialThresholds({
                advisory: toDisplay(data.advisory_level, unit),
                warning: toDisplay(data.warning_level, unit),
                critical: toDisplay(data.critical_level, unit),
                unit: unit
            });
        }
    });

    const fetchThresholds = async () => {
        setIsLoading(true);
        try {
            const res = await authFetch(`${API_BASE_URL}/api/config/thresholds`);
            if (res.ok) {
                const data = await res.json();
                const unit = data.measurement_unit || "cm";
                setMeasurementUnit(unit);
                setAdvisoryLevel(toDisplay(data.advisory_level, unit));
                setWarningLevel(toDisplay(data.warning_level, unit));
                setCriticalLevel(toDisplay(data.critical_level, unit));
                setInitialThresholds({
                    advisory: toDisplay(data.advisory_level, unit),
                    warning: toDisplay(data.warning_level, unit),
                    critical: toDisplay(data.critical_level, unit),
                    unit: unit
                });
            } else {
                console.error("Failed to fetch thresholds");
            }
        } catch (err) {
            console.error("Error fetching thresholds:", err);
        } finally {
            setIsLoading(false);
        }
    };

    const handleUnitChange = (newUnit) => {
        if (newUnit === measurementUnit) return;
        
        // Convert current values to the new unit for display
        if (newUnit === "m") {
            setAdvisoryLevel((parseFloat(advisoryLevel) / 100).toString());
            setWarningLevel((parseFloat(warningLevel) / 100).toString());
            setCriticalLevel((parseFloat(criticalLevel) / 100).toString());
        } else {
            setAdvisoryLevel(Math.round(parseFloat(advisoryLevel) * 100).toString());
            setWarningLevel(Math.round(parseFloat(warningLevel) * 100).toString());
            setCriticalLevel(Math.round(parseFloat(criticalLevel) * 100).toString());
        }
        setMeasurementUnit(newUnit);
    };

    const handleSave = async () => {
        setSuccessMessage("");
        setErrorMessage("");
        setInfoMessage("");

        const currentThresholds = {
            advisory: advisoryLevel,
            warning: warningLevel,
            critical: criticalLevel,
            unit: measurementUnit
        };

        if (initialThresholds && areValuesEqual(currentThresholds, initialThresholds)) {
            setInfoMessage("No changes detected. The configurations remain the same.");
            setTimeout(() => setInfoMessage(""), 4000);
            return;
        }

        setIsSaving(true);
        try {
            const res = await authFetch(`${API_BASE_URL}/api/config/thresholds`, {
                method: "PUT",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({
                    advisory_level: fromDisplay(advisoryLevel, measurementUnit),
                    warning_level: fromDisplay(warningLevel, measurementUnit),
                    critical_level: fromDisplay(criticalLevel, measurementUnit),
                    measurement_unit: measurementUnit
                })
            });

            if (res.ok) {
                setErrorMessage("");
                setSuccessMessage("Configuration saved successfully!");
                setInitialThresholds({ ...currentThresholds });
                setTimeout(() => setSuccessMessage(""), 4000);
            } else {
                setSuccessMessage("");
                setErrorMessage("Error: Failed to save threshold configuration.");
            }
        } catch (err) {
            console.error("Save error:", err);
            setSuccessMessage("");
            setErrorMessage("Error: Backend is offline or network issue occurred.");
        } finally {
            setIsSaving(false);
        }
    };

    return (
        <View style={styles.dashboardMain}>

                <View style={styles.dashboardTopBar}>
                    <View>
                        <Text style={styles.dashboardTopTitle}>Threshold Configuration</Text>
                        <Text style={styles.dashboardTopSubtitle}>
                            Set and dynamically modify risk level parameters for flood alerts
                        </Text>
                    </View>
                    <View style={styles.dashboardTopRight}>
                        <TopRightStatusIndicator />
                        <RealTimeClock style={styles.dashboardTopDate} />
                    </View>
                </View>

                {isLoading ? (
                    <View style={{ flex: 1, justifyContent: "center", alignItems: "center" }}>
                        <ActivityIndicator size="large" color="#B0DB9C" />
                        <Text style={{ marginTop: 16, fontFamily: "Poppins_500Medium" }}>Loading configurations...</Text>
                    </View>
                ) : (
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
                                        <View style={{ flexDirection: 'row', alignItems: 'center' }}>
                                            <Feather name="settings" size={24} color="#3b82f6" />
                                            <Text style={styles.configCardTitle}>Water Level Thresholds</Text>
                                        </View>
                                        
                                        {/* Unit Selector */}
                                        <View style={{ flexDirection: 'row', backgroundColor: '#f1f5f9', borderRadius: 8, padding: 4 }}>
                                            <TouchableOpacity 
                                                onPress={() => handleUnitChange("cm")}
                                                style={{ 
                                                    paddingHorizontal: 12, 
                                                    paddingVertical: 6, 
                                                    backgroundColor: measurementUnit === "cm" ? "#fff" : "transparent",
                                                    borderRadius: 6,
                                                    shadowColor: measurementUnit === "cm" ? "#000" : "transparent",
                                                    shadowOffset: { width: 0, height: 1 },
                                                    shadowOpacity: 0.1,
                                                    shadowRadius: 2,
                                                    elevation: measurementUnit === "cm" ? 2 : 0
                                                }}
                                            >
                                                <Text style={{ fontSize: 12, fontFamily: "Poppins_600SemiBold", color: measurementUnit === "cm" ? "#3b82f6" : "#64748b" }}>CM</Text>
                                            </TouchableOpacity>
                                            <TouchableOpacity 
                                                onPress={() => handleUnitChange("m")}
                                                style={{ 
                                                    paddingHorizontal: 12, 
                                                    paddingVertical: 6, 
                                                    backgroundColor: measurementUnit === "m" ? "#fff" : "transparent",
                                                    borderRadius: 6,
                                                    shadowColor: measurementUnit === "m" ? "#000" : "transparent",
                                                    shadowOffset: { width: 0, height: 1 },
                                                    shadowOpacity: 0.1,
                                                    shadowRadius: 2,
                                                    elevation: measurementUnit === "m" ? 2 : 0
                                                }}
                                            >
                                                <Text style={{ fontSize: 12, fontFamily: "Poppins_600SemiBold", color: measurementUnit === "m" ? "#3b82f6" : "#64748b" }}>Meters</Text>
                                            </TouchableOpacity>
                                        </View>
                                    </View>

                                    {/* Advisory Input */}
                                    <View style={styles.thresholdRow}>
                                        <View style={styles.thresholdLabelRow}>
                                            <Text style={styles.thresholdLabel}>Advisory Level</Text>
                                            <View style={[styles.thresholdBadge, { backgroundColor: "#eff6ff", borderColor: "#bfdbfe" }]}>
                                                <Text style={[styles.thresholdBadgeText, { color: "#2563eb" }]}>{advisoryLevel}{measurementUnit}</Text>
                                            </View>
                                        </View>
                                        <TextInput
                                            style={styles.thresholdInputDisplay}
                                            value={advisoryLevel}
                                            onChangeText={setAdvisoryLevel}
                                            keyboardType="numeric"
                                        />
                                        <Text style={styles.thresholdDescription}>
                                            Water level (in {measurementUnit}) that triggers advisory alerts to residents
                                        </Text>
                                    </View>

                                    {/* Warning Input */}
                                    <View style={styles.thresholdRow}>
                                        <View style={styles.thresholdLabelRow}>
                                            <Text style={styles.thresholdLabel}>Warning Level</Text>
                                            <View style={[styles.thresholdBadge, { backgroundColor: "#fff7ed", borderColor: "#fed7aa" }]}>
                                                <Text style={[styles.thresholdBadgeText, { color: "#ea580c" }]}>{warningLevel}{measurementUnit}</Text>
                                            </View>
                                        </View>
                                        <TextInput
                                            style={styles.thresholdInputDisplay}
                                            value={warningLevel}
                                            onChangeText={setWarningLevel}
                                            keyboardType="numeric"
                                        />
                                        <Text style={styles.thresholdDescription}>
                                            Water level (in {measurementUnit}) that triggers warning alerts and preparation notices
                                        </Text>
                                    </View>

                                    {/* Critical Input */}
                                    <View style={styles.thresholdRow}>
                                        <View style={styles.thresholdLabelRow}>
                                            <Text style={styles.thresholdLabel}>Critical Level</Text>
                                            <View style={[styles.thresholdBadge, { backgroundColor: "#fef2f2", borderColor: "#fecaca" }]}>
                                                <Text style={[styles.thresholdBadgeText, { color: "#dc2626" }]}>{criticalLevel}{measurementUnit}</Text>
                                            </View>
                                        </View>
                                        <TextInput
                                            style={styles.thresholdInputDisplay}
                                            value={criticalLevel}
                                            onChangeText={setCriticalLevel}
                                            keyboardType="numeric"
                                        />
                                        <Text style={styles.thresholdDescription}>
                                            Water level (in {measurementUnit}) that triggers critical alerts and evacuation orders
                                        </Text>
                                    </View>

                                    <TouchableOpacity style={styles.saveConfigButton} onPress={handleSave} disabled={isSaving}>
                                        {isSaving ? (
                                            <ActivityIndicator size="small" color="#1a3d0a" />
                                        ) : (
                                            <Feather name="save" size={18} color="#1a3d0a" />
                                        )}
                                        <Text style={styles.saveConfigButtonText}>
                                            {isSaving ? "Saving..." : "Save Configuration"}
                                        </Text>
                                    </TouchableOpacity>
                                    {successMessage ? (
                                        <View style={{ marginTop: 16, padding: 12, backgroundColor: "#dcfce7", borderRadius: 8, flexDirection: "row", alignItems: "center" }}>
                                            <Feather name="check-circle" size={18} color="#15803d" style={{ marginRight: 8 }} />
                                            <Text style={{ color: "#166534", fontFamily: "Poppins_500Medium", fontSize: 13 }}>{successMessage}</Text>
                                        </View>
                                    ) : null}
                                    {errorMessage ? (
                                        <View style={{ marginTop: 16, padding: 12, backgroundColor: "#fee2e2", borderRadius: 8, flexDirection: "row", alignItems: "center" }}>
                                            <Feather name="alert-circle" size={18} color="#b91c1c" style={{ marginRight: 8 }} />
                                            <Text style={{ color: "#991b1b", fontFamily: "Poppins_500Medium", fontSize: 13 }}>{errorMessage}</Text>
                                        </View>
                                    ) : null}
                                    {infoMessage ? (
                                        <View style={{ marginTop: 16, padding: 12, backgroundColor: "#e0f2fe", borderRadius: 8, flexDirection: "row", alignItems: "center" }}>
                                            <Feather name="info" size={18} color="#0284c7" style={{ marginRight: 8 }} />
                                            <Text style={{ color: "#075985", fontFamily: "Poppins_500Medium", fontSize: 13 }}>{infoMessage}</Text>
                                        </View>
                                    ) : null}
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
                                            colors={['#dc2626', '#f97316', '#3b82f6']}
                                            style={styles.visualGradient}
                                            start={{ x: 0, y: 0 }}
                                            end={{ x: 0, y: 1 }}
                                        />
                                        <View style={styles.visualLabelOverlay}>
                                            <View style={styles.visualLabelItem}>
                                                <Text style={styles.visualLabelText}>CRITICAL ≥ {criticalLevel}{measurementUnit}</Text>
                                            </View>
                                            <View style={styles.visualLabelItem}>
                                                <Text style={styles.visualLabelText}>WARNING  {warningLevel}{measurementUnit} - {criticalLevel}{measurementUnit}</Text>
                                            </View>
                                            <View style={styles.visualLabelItem}>
                                                <Text style={styles.visualLabelText}>ADVISORY  {advisoryLevel}{measurementUnit} - {warningLevel}{measurementUnit}</Text>
                                            </View>
                                        </View>
                                    </View>

                                    <View style={styles.warningNote}>
                                        <Feather name="alert-triangle" size={20} color="#b45309" style={{ marginTop: 2 }} />
                                        <View style={{ flex: 1 }}>
                                            <Text style={styles.warningNoteTitle}>Important Note</Text>
                                            <Text style={styles.warningNoteText}>
                                                Changes to threshold levels will immediately update IoT calibrations and affect all automated alert systems.
                                                Make sure to test thoroughly before applying to production.
                                            </Text>
                                        </View>
                                    </View>
                                </View>
                            </View>
                        </View>
                    </ScrollView>
                )}
            </View>
        );
    };

export default ThresholdConfigPage;
