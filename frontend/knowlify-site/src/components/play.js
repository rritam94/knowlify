import React, { useEffect, useRef, forwardRef, useImperativeHandle, useState } from 'react';

const AudioPlayer = forwardRef(({ audioBytes, onEnded, isPaused, isAudioEnded, currentTime }, ref) => {
  const audioRef = useRef(null);
  const urlRef = useRef(null);
  const [isReady, setIsReady] = useState(false);
  const [duration, setDuration] = useState(0);
  const [localIsAudioEnded, setLocalIsAudioEnded] = useState(isAudioEnded);

  useImperativeHandle(ref, () => ({
    pause: () => {
      if (audioRef.current) {
        audioRef.current.pause();
      }
    },
    resume: () => {
      if (audioRef.current && !localIsAudioEnded) {
        audioRef.current.play().catch(error => {
          console.error('Audio playback failed:', error);
        });
      }
    },
    seek: (time) => {
      if (audioRef.current) {
        audioRef.current.currentTime = time;
        if (time < audioRef.current.duration) {
          setLocalIsAudioEnded(false);
        }
      }
    },
    stop: () => {
      if (audioRef.current) {
        audioRef.current.pause();
        audioRef.current.currentTime = 0;
      }
    },
    getCurrentTime: () => audioRef.current ? audioRef.current.currentTime : 0,
    getDuration: () => audioRef.current ? audioRef.current.duration : 0,
  }));

  useEffect(() => {
    if (audioBytes) {
      const byteArray = new Uint8Array(audioBytes.split('').map(char => char.charCodeAt(0)));
      const blob = new Blob([byteArray], { type: 'audio/wav' });
      const url = URL.createObjectURL(blob);

      const handleAudioEnded = () => {
        setLocalIsAudioEnded(true);
        if (onEnded) onEnded();
      };

      const audio = new Audio(url);
      audio.addEventListener('ended', handleAudioEnded);
      audio.addEventListener('canplaythrough', () => setIsReady(true));
      audio.addEventListener('loadedmetadata', () => setDuration(audio.duration));

      audioRef.current = audio;
      urlRef.current = url;

      return () => {
        audio.removeEventListener('ended', handleAudioEnded);
        audio.removeEventListener('canplaythrough', () => setIsReady(true));
        audio.removeEventListener('loadedmetadata', () => setDuration(audio.duration));
        audio.pause();
        URL.revokeObjectURL(url);
      };
    }
  }, [audioBytes, onEnded]);

  useEffect(() => {
    if (isReady && audioRef.current) {
      if (!isPaused && !localIsAudioEnded) {
        audioRef.current.play().catch(error => {
          console.error('Audio playback failed:', error);
        });
      } else {
        audioRef.current.pause();
      }
    }
  }, [isPaused, isReady, localIsAudioEnded]);

  useEffect(() => {
    if (audioRef.current && !isPaused && !localIsAudioEnded) {
      audioRef.current.play().catch(error => {
        console.error('Audio playback failed:', error);
      });
    }
  }, [currentTime, isPaused, localIsAudioEnded]);

  useEffect(() => {
    setLocalIsAudioEnded(isAudioEnded);
  }, [isAudioEnded]);

  return null;
});

export default AudioPlayer;