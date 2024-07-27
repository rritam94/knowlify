import React, { useEffect, useRef } from 'react';

const AudioPlayer = ({ audioBytes, onEnded }) => {
    const audioRef = useRef(null);
    const urlRef = useRef(null);

    useEffect(() => {
        if (audioBytes) {
            const byteArray = new Uint8Array(audioBytes.split('').map(char => char.charCodeAt(0)));
            const blob = new Blob([byteArray], { type: 'audio/wav' });
            const url = URL.createObjectURL(blob);

            const handleAudioEnded = () => {
                if (onEnded) onEnded();
                URL.revokeObjectURL(urlRef.current);
            };

            const setupNewAudio = () => {
                const audio = new Audio();
                audio.src = url;
                audio.addEventListener('ended', handleAudioEnded);
                audioRef.current = audio;
                urlRef.current = url;

                audio.load(); // Preload the audio
                return audio.play().catch(error => {
                    console.error('Error playing audio:', error);
                });
            };

            // Clean up previous audio
            if (audioRef.current) {
                audioRef.current.pause();
                audioRef.current.removeEventListener('ended', handleAudioEnded);
                audioRef.current.src = '';
                if (urlRef.current) {
                    URL.revokeObjectURL(urlRef.current);
                }
            }

            // Setup and play new audio
            setupNewAudio();

            return () => {
                if (audioRef.current) {
                    audioRef.current.pause();
                    audioRef.current.removeEventListener('ended', handleAudioEnded);
                }
                if (urlRef.current) {
                    URL.revokeObjectURL(urlRef.current);
                    urlRef.current = null;
                }
            };
        }
    }, [audioBytes, onEnded]);

    return null;
};

export default AudioPlayer;