// In production, this would point to your deployed backend URL.
// For local development, it points to the FastAPI local server.
export const API_BASE_URL = 'https://pastelink-andget.onrender.com';

export const ANIMATION_VARIANTS = {
  hidden: { opacity: 0, y: 20 },
  visible: { opacity: 1, y: 0 },
  exit: { opacity: 0, y: -20 }
};