import { io } from "socket.io-client";
import { API_BASE_URL } from "../config/api";

// Singleton socket instance to maintain connection across navigation
let globalSocket = null;

/**
 * getSocket
 * Returns the current socket instance or creates a new one if it doesn't exist.
 */
export const getSocket = () => {
  if (!globalSocket && typeof window !== "undefined") {
    console.log("[SocketManager] Creating new persistent socket connection...");
    globalSocket = io(API_BASE_URL, {
      transports: ["websocket", "polling"],
      reconnection: true,
      reconnectionAttempts: Infinity,
      reconnectionDelay: 1000,
      reconnectionDelayMax: 5000,
      timeout: 20000
    });
    
    globalSocket.on("connect", () => {
      console.log("[SocketManager] Persistent WebSocket Connected");
    });
    
    globalSocket.on("disconnect", (reason) => {
      console.log("[SocketManager] Persistent WebSocket Disconnected:", reason);
    });
    
    globalSocket.on("force_logout", (data) => {
      try {
        const currentId = localStorage.getItem("userId");
        const currentRole = localStorage.getItem("userRole");
        if (currentId && currentRole) {
          const myType = (currentRole === "super_admin" || currentRole === "admin") ? "a" : "u";
          if (String(currentId) === String(data.id) && myType === data.type) {
            console.log("[SocketManager] Force logout received for this account.");
            localStorage.removeItem("authToken");
            localStorage.removeItem("userRole");
            localStorage.removeItem("activePage");
            localStorage.removeItem("userId");
            sessionStorage.removeItem("welcomeBannerShown");
            window.location.reload();
          }
        }
      } catch (error) {
        console.warn("Error processing force_logout:", error);
      }
    });
  }
  return globalSocket;
};

/**
 * disconnectSocket
 * Manually disconnects and nullifies the global socket instance.
 * Useful during logout to ensure a fresh connection on the next login.
 */
export const disconnectSocket = () => {
  if (globalSocket) {
    console.log("[SocketManager] Manually disconnecting socket...");
    globalSocket.disconnect();
    globalSocket = null;
  }
};
