
export const isDevelopmentMode = !process.env.NODE_ENV || process.env.NODE_ENV === 'development';

export const SERVICE_PREFIX: string = isDevelopmentMode ? "http://localhost:5000" : "";
