import React, { useState, useEffect } from "react";
import { Text } from "react-native";
import { formatPST } from "../utils/dateUtils";

const RealTimeClock = ({ style }) => {
    const [dateTime, setDateTime] = useState(() => {
        const now = new Date();
        return formatPST(now);
    });

    useEffect(() => {
        const tick = () => {
            const now = new Date();
            setDateTime(formatPST(now));
        };
        tick();
        const interval = setInterval(tick, 1000);
        return () => clearInterval(interval);
    }, []);

    return <Text style={style}>{dateTime}</Text>;
};

export default RealTimeClock;
