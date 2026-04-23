import React, { useMemo, useState } from "react";
import {
  SafeAreaView,
  View,
  Text,
  TextInput,
  TouchableOpacity,
  StyleSheet,
  ScrollView,
  Platform,
  Image,
} from "react-native";
import { LinearGradient } from "expo-linear-gradient";
import { Feather } from "@expo/vector-icons";

const DEMO_CREDENTIALS = {
  lgu: {
    email: "moderator@lgu.gov",
    password: "password123",
  },
  super: {
    email: "admin@system.com",
    password: "admin123",
  },
};
const FLOOD_HERO = require("./image/flood6.jpg");

export default function App() {
  const [view, setView] = useState("landing");
  const [role, setRole] = useState("lgu");
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [remember, setRemember] = useState(false);
  const [error, setError] = useState("");
  const [showRecovery, setShowRecovery] = useState(false);
  const [authenticatedRole, setAuthenticatedRole] = useState("");
  const [activeScreen, setActiveScreen] = useState("home");
  const [hasCompletedOnboarding, setHasCompletedOnboarding] = useState(false);
  const [navigatingTo, setNavigatingTo] = useState(null);

  const isReady = email.trim().length > 0 && password.trim().length > 0 && role;

  const onSubmit = () => {
    setError("");
    if (!isReady) {
      setError("Please complete all required fields.");
      return;
    }

    const selected = DEMO_CREDENTIALS[role];
    const otherRole = role === "lgu" ? "super" : "lgu";
    const other = DEMO_CREDENTIALS[otherRole];

    if (email === selected.email && password === selected.password) {
      setAuthenticatedRole(role);
      setView("admin-dashboard");
      return;
    }

    if (email === other.email && password === other.password) {
      setError("Unauthorized role access for this account.");
      return;
    }

    setError("Invalid credentials. Please try again.");
  };

  if (view === "landing") {
    return (
      <LandingPage
        onAdminLogin={() => setView("admin-login")}
        onMobileOpen={() => setView("mobile")}
      />
    );
  }

  if (view === "admin-dashboard" && authenticatedRole) {
    return (
      <AdminDashboard
        userRole={authenticatedRole === "super" ? "super-admin" : "lgu-moderator"}
        onLogout={() => {
          setAuthenticatedRole("");
          setEmail("");
          setPassword("");
          setRemember(false);
          setView("landing");
        }}
      />
    );
  }

  if (view === "mobile") {
    return (
      <MobileApp
        activeScreen={activeScreen}
        setActiveScreen={setActiveScreen}
        hasCompletedOnboarding={hasCompletedOnboarding}
        onCompleteOnboarding={() => setHasCompletedOnboarding(true)}
        navigatingTo={navigatingTo}
        onNavigate={(center) => setNavigatingTo(center)}
        onEndNavigation={() => setNavigatingTo(null)}
        onExit={() => setView("landing")}
      />
    );
  }

  return (
    <SafeAreaView style={styles.safe}>
      <LinearGradient colors={["#1b4fe0", "#4b2f9a"]} style={styles.background}>
        <View style={styles.header}>
          <View style={styles.shield}>
            <Feather name="shield" size={28} color="#ffffff" />
          </View>
          <Text style={styles.title}>Flood Monitor Admin</Text>
          <Text style={styles.subtitle}>Management Dashboard & Control Center</Text>
        </View>

        <View style={styles.card}>
          <Text style={styles.cardTitle}>Sign In</Text>

          <View style={styles.roleRow}>
            <RoleButton
              label="LGU Moderator"
              selected={role === "lgu"}
              onPress={() => setRole("lgu")}
            />
            <RoleButton
              label="Super Admin"
              selected={role === "super"}
              onPress={() => setRole("super")}
            />
          </View>

          <View style={styles.field}>
            <Text style={styles.label}>Email Address</Text>
            <TextInput
              value={email}
              onChangeText={setEmail}
              placeholder="admin@example.com"
              placeholderTextColor="#9aa5b1"
              autoCapitalize="none"
              keyboardType="email-address"
              style={styles.input}
            />
          </View>

          <View style={styles.field}>
            <Text style={styles.label}>Password</Text>
            <TextInput
              value={password}
              onChangeText={setPassword}
              placeholder="********"
              placeholderTextColor="#9aa5b1"
              secureTextEntry
              style={styles.input}
            />
          </View>

          <View style={styles.optionsRow}>
            <TouchableOpacity
              style={styles.rememberRow}
              onPress={() => setRemember((prev) => !prev)}
            >
              <View style={[styles.checkbox, remember && styles.checkboxChecked]}>
                {remember ? <Feather name="check" size={12} color="#ffffff" /> : null}
              </View>
              <Text style={styles.optionText}>Remember me</Text>
            </TouchableOpacity>
            <TouchableOpacity onPress={() => setShowRecovery((prev) => !prev)}>
              <Text style={styles.forgotText}>Forgot password?</Text>
            </TouchableOpacity>
          </View>

          {showRecovery ? (
            <Text style={styles.recoveryText}>
              Password recovery is restricted. Contact the system administrator.
            </Text>
          ) : null}

          {error ? <Text style={styles.errorText}>{error}</Text> : null}

          <TouchableOpacity
            style={[styles.signInButton, !isReady && styles.signInDisabled]}
            onPress={onSubmit}
            disabled={!isReady}
          >
            <Text style={styles.signInText}>Sign In</Text>
          </TouchableOpacity>

          <View style={styles.demoBlock}>
            <Text style={styles.demoTitle}>Demo Credentials:</Text>
            <Text style={styles.demoText}>
              LGU Moderator: moderator@lgu.gov / password123
            </Text>
            <Text style={styles.demoText}>Admin: admin@system.com / admin123</Text>
          </View>
        </View>

        <Text style={styles.footerText}>Flood Monitoring System v1.0 © 2024</Text>
      </LinearGradient>
    </SafeAreaView>
  );
}

function RoleButton({ label, selected, onPress }) {
  return (
    <TouchableOpacity
      onPress={onPress}
      style={[styles.roleButton, selected && styles.roleButtonActive]}
    >
      <Text style={[styles.roleText, selected && styles.roleTextActive]}>{label}</Text>
    </TouchableOpacity>
  );
}

function AdminDashboard({ userRole, onLogout }) {
  const [activeTab, setActiveTab] = useState("overview");
  const [sidebarOpen, setSidebarOpen] = useState(true);

  const menuItems = useMemo(
    () => [
      { id: "overview", icon: "layout", label: "Overview", roles: ["all"] },
      { id: "sensor-map", icon: "map", label: "Sensor Map", roles: ["all"] },
      { id: "alerts", icon: "bell", label: "Alert Management", roles: ["all"] },
      { id: "system-health", icon: "activity", label: "System Health", roles: ["all"] },
      { id: "users", icon: "users", label: "User Management", roles: ["super"] },
      { id: "reports", icon: "file-text", label: "Data & Reports", roles: ["all"] },
      { id: "threshold", icon: "settings", label: "Threshold Config", roles: ["super"] },
    ],
    []
  );

  const filteredMenu = menuItems.filter(
    (item) => item.roles.includes("all") || userRole === "super-admin"
  );

  return (
    <SafeAreaView style={styles.dashboardSafe}>
      <View style={styles.dashboardContainer}>
        <View style={[styles.sidebar, !sidebarOpen && styles.sidebarCollapsed]}>
          <View style={styles.sidebarHeader}>
            <Text style={styles.brandTitle}>Flood Monitor</Text>
            <Text style={styles.brandSubtitle}>Admin Dashboard</Text>
          </View>

          <ScrollView contentContainerStyle={styles.sidebarMenu}>
            {filteredMenu.map((item) => (
              <TouchableOpacity
                key={item.id}
                onPress={() => setActiveTab(item.id)}
                style={[
                  styles.menuButton,
                  activeTab === item.id && styles.menuButtonActive,
                ]}
              >
                <Feather
                  name={item.icon}
                  size={18}
                  color={activeTab === item.id ? "#ffffff" : "#c7d2fe"}
                />
                {sidebarOpen ? (
                  <Text
                    style={[
                      styles.menuLabel,
                      activeTab === item.id && styles.menuLabelActive,
                    ]}
                  >
                    {item.label}
                  </Text>
                ) : null}
              </TouchableOpacity>
            ))}
          </ScrollView>

          <View style={styles.sidebarFooter}>
            <View style={styles.userRow}>
              <View style={styles.userAvatar}>
                <Text style={styles.userAvatarText}>AD</Text>
              </View>
              {sidebarOpen ? (
                <View style={styles.userInfo}>
                  <Text style={styles.userName}>Admin User</Text>
                  <Text style={styles.userRole}>
                    {userRole === "super-admin" ? "Super Admin" : "LGU Moderator"}
                  </Text>
                </View>
              ) : null}
            </View>
            <TouchableOpacity style={styles.logoutButton} onPress={onLogout}>
              <Feather name="log-out" size={16} color="#ffffff" />
              {sidebarOpen ? <Text style={styles.logoutText}>Logout</Text> : null}
            </TouchableOpacity>
          </View>
        </View>

        <View style={styles.dashboardContent}>
          <View style={styles.topBar}>
            <TouchableOpacity
              onPress={() => setSidebarOpen((prev) => !prev)}
              style={styles.iconButton}
            >
              <Feather
                name={sidebarOpen ? "x" : "menu"}
                size={20}
                color="#64748b"
              />
            </TouchableOpacity>
            <View style={styles.topRight}>
              <View style={styles.statusPill}>
                <Text style={styles.statusText}>System Online</Text>
              </View>
              <Text style={styles.dateText}>
                {new Intl.DateTimeFormat("en-US", {
                  timeZone: "Asia/Manila",
                  weekday: "long",
                  year: "numeric",
                  month: "long",
                  day: "numeric",
                }).format(new Date())}
              </Text>
            </View>
          </View>

          <View style={styles.panel}>
            <Text style={styles.panelTitle}>{tabTitle(activeTab)}</Text>
            <Text style={styles.panelText}>
              Replace this section with the {tabTitle(activeTab)} content.
            </Text>
          </View>
        </View>
      </View>
    </SafeAreaView>
  );
}

function LandingPage({ onAdminLogin, onMobileOpen }) {
  return (
    <SafeAreaView style={styles.safe}>
      <LinearGradient colors={["#1b4fe0", "#4b2f9a"]} style={styles.background}>
        <View style={styles.heroCard}>
          <Image source={FLOOD_HERO} style={styles.heroImage} />
          <View style={styles.heroOverlay} />
          <View style={styles.heroCaption}>
            <Text style={styles.heroLabel}>Real Impact</Text>
            <Text style={styles.heroTitle}>Floods Affect Thousands Annually</Text>
          </View>
        </View>
        <View style={styles.landingHeader}>
          <View style={styles.shield}>
            <Feather name="shield" size={28} color="#ffffff" />
          </View>
          <Text style={styles.title}>Flood Monitor</Text>
          <Text style={styles.subtitle}>Real-time Flood Monitoring System</Text>
        </View>

        <View style={styles.landingCard}>
          <Text style={styles.landingTitle}>Admin Access Only</Text>
          <Text style={styles.landingText}>
            Secure access for LGU Moderators and Super Admins.
          </Text>
          <TouchableOpacity style={styles.primaryButton} onPress={onAdminLogin}>
            <Text style={styles.primaryButtonText}>Go to Admin Login</Text>
          </TouchableOpacity>
          <TouchableOpacity style={styles.secondaryButton} onPress={onMobileOpen}>
            <Text style={styles.secondaryButtonText}>Open Mobile Demo</Text>
          </TouchableOpacity>
        </View>

        <Text style={styles.footerText}>Flood Monitoring System v1.0 © 2024</Text>
      </LinearGradient>
    </SafeAreaView>
  );
}

function MobileApp({
  activeScreen,
  setActiveScreen,
  hasCompletedOnboarding,
  onCompleteOnboarding,
  navigatingTo,
  onNavigate,
  onEndNavigation,
  onExit,
}) {
  if (!hasCompletedOnboarding) {
    return <OnboardingScreen onComplete={onCompleteOnboarding} onExit={onExit} />;
  }

  if (navigatingTo) {
    return <NavigationPage center={navigatingTo} onBack={onEndNavigation} />;
  }

  return (
    <SafeAreaView style={styles.mobileSafe}>
      <View style={styles.mobileHeader}>
        <Text style={styles.mobileHeaderTitle}>Flood Monitor</Text>
        <TouchableOpacity onPress={onExit} style={styles.exitButton}>
          <Text style={styles.exitButtonText}>Exit</Text>
        </TouchableOpacity>
      </View>
      <ScrollView contentContainerStyle={styles.mobileContent}>
        {activeScreen === "home" && <HomeScreen />}
        {activeScreen === "alerts" && <AlertsScreen />}
        {activeScreen === "evacuation" && (
          <EvacuationScreen onNavigate={onNavigate} />
        )}
        {activeScreen === "report" && <ReportScreen />}
        {activeScreen === "settings" && <SettingsScreen />}
      </ScrollView>
      <MobileNavigation activeScreen={activeScreen} onChange={setActiveScreen} />
    </SafeAreaView>
  );
}

function OnboardingScreen({ onComplete, onExit }) {
  const [step, setStep] = useState(1);

  const onNext = () => {
    if (step < 4) {
      setStep((prev) => prev + 1);
      return;
    }
    onComplete();
  };

  return (
    <SafeAreaView style={styles.onboardingSafe}>
      <LinearGradient colors={["#2563eb", "#6d28d9"]} style={styles.onboardingHero}>
        <View style={styles.onboardingTop}>
          <TouchableOpacity onPress={onExit}>
            <Text style={styles.onboardingExit}>Back</Text>
          </TouchableOpacity>
          <Text style={styles.onboardingStep}>Step {step} of 4</Text>
        </View>
        <View style={styles.onboardingCard}>
          <Text style={styles.onboardingTitle}>Welcome to Flood Monitor</Text>
          <Text style={styles.onboardingText}>
            Get real-time alerts, safe routes, and community updates.
          </Text>
          <View style={styles.onboardingList}>
            <Text style={styles.onboardingBullet}>• Real-time flood alerts</Text>
            <Text style={styles.onboardingBullet}>• Evacuation routes</Text>
            <Text style={styles.onboardingBullet}>• Community reports</Text>
          </View>
          <TouchableOpacity style={styles.primaryButton} onPress={onNext}>
            <Text style={styles.primaryButtonText}>
              {step === 4 ? "Get Started" : "Continue"}
            </Text>
          </TouchableOpacity>
        </View>
      </LinearGradient>
    </SafeAreaView>
  );
}

function MobileNavigation({ activeScreen, onChange }) {
  const items = [
    { id: "home", label: "Home", icon: "home" },
    { id: "alerts", label: "Alerts", icon: "bell" },
    { id: "evacuation", label: "Evac", icon: "map-pin" },
    { id: "report", label: "Report", icon: "message-square" },
    { id: "settings", label: "Settings", icon: "settings" },
  ];

  return (
    <View style={styles.navBar}>
      {items.map((item) => {
        const isActive = activeScreen === item.id;
        return (
          <TouchableOpacity
            key={item.id}
            onPress={() => onChange(item.id)}
            style={styles.navItem}
          >
            <Feather name={item.icon} size={18} color={isActive ? "#2563eb" : "#94a3b8"} />
            <Text style={[styles.navLabel, isActive && styles.navLabelActive]}>
              {item.label}
            </Text>
          </TouchableOpacity>
        );
      })}
    </View>
  );
}

function HomeScreen() {
  return (
    <View style={styles.section}>
      <View style={styles.sectionHeader}>
        <Text style={styles.sectionTitle}>Current Status</Text>
        <View style={styles.statusPill}>
          <Text style={styles.statusText}>LOW RISK</Text>
        </View>
      </View>
      <Text style={styles.sectionText}>Your area is currently safe.</Text>
      <View style={styles.cardSmall}>
        <Text style={styles.cardLabel}>Water Level</Text>
        <Text style={styles.cardValue}>2.3m</Text>
      </View>
      <View style={styles.cardSmall}>
        <Text style={styles.cardLabel}>Active Sensors</Text>
        <Text style={styles.cardValue}>24</Text>
      </View>
    </View>
  );
}

function AlertsScreen() {
  const alerts = [
    { id: 1, title: "Medium Risk Alert", time: "15 minutes ago" },
    { id: 2, title: "Weather Update", time: "1 hour ago" },
  ];

  return (
    <View style={styles.section}>
      <Text style={styles.sectionTitle}>Alerts</Text>
      {alerts.map((alert) => (
        <View key={alert.id} style={styles.card}>
          <Text style={styles.cardTitle}>{alert.title}</Text>
          <Text style={styles.sectionText}>{alert.time}</Text>
        </View>
      ))}
    </View>
  );
}

function EvacuationScreen({ onNavigate }) {
  const centers = [
    { id: 1, name: "Barangay Hall San Jose", distance: "0.8 km" },
    { id: 2, name: "City Sports Complex", distance: "1.2 km" },
  ];

  return (
    <View style={styles.section}>
      <Text style={styles.sectionTitle}>Evacuation Centers</Text>
      {centers.map((center) => (
        <View key={center.id} style={styles.card}>
          <Text style={styles.cardTitle}>{center.name}</Text>
          <Text style={styles.sectionText}>{center.distance} away</Text>
          <TouchableOpacity
            style={styles.primaryButton}
            onPress={() => onNavigate(center)}
          >
            <Text style={styles.primaryButtonText}>Start Navigation</Text>
          </TouchableOpacity>
        </View>
      ))}
    </View>
  );
}

function ReportScreen() {
  const [type, setType] = useState("Flooding");
  const [description, setDescription] = useState("");

  return (
    <View style={styles.section}>
      <Text style={styles.sectionTitle}>Report</Text>
      <Text style={styles.label}>Report Type</Text>
      <View style={styles.roleRow}>
        <RoleButton label="Flooding" selected={type === "Flooding"} onPress={() => setType("Flooding")} />
        <RoleButton label="Water Level" selected={type === "Water Level"} onPress={() => setType("Water Level")} />
      </View>
      <Text style={styles.label}>Description</Text>
      <TextInput
        value={description}
        onChangeText={setDescription}
        placeholder="Describe what you are observing..."
        placeholderTextColor="#9aa5b1"
        style={styles.input}
        multiline
      />
      <TouchableOpacity style={styles.primaryButton}>
        <Text style={styles.primaryButtonText}>Submit Report</Text>
      </TouchableOpacity>
    </View>
  );
}

function SettingsScreen() {
  return (
    <View style={styles.section}>
      <Text style={styles.sectionTitle}>Settings</Text>
      <View style={styles.card}>
        <Text style={styles.cardTitle}>Alert Preferences</Text>
        <Text style={styles.sectionText}>Manage notification types and frequency.</Text>
      </View>
      <View style={styles.card}>
        <Text style={styles.cardTitle}>Privacy & Security</Text>
        <Text style={styles.sectionText}>Manage your data and permissions.</Text>
      </View>
    </View>
  );
}

function NavigationPage({ center, onBack }) {
  return (
    <SafeAreaView style={styles.mobileSafe}>
      <View style={styles.navHeader}>
        <TouchableOpacity onPress={onBack}>
          <Text style={styles.navBack}>Back</Text>
        </TouchableOpacity>
        <Text style={styles.navTitle}>{center?.name}</Text>
      </View>
      <View style={styles.navMap}>
        <Feather name="navigation" size={40} color="#2563eb" />
        <Text style={styles.sectionText}>Navigation in progress...</Text>
      </View>
    </SafeAreaView>
  );
}

const tabTitle = (tab) => {
  switch (tab) {
    case "overview":
      return "Overview";
    case "sensor-map":
      return "Sensor Map";
    case "alerts":
      return "Alert Management";
    case "system-health":
      return "System Health";
    case "users":
      return "User Management";
    case "reports":
      return "Data & Reports";
    case "threshold":
      return "Threshold Config";
    default:
      return "Overview";
  }
};

const styles = StyleSheet.create({
  safe: {
    flex: 1,
    backgroundColor: "#1b4fe0",
  },
  background: {
    flex: 1,
    alignItems: "center",
    justifyContent: "center",
    paddingHorizontal: 20,
    paddingBottom: 24,
    gap: 18,
  },
  header: {
    alignItems: "center",
    gap: 6,
  },
  shield: {
    width: 56,
    height: 56,
    borderRadius: 16,
    backgroundColor: "rgba(255,255,255,0.18)",
    alignItems: "center",
    justifyContent: "center",
  },
  title: {
    color: "#ffffff",
    fontSize: 24,
    fontWeight: "700",
  },
  subtitle: {
    color: "rgba(248,251,255,0.85)",
    fontSize: 13,
  },
  card: {
    width: "100%",
    maxWidth: 420,
    backgroundColor: "#ffffff",
    borderRadius: 20,
    padding: 24,
    gap: 16,
    shadowColor: "#0f172a",
    shadowOffset: { width: 0, height: 16 },
    shadowOpacity: 0.18,
    shadowRadius: 30,
    elevation: 10,
  },
  cardTitle: {
    fontSize: 20,
    fontWeight: "700",
    color: "#0f172a",
  },
  roleRow: {
    flexDirection: "row",
    gap: 10,
  },
  roleButton: {
    flex: 1,
    paddingVertical: 10,
    borderRadius: 12,
    backgroundColor: "#f8fafc",
    borderWidth: 1,
    borderColor: "#e2e8f0",
    alignItems: "center",
  },
  roleButtonActive: {
    backgroundColor: "#eef2ff",
    borderColor: "#2563eb",
  },
  roleText: {
    fontSize: 12,
    fontWeight: "600",
    color: "#334155",
  },
  roleTextActive: {
    color: "#1d4ed8",
  },
  field: {
    gap: 6,
  },
  label: {
    fontSize: 12,
    fontWeight: "600",
    color: "#1e293b",
  },
  input: {
    borderWidth: 1,
    borderColor: "#d7dee9",
    borderRadius: 10,
    paddingHorizontal: 12,
    paddingVertical: Platform.OS === "web" ? 10 : 8,
    fontSize: 14,
    color: "#0f172a",
  },
  optionsRow: {
    flexDirection: "row",
    justifyContent: "space-between",
    alignItems: "center",
  },
  rememberRow: {
    flexDirection: "row",
    alignItems: "center",
    gap: 6,
  },
  checkbox: {
    width: 16,
    height: 16,
    borderRadius: 4,
    borderWidth: 1,
    borderColor: "#cbd5f5",
    alignItems: "center",
    justifyContent: "center",
  },
  checkboxChecked: {
    backgroundColor: "#2563eb",
    borderColor: "#2563eb",
  },
  optionText: {
    fontSize: 12,
    color: "#475569",
  },
  forgotText: {
    fontSize: 12,
    color: "#1d4ed8",
    fontWeight: "600",
  },
  recoveryText: {
    fontSize: 12,
    color: "#475569",
    backgroundColor: "#f8fafc",
    borderRadius: 10,
    borderWidth: 1,
    borderColor: "#e2e8f0",
    padding: 10,
  },
  errorText: {
    color: "#b42318",
    fontSize: 12,
  },
  signInButton: {
    backgroundColor: "#2563eb",
    borderRadius: 12,
    paddingVertical: 12,
    alignItems: "center",
  },
  signInDisabled: {
    opacity: 0.5,
  },
  signInText: {
    color: "#ffffff",
    fontWeight: "700",
    fontSize: 14,
  },
  demoBlock: {
    gap: 4,
  },
  demoTitle: {
    fontSize: 11,
    color: "#64748b",
    fontWeight: "600",
  },
  demoText: {
    fontSize: 11,
    color: "#64748b",
  },
  footerText: {
    color: "rgba(248,251,255,0.8)",
    fontSize: 11,
  },
  landingHeader: {
    alignItems: "center",
    gap: 6,
    marginBottom: 12,
  },
  heroCard: {
    width: "100%",
    maxWidth: 520,
    borderRadius: 20,
    overflow: "hidden",
    marginBottom: 16,
  },
  heroImage: {
    width: "100%",
    height: 220,
    resizeMode: "cover",
  },
  heroOverlay: {
    ...StyleSheet.absoluteFillObject,
    backgroundColor: "rgba(0,0,0,0.35)",
  },
  heroCaption: {
    position: "absolute",
    bottom: 16,
    left: 16,
    right: 16,
    gap: 4,
  },
  heroLabel: {
    color: "rgba(255,255,255,0.85)",
    fontSize: 11,
    fontWeight: "600",
  },
  heroTitle: {
    color: "#ffffff",
    fontSize: 18,
    fontWeight: "700",
  },
  landingCard: {
    width: "100%",
    maxWidth: 420,
    backgroundColor: "#ffffff",
    borderRadius: 20,
    padding: 24,
    gap: 12,
    shadowColor: "#0f172a",
    shadowOffset: { width: 0, height: 12 },
    shadowOpacity: 0.18,
    shadowRadius: 24,
    elevation: 8,
  },
  landingTitle: {
    fontSize: 20,
    fontWeight: "700",
    color: "#0f172a",
  },
  landingText: {
    fontSize: 13,
    color: "#475569",
  },
  primaryButton: {
    backgroundColor: "#2563eb",
    borderRadius: 12,
    paddingVertical: 12,
    alignItems: "center",
  },
  primaryButtonText: {
    color: "#ffffff",
    fontWeight: "700",
    fontSize: 13,
  },
  secondaryButton: {
    backgroundColor: "#f1f5f9",
    borderRadius: 12,
    paddingVertical: 12,
    alignItems: "center",
  },
  secondaryButtonText: {
    color: "#1e293b",
    fontWeight: "600",
    fontSize: 13,
  },
  mobileSafe: {
    flex: 1,
    backgroundColor: "#f8fafc",
  },
  mobileHeader: {
    padding: 16,
    backgroundColor: "#ffffff",
    borderBottomWidth: 1,
    borderBottomColor: "#e2e8f0",
    flexDirection: "row",
    justifyContent: "space-between",
    alignItems: "center",
  },
  mobileHeaderTitle: {
    fontSize: 16,
    fontWeight: "700",
    color: "#0f172a",
  },
  exitButton: {
    paddingHorizontal: 12,
    paddingVertical: 6,
    borderRadius: 999,
    backgroundColor: "#e2e8f0",
  },
  exitButtonText: {
    fontSize: 11,
    fontWeight: "700",
    color: "#334155",
  },
  mobileContent: {
    padding: 16,
    paddingBottom: 80,
    gap: 16,
  },
  onboardingSafe: {
    flex: 1,
    backgroundColor: "#2563eb",
  },
  onboardingHero: {
    flex: 1,
    padding: 20,
    justifyContent: "center",
    gap: 16,
  },
  onboardingTop: {
    flexDirection: "row",
    justifyContent: "space-between",
  },
  onboardingExit: {
    color: "#ffffff",
    fontWeight: "600",
  },
  onboardingStep: {
    color: "#e0e7ff",
    fontWeight: "600",
  },
  onboardingCard: {
    backgroundColor: "#ffffff",
    borderRadius: 20,
    padding: 20,
    gap: 10,
  },
  onboardingTitle: {
    fontSize: 20,
    fontWeight: "700",
    color: "#0f172a",
  },
  onboardingText: {
    fontSize: 13,
    color: "#475569",
  },
  onboardingList: {
    gap: 6,
  },
  onboardingBullet: {
    fontSize: 12,
    color: "#475569",
  },
  navBar: {
    position: "absolute",
    bottom: 0,
    left: 0,
    right: 0,
    flexDirection: "row",
    justifyContent: "space-around",
    paddingVertical: 8,
    borderTopWidth: 1,
    borderTopColor: "#e2e8f0",
    backgroundColor: "#ffffff",
  },
  navItem: {
    alignItems: "center",
    gap: 4,
  },
  navLabel: {
    fontSize: 10,
    color: "#94a3b8",
  },
  navLabelActive: {
    color: "#2563eb",
    fontWeight: "700",
  },
  section: {
    gap: 12,
  },
  sectionHeader: {
    flexDirection: "row",
    justifyContent: "space-between",
    alignItems: "center",
  },
  sectionTitle: {
    fontSize: 18,
    fontWeight: "700",
    color: "#0f172a",
  },
  sectionText: {
    fontSize: 12,
    color: "#64748b",
  },
  cardSmall: {
    backgroundColor: "#ffffff",
    padding: 12,
    borderRadius: 12,
    shadowColor: "#0f172a",
    shadowOffset: { width: 0, height: 8 },
    shadowOpacity: 0.08,
    shadowRadius: 16,
    elevation: 3,
    gap: 4,
  },
  cardLabel: {
    fontSize: 11,
    color: "#64748b",
  },
  cardValue: {
    fontSize: 16,
    fontWeight: "700",
    color: "#0f172a",
  },
  card: {
    backgroundColor: "#ffffff",
    padding: 14,
    borderRadius: 14,
    shadowColor: "#0f172a",
    shadowOffset: { width: 0, height: 8 },
    shadowOpacity: 0.08,
    shadowRadius: 16,
    elevation: 3,
    gap: 6,
  },
  cardTitle: {
    fontSize: 14,
    fontWeight: "700",
    color: "#0f172a",
  },
  navHeader: {
    padding: 16,
    flexDirection: "row",
    justifyContent: "space-between",
    alignItems: "center",
    borderBottomWidth: 1,
    borderBottomColor: "#e2e8f0",
    backgroundColor: "#ffffff",
  },
  navBack: {
    color: "#2563eb",
    fontWeight: "700",
  },
  navTitle: {
    fontSize: 14,
    fontWeight: "700",
    color: "#0f172a",
  },
  navMap: {
    flex: 1,
    alignItems: "center",
    justifyContent: "center",
    gap: 10,
  },
  dashboardSafe: {
    flex: 1,
    backgroundColor: "#eef2f7",
  },
  dashboardContainer: {
    flex: 1,
    flexDirection: "row",
  },
  sidebar: {
    width: 260,
    backgroundColor: "#0f172a",
    paddingVertical: 24,
    paddingHorizontal: 16,
  },
  sidebarCollapsed: {
    width: 72,
  },
  sidebarHeader: {
    paddingBottom: 16,
    borderBottomWidth: 1,
    borderBottomColor: "rgba(148,163,184,0.3)",
  },
  brandTitle: {
    color: "#ffffff",
    fontWeight: "700",
    fontSize: 18,
  },
  brandSubtitle: {
    color: "#94a3b8",
    marginTop: 4,
    fontSize: 12,
  },
  sidebarMenu: {
    paddingVertical: 18,
    gap: 10,
  },
  menuButton: {
    flexDirection: "row",
    alignItems: "center",
    gap: 12,
    paddingVertical: 10,
    paddingHorizontal: 12,
    borderRadius: 12,
  },
  menuButtonActive: {
    backgroundColor: "#2563eb",
  },
  menuLabel: {
    color: "#c7d2fe",
    fontSize: 13,
    fontWeight: "600",
  },
  menuLabelActive: {
    color: "#ffffff",
  },
  sidebarFooter: {
    borderTopWidth: 1,
    borderTopColor: "rgba(148,163,184,0.3)",
    paddingTop: 16,
    gap: 12,
  },
  userRow: {
    flexDirection: "row",
    alignItems: "center",
    gap: 10,
  },
  userAvatar: {
    width: 38,
    height: 38,
    borderRadius: 19,
    backgroundColor: "#2563eb",
    alignItems: "center",
    justifyContent: "center",
  },
  userAvatarText: {
    color: "#ffffff",
    fontWeight: "700",
    fontSize: 12,
  },
  userInfo: {
    flex: 1,
  },
  userName: {
    color: "#ffffff",
    fontSize: 12,
    fontWeight: "700",
  },
  userRole: {
    color: "#94a3b8",
    fontSize: 11,
  },
  logoutButton: {
    flexDirection: "row",
    alignItems: "center",
    gap: 8,
    backgroundColor: "#dc2626",
    paddingVertical: 10,
    paddingHorizontal: 12,
    borderRadius: 12,
  },
  logoutText: {
    color: "#ffffff",
    fontSize: 12,
    fontWeight: "700",
  },
  dashboardContent: {
    flex: 1,
    backgroundColor: "#f1f5f9",
  },
  topBar: {
    paddingHorizontal: 20,
    paddingVertical: 14,
    backgroundColor: "#ffffff",
    borderBottomWidth: 1,
    borderBottomColor: "#e2e8f0",
    flexDirection: "row",
    justifyContent: "space-between",
    alignItems: "center",
  },
  iconButton: {
    width: 36,
    height: 36,
    borderRadius: 10,
    backgroundColor: "#f8fafc",
    alignItems: "center",
    justifyContent: "center",
  },
  topRight: {
    flexDirection: "row",
    alignItems: "center",
    gap: 12,
  },
  statusPill: {
    backgroundColor: "#dcfce7",
    paddingHorizontal: 10,
    paddingVertical: 4,
    borderRadius: 999,
  },
  statusText: {
    color: "#15803d",
    fontSize: 11,
    fontWeight: "700",
  },
  dateText: {
    fontSize: 11,
    color: "#64748b",
  },
  panel: {
    margin: 20,
    padding: 20,
    backgroundColor: "#ffffff",
    borderRadius: 16,
    shadowColor: "#0f172a",
    shadowOffset: { width: 0, height: 10 },
    shadowOpacity: 0.08,
    shadowRadius: 16,
    elevation: 4,
    gap: 6,
  },
  panelTitle: {
    fontSize: 18,
    fontWeight: "700",
    color: "#0f172a",
  },
  panelText: {
    fontSize: 13,
    color: "#475569",
  },
});
