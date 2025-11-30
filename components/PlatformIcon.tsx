import React from 'react';
import { Platform } from '../types';
import { Youtube, Instagram, Music, Link as LinkIcon } from 'lucide-react';

interface PlatformIconProps {
  platform: Platform;
}

const PlatformIcon: React.FC<PlatformIconProps> = ({ platform }) => {
  const iconClass = "w-6 h-6 transition-all";
  switch (platform) {
    case 'youtube':
      return <Youtube className={`${iconClass} text-red-500`} />;
    case 'tiktok':
      return <Music className={`${iconClass} text-cyan-400`} />;
    case 'instagram':
      return <Instagram className={`${iconClass} text-pink-500`} />;
    default:
      return <LinkIcon className={`${iconClass} text-white/50`} />;
  }
};

export default PlatformIcon;