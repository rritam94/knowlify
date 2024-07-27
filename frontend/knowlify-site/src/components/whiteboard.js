import React, { useRef, useEffect, useState } from 'react';

const Whiteboard = ({ coordinates, onEnded, clearOnUpdate }) => {
  const canvasRef = useRef(null);
  const animationRef = useRef(null);
  const indexRef = useRef(0);
  const [isDrawing, setIsDrawing] = useState(false);

  useEffect(() => {
    const canvas = canvasRef.current;
    const ctx = canvas.getContext('2d');

    if (clearOnUpdate) {
      ctx.clearRect(0, 0, canvas.width, canvas.height);
    }

    indexRef.current = 0;
    setIsDrawing(coordinates.length > 0);

    const drawPixel = () => {
      if (indexRef.current < coordinates.length) {
        const [x, y] = coordinates[indexRef.current];
        ctx.fillStyle = 'white';
        ctx.fillRect(x, y, 1, 1);
        indexRef.current++;
        animationRef.current = requestAnimationFrame(drawPixel);
      } else {
        setIsDrawing(false);
        if (onEnded) onEnded();
      }
    };

    if (coordinates.length > 0) {
      drawPixel();
    }

    return () => {
      if (animationRef.current) {
        cancelAnimationFrame(animationRef.current);
      }
    };
  }, [coordinates, clearOnUpdate, onEnded]);

  return (
    <>
      <canvas ref={canvasRef} width={600} height={400} style={{ border: '1px solid white' }} />
      {isDrawing && <p>Drawing in progress...</p>}
    </>
  );
};

export default Whiteboard;