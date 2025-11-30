import React, { useState, useEffect } from 'react';
import { Platform, DownloadType } from './types';
import { downloadMedia, triggerBrowserDownload } from './services/apiService';
import GlassCard from './components/GlassCard';
import PlatformIcon from './components/PlatformIcon';
import { Loader2, Download, AlertCircle, CheckCircle2, Video, Music } from 'lucide-react';

const App: React.FC = () => {
  const [url, setUrl] = useState('');
  const [platform, setPlatform] = useState<Platform>('unknown');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [success, setSuccess] = useState<string | null>(null);
  const [progress, setProgress] = useState<string>('');

  // Auto-detect platform
  useEffect(() => {
    if (url.includes('youtube.com') || url.includes('youtu.be')) {
      setPlatform('youtube');
    } else if (url.includes('tiktok.com')) {
      setPlatform('tiktok');
    } else if (url.includes('instagram.com')) {
      setPlatform('instagram');
    } else {
      setPlatform('unknown');
    }
  }, [url]);

  const handleDownload = async (kind: DownloadType) => {
    if (!url) {
      setError("Please paste a link first.");
      setTimeout(() => setError(null), 3000);
      return;
    }
    
    setError(null);
    setSuccess(null);
    setLoading(true);
    setProgress('Initializing download...');

    try {
      // Simulate progress stages for better UX since backend process is opaque
      const progressTimer = setInterval(() => {
         setProgress((prev) => {
           if(prev === 'Initializing download...') return 'Fetching media info...';
           if(prev === 'Fetching media info...') return 'Processing on server...';
           if(prev === 'Processing on server...') return 'Encoding... this may take a moment';
           return prev;
         })
      }, 2500);

      const response = await downloadMedia({ url, kind });
      
      clearInterval(progressTimer);
      setProgress('Finalizing download...');

      if (response.status === 'error') {
        throw new Error(response.message || 'Unknown error occurred');
      }

      // Determine MIME type
      const mimeType = kind === 'mp4' ? 'video/mp4' : 'audio/mpeg';
      
      triggerBrowserDownload(response.data, response.filename, mimeType);
      
      setSuccess(`Downloaded ${response.filename} successfully!`);
      setUrl(''); // Reset input on success
      setTimeout(() => setSuccess(null), 5000);
    } catch (err: any) {
      setError(err.message || "An unexpected error occurred.");
    } finally {
      setLoading(false);
      setProgress('');
    }
  };

  return (
    <div className="min-h-screen w-full flex items-center justify-center relative bg-slate-900 overflow-hidden p-4">
      {/* Liquid Background Elements */}
      <div className="absolute top-[-10%] left-[-10%] w-[500px] h-[500px] bg-purple-600 rounded-full mix-blend-multiply filter blur-[128px] opacity-50 animate-blob"></div>
      <div className="absolute top-[-10%] right-[-10%] w-[500px] h-[500px] bg-cyan-600 rounded-full mix-blend-multiply filter blur-[128px] opacity-50 animate-blob animation-delay-2000"></div>
      <div className="absolute bottom-[-20%] left-[20%] w-[500px] h-[500px] bg-pink-600 rounded-full mix-blend-multiply filter blur-[128px] opacity-50 animate-blob animation-delay-4000"></div>

      <div className="w-full max-w-md z-10">
        <div className="mb-8 text-center">
          <h1 className="text-4xl font-bold text-transparent bg-clip-text bg-gradient-to-r from-white to-white/70 tracking-tight mb-2">
            PasteLink<span className="text-cyan-400">And</span>Get
          </h1>
        </div>

        <GlassCard>
          <div className="relative group mb-6">
            <div className="absolute inset-y-0 left-0 pl-4 flex items-center pointer-events-none transition-transform group-focus-within:scale-110">
              <PlatformIcon platform={platform} />
            </div>
            <input
              type="text"
              value={url}
              onChange={(e) => setUrl(e.target.value)}
              placeholder="Paste YouTube, TikTok, or Instagram link..."
              className="w-full bg-white/5 border border-white/10 rounded-xl py-4 pl-12 pr-4 text-white placeholder-white/30 focus:outline-none focus:ring-2 focus:ring-cyan-500/50 focus:bg-white/10 transition-all duration-300"
              disabled={loading}
            />
            <div className="absolute -inset-0.5 bg-gradient-to-r from-cyan-500 to-purple-500 rounded-xl opacity-0 group-focus-within:opacity-20 transition duration-500 -z-10 blur-md"></div>
          </div>

          <div className="grid grid-cols-2 gap-4 mb-6">
            <button
              onClick={() => handleDownload('mp4')}
              disabled={loading || !url}
              className="relative overflow-hidden group bg-gradient-to-br from-indigo-600/80 to-purple-700/80 hover:from-indigo-500 hover:to-purple-600 text-white p-4 rounded-xl flex flex-col items-center justify-center gap-2 transition-all duration-300 disabled:opacity-50 disabled:cursor-not-allowed border border-white/10 shadow-lg hover:shadow-indigo-500/25"
            >
              <div className="absolute inset-0 bg-white/20 translate-y-full group-hover:translate-y-0 transition-transform duration-300"></div>
              <Video size={24} className="mb-1" />
              <span className="font-semibold text-sm z-10">Download MP4</span>
              <span className="text-[10px] text-white/50 z-10">Video</span>
            </button>

            <button
              onClick={() => handleDownload('mp3')}
              disabled={loading || !url}
              className="relative overflow-hidden group bg-gradient-to-br from-pink-600/80 to-rose-700/80 hover:from-pink-500 hover:to-rose-600 text-white p-4 rounded-xl flex flex-col items-center justify-center gap-2 transition-all duration-300 disabled:opacity-50 disabled:cursor-not-allowed border border-white/10 shadow-lg hover:shadow-pink-500/25"
            >
              <div className="absolute inset-0 bg-white/20 translate-y-full group-hover:translate-y-0 transition-transform duration-300"></div>
              <div className="relative z-10 flex flex-col items-center">
                 <Music size={24} className="mb-1" />
                 <span className="font-semibold text-sm">Download MP3</span>
                 <span className="text-[10px] text-white/50">Audio</span>
              </div>
            </button>
          </div>

          <div className="space-y-4 h-24">
             {loading && (
               <div className="flex flex-col items-center text-center p-4 bg-white/5 rounded-xl border border-white/5">
                  <Loader2 className="animate-spin text-cyan-400 w-8 h-8 mb-2" />
                  <p className="text-white text-sm font-medium">{progress}</p>
                  <p className="text-white/40 text-xs mt-1">Please be patient...</p>
               </div>
             )}

             {error && (
               <div className="flex items-start gap-3 p-4 bg-red-500/10 border border-red-500/20 rounded-xl text-red-200 text-sm">
                 <AlertCircle className="w-5 h-5 shrink-0 mt-0.5" />
                 <span>{error}</span>
               </div>
             )}

             {success && (
               <div className="flex items-start gap-3 p-4 bg-green-500/10 border border-green-500/20 rounded-xl text-green-200 text-sm">
                 <CheckCircle2 className="w-5 h-5 shrink-0 mt-0.5" />
                 <span>{success}</span>
               </div>
             )}
          </div>
        </GlassCard>

        {/* Footer removed as requested */}
      </div>
    </div>
  );
};

export default App;