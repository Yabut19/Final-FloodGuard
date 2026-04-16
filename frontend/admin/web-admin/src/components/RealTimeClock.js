import React, { useState, useEffect } from "react";
import { Text } from "react-native";
import { formatDateTime } from "../utils/helpers";

const RealTimeClock = ({ style }) => {
    const [dateTime, setDateTime] = useState(() => {
        const now = new Date();
        return formatDateTime(now);
    });

    useEffect(() => {
        const tick = () => {
            const now = new Date();
            setDateTime(formatDateTime(now));
        };
        tick();
        const interval = setInterval(tick, 1000);
        return () => clearInterval(interval);
    }, []);

    return <Text style={style}>{dateTime}</Text>;
};

export default RealTimeClock;
