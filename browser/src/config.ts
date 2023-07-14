
export const isDevelopmentMode = !process.env.NODE_ENV || process.env.NODE_ENV === 'development';

export const SERVICE_PREFIX: string = isDevelopmentMode ? "http://localhost:5000" : "";
export const WS_SERVICE: string = isDevelopmentMode ? "ws://localhost:5000/ws" : "ws://" + window.location.host + "/ws";
