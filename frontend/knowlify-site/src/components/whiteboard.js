import React, { useRef, useEffect, useState, forwardRef, useImperativeHandle } from 'react';

const Whiteboard = forwardRef(({ coordinates, onEnded }, ref) => {
  const canvasRef = useRef(null);
  const animationRef = useRef(null);
  const indexRef = useRef(0);
  const [isDrawing, setIsDrawing] = useState(false);
  const elapsedTimeRef = useRef(0);
  const lastTimestampRef = useRef(null);
  const pixelsPerSecond = 150;
  const isPausedRef = useRef(false);
  const allCoordinatesRef = useRef([]);

  const drawPixelsInBatches = (timestamp) => {
    if (!lastTimestampRef.current) {
      lastTimestampRef.current = timestamp;
    }

    const deltaTime = timestamp - lastTimestampRef.current;
    lastTimestampRef.current = timestamp;

    if (!isPausedRef.current) {
      elapsedTimeRef.current += deltaTime;
    }

    const canvas = canvasRef.current;
    const ctx = canvas.getContext('2d');

    const targetIndex = Math.min(Math.floor(elapsedTimeRef.current / 1000 * pixelsPerSecond), coordinates.length);

    while (indexRef.current < targetIndex) {
      const [x, y] = coordinates[indexRef.current];
      ctx.fillStyle = 'white';
      ctx.fillRect(x, y, 1, 1);
      indexRef.current++;
    }

    if (indexRef.current < coordinates.length) {
      animationRef.current = requestAnimationFrame(drawPixelsInBatches);
    } else {
      setIsDrawing(false);
      if (onEnded) onEnded();
    }
  };

  useImperativeHandle(ref, () => ({
    pause: () => {
      isPausedRef.current = true;
    },
    resume: () => {
      isPausedRef.current = false;
      if (isDrawing && !animationRef.current) {
        animationRef.current = requestAnimationFrame(drawPixelsInBatches);
      }
    },
    seek: (time) => {
      const canvas = canvasRef.current;
      const ctx = canvas.getContext('2d');

      const newIndex = Math.min(Math.floor(time * pixelsPerSecond), coordinates.length);
      indexRef.current = newIndex;
      elapsedTimeRef.current = time * 1000;

      allCoordinatesRef.current.forEach(([x, y]) => {
        ctx.fillStyle = 'white';
        ctx.fillRect(x, y, 1, 1);
      });

      for (let i = 0; i < newIndex; i++) {
        const [x, y] = coordinates[i];
        ctx.fillStyle = 'white';
        ctx.fillRect(x, y, 1, 1);
      }

      lastTimestampRef.current = null;
    },
    getDuration: () => {
      return coordinates.length / pixelsPerSecond;
    },
    // drawEndState: () => {
    //   const canvas = canvasRef.current;
    //   const ctx = canvas.getContext('2d');

    //   allCoordinatesRef.current = [...allCoordinatesRef.current, ...coordinates];
      
    //   allCoordinatesRef.current.forEach(([x, y]) => {
    //     ctx.fillStyle = 'white';
    //     ctx.fillRect(x, y, 1, 1);
    //   });

    //   indexRef.current = coordinates.length;
    //   elapsedTimeRef.current = coordinates.length / pixelsPerSecond * 1000;
    //   setIsDrawing(false);
    //   if (onEnded) onEnded();
    // },
    clearAll: () => {
      const canvas = canvasRef.current;
      const ctx = canvas.getContext('2d');
      ctx.clearRect(0, 0, canvas.width, canvas.height);
      allCoordinatesRef.current = [];
    },

    finishPixels: () => {
      const canvas = canvasRef.current;
      const ctx = canvas.getContext('2d');

      coordinates.forEach(([x, y]) => {
        ctx.fillStyle = 'white';
        ctx.fillRect(x, y, 1, 1);
      });

      // Stop the ongoing animation
      if (animationRef.current) {
        cancelAnimationFrame(animationRef.current);
      }

      setIsDrawing(false);
      indexRef.current = coordinates.length;
      elapsedTimeRef.current = coordinates.length / pixelsPerSecond * 1000;
    },

    removePixels: () => {
      const canvas = canvasRef.current;
      const ctx = canvas.getContext('2d');

      coordinates.forEach(([x, y]) => {
        ctx.fillStyle = 'rgb(40, 40, 40)';
        ctx.fillRect(x, y, 1, 1);
      });

      if (animationRef.current) {
        cancelAnimationFrame(animationRef.current);
      }

      setIsDrawing(false);
      indexRef.current = coordinates.length;
      elapsedTimeRef.current = coordinates.length / pixelsPerSecond * 1000;
    },
  }));

  useEffect(() => {
    const canvas = canvasRef.current;
    const ctx = canvas.getContext('2d');

    indexRef.current = 0;
    elapsedTimeRef.current = 0;
    lastTimestampRef.current = null;
    setIsDrawing(coordinates.length > 0);

    if (coordinates.length > 0) {
      animationRef.current = requestAnimationFrame(drawPixelsInBatches);
    }

    return () => {
      if (animationRef.current) {
        cancelAnimationFrame(animationRef.current);
      }
    };
  }, [coordinates]);

  return (
    <>
      <canvas ref={canvasRef} width={600} height={400} style={{ border: '1px solid white' }} />
    </>
  );
});

export default Whiteboard;