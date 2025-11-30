export type Platform = 'youtube' | 'tiktok' | 'instagram' | 'unknown';

export type DownloadType = 'mp4' | 'mp3';

export interface DownloadResponse {
  filename: string;
  data: string; // Base64 encoded string
  status: 'success' | 'error';
  message?: string;
}

export interface ApiError {
  detail: string;
}

export interface DownloadRequest {
  url: string;
  kind: DownloadType;
}