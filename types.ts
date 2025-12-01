export type Platform = 'youtube' | 'instagram' | 'unknown';

export type DownloadType = 'mp4' | 'mp3';

export interface DownloadResponse {
  status: 'success' | 'error';
  filename: string;
  data: string; // Base64 encoded string
  message: string;
}

export interface ApiError {
  detail: string;
}

export interface DownloadRequest {
  url: string;
  format?: DownloadType;  // Optional - defaults to mp4
}