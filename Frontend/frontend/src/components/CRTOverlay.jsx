import React from 'react';
import { motion } from 'framer-motion';

const CRTOverlay = () => {
  return (
    <div className="pointer-events-none fixed inset-0 z-50 overflow-hidden h-full w-full">
      {/* Static Scanlines */}
      <div className="absolute inset-0 bg-[linear-gradient(rgba(18,16,16,0)_50%,rgba(0,0,0,0.25)_50%),linear-gradient(90deg,rgba(255,0,0,0.06),rgba(0,255,0,0.02),rgba(0,0,255,0.06))] bg-[length:100%_2px,3px_100%] pointer-events-none" />
      
      {/* Moving Scanline Bar */}
      <motion.div 
        initial={{ top: "-100%" }}
        animate={{ top: "100%" }}
        transition={{ repeat: Infinity, duration: 6, ease: "linear" }}
        className="absolute w-full h-32 bg-gradient-to-b from-transparent via-white/5 to-transparent opacity-30"
      />
      
      {/* Vignette (Dark Corners) */}
      <div className="absolute inset-0 bg-[radial-gradient(circle,rgba(0,0,0,0)_60%,rgba(0,0,0,0.4)_100%)]" />
    </div>
  );
};

export default CRTOverlay;