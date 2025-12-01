import { API_BASE_URL } from '../constants';
import { DownloadRequest, DownloadResponse, DownloadType } from '../types';

export const downloadMedia = async (url: string, format: DownloadType = 'mp4'): Promise<DownloadResponse> => {
  try {
    if (!url) {
        throw new Error("URL is required");
    }

    const request: DownloadRequest = { url, format };

    const response = await fetch(`${API_BASE_URL}/download`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(request),
    });

    if (!response.ok) {
      const errorData = await response.json().catch(() => ({ detail: `Server returned an invalid response. Status: ${response.status}` }));
      throw new Error(errorData.detail || `An unknown server error occurred.`);
    }

    const data: DownloadResponse = await response.json();
    return data;
  } catch (error: any) {
    console.error("Download failed:", error);
    
    let message = error.message || "Failed to communicate with the backend.";
    
    if (error instanceof TypeError) { // Catches network errors like "Failed to fetch"
      message = "Cannot connect to server. Is the backend running on port 8000?";
    }
    
    throw new Error(message);
  }
};

export const triggerBrowserDownload = (base64Data: string, filename: string, mimeType: string) => {
  try {
    // Convert Base64 to Blob
    const byteCharacters = atob(base64Data);
    const byteNumbers = new Array(byteCharacters.length);
    for (let i = 0; i < byteCharacters.length; i++) {
        byteNumbers[i] = byteCharacters.charCodeAt(i);
    }
    const byteArray = new Uint8Array(byteNumbers);
    const blob = new Blob([byteArray], { type: mimeType });

    // Create Object URL and Trigger Download
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = filename;
    document.body.appendChild(a);
    a.click();
    
    // Cleanup
    setTimeout(() => {
        document.body.removeChild(a);
        window.URL.revokeObjectURL(url);
    }, 100);
  } catch (e) {
    console.error("Error triggering download:", e);
    alert("Failed to save file. Your browser might be blocking the download.");
  }
};