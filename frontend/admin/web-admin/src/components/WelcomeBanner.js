import React, { useEffect, useRef } from 'react';
import { View, Text, Animated, StyleSheet, Easing, Dimensions } from 'react-native';
import { Feather } from '@expo/vector-icons';

const { width } = Dimensions.get('window');

const WelcomeBanner = ({ userName }) => {
    const [shouldShow, setShouldShow] = React.useState(false);
    const scaleAnim = useRef(new Animated.Value(0.8)).current;
    const opacityAnim = useRef(new Animated.Value(0)).current;

    // Confetti animation values (30 pieces for a rich background)
    const confettiCount = 30;
    const confettiValues = useRef([...Array(confettiCount)].map(() => new Animated.Value(0))).current;

    useEffect(() => {
        const hasShown = sessionStorage.getItem('welcomeBannerShown');
        if (hasShown) return;

        sessionStorage.setItem('welcomeBannerShown', 'true');
        setShouldShow(true);

        confettiValues.forEach(v => v.setValue(0));

        Animated.parallel([
            Animated.timing(scaleAnim, {
                toValue: 1,
                duration: 600,
                easing: Easing.out(Easing.back(1.5)),
                useNativeDriver: true,
            }),
            Animated.timing(opacityAnim, {
                toValue: 1,
                duration: 500,
                useNativeDriver: true,
            }),
            // Staggered confetti burst
            Animated.stagger(10, confettiValues.map(v =>
                Animated.timing(v, {
                    toValue: 1,
                    duration: 1200,
                    easing: Easing.out(Easing.exp),
                    useNativeDriver: true,
                })
            ))
        ]).start(() => {
            setTimeout(() => {
                Animated.parallel([
                    Animated.timing(scaleAnim, {
                        toValue: 0.8,
                        duration: 500,
                        easing: Easing.in(Easing.ease),
                        useNativeDriver: true,
                    }),
                    Animated.timing(opacityAnim, {
                        toValue: 0,
                        duration: 400,
                        useNativeDriver: true,
                    })
                ]).start(() => setShouldShow(false));
            }, 1500); // Display for 1.5s
        });
    }, []);

    if (!shouldShow) return null;

    const firstName = userName ? userName.split(' ')[0] : 'Hero';

    // Generate randomized confetti data that bursts FROM the center
    const confettiData = [...Array(confettiCount)].map((_, i) => {
        const angle = (Math.random() * 2 * Math.PI); // Random direction in radians
        const velocity = 200 + Math.random() * 300; // Random distance/speed
        return {
            color: ['#3b82f6', '#ef4444', '#f59e0b', '#10b981', '#8b5cf6', '#ec4899'][i % 6],
            finalRotate: `${(Math.random() - 0.5) * 500}deg`,
            size: 6 + Math.random() * 8,
            // Calculate X and Y directions based on random angle
            xDir: Math.cos(angle) * velocity,
            yDir: Math.sin(angle) * velocity,
        };
    });

    return (
        <View style={styles.bannerWrapper}>
            {/* Background Confetti Burst - ORIGINATING FROM CENTER */}
            {confettiData.map((c, i) => {
                const translateY = confettiValues[i].interpolate({
                    inputRange: [0, 1],
                    outputRange: [0, c.yDir]
                });
                const translateX = confettiValues[i].interpolate({
                    inputRange: [0, 1],
                    outputRange: [0, c.xDir]
                });
                const scale = confettiValues[i].interpolate({
                    inputRange: [0, 0.1, 1],
                    outputRange: [0, 1.5, 1]
                });
                const rotate = confettiValues[i].interpolate({
                    inputRange: [0, 1],
                    outputRange: ['0deg', c.finalRotate]
                });

                return (
                    <Animated.View
                        key={i}
                        style={[
                            styles.confetti,
                            {
                                backgroundColor: c.color,
                                top: '50%', // Start exactly at the vertical center
                                left: '50%', // Start exactly at the horizontal center
                                width: c.size,
                                height: c.size * 1.5,
                                opacity: confettiValues[i].interpolate({
                                    inputRange: [0, 0.8, 1],
                                    outputRange: [0, 1, 0] // Fade out at the end of the burst
                                }),
                                transform: [
                                    { translateX: translateX },
                                    { translateY: translateY },
                                    { scale: scale },
                                    { rotate: rotate }
                                ]
                            }
                        ]}
                    />
                );
            })}

            <Animated.View
                style={[
                    styles.bannerContainer,
                    {
                        opacity: opacityAnim,
                        transform: [{ scale: scaleAnim }]
                    }
                ]}
            >
                <View style={styles.content}>
                    <Text style={styles.emoji}>🎉</Text>
                    <Text style={styles.welcomeTitle}>Welcome back, {firstName}!</Text>
                    <Text style={styles.subTitleText}>Ready to monitor, alert, and protect the community today?</Text>
                </View>
            </Animated.View>
        </View>
    );
};

const styles = StyleSheet.create({
    bannerWrapper: {
        position: 'absolute',
        top: 0,
        left: 0,
        right: 0,
        bottom: 0,
        alignItems: 'center',
        justifyContent: 'center',
        zIndex: 9999,
        backgroundColor: 'rgba(255,255,255,0.8)', // Lighter backdrop to show confetti better
    },
    bannerContainer: {
        backgroundColor: '#ffffff',
        borderRadius: 32,
        padding: 48,
        width: width > 768 ? 550 : '90%',
        maxWidth: 600,
        shadowColor: '#000',
        shadowOffset: { width: 0, height: 25 },
        shadowOpacity: 0.2,
        shadowRadius: 40,
        elevation: 20,
        borderWidth: 1,
        borderColor: 'rgba(0,0,0,0.03)',
        // No overflow hidden so banner can feel integrated with background
    },
    confetti: {
        position: 'absolute',
        borderRadius: 2,
        zIndex: -1, // Behind the banner
    },
    content: {
        alignItems: 'center',
        justifyContent: 'center',
    },
    emoji: {
        fontSize: 64,
        marginBottom: 24,
    },
    welcomeTitle: {
        fontSize: 28,
        fontFamily: 'Poppins_700Bold',
        color: '#1e293b',
        textAlign: 'center',
        marginBottom: 12,
    },
    subTitleText: {
        fontSize: 18,
        fontFamily: 'Poppins_400Regular',
        color: '#64748b',
        textAlign: 'center',
        lineHeight: 26,
    }
});

export default WelcomeBanner;
