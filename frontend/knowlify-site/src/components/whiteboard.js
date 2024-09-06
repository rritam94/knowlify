import React, { useRef, useEffect, useState, forwardRef, useImperativeHandle } from 'react';

const Whiteboard = forwardRef(({ coordinates, onEnded }, ref) => {
  const canvasRef = useRef(null);
  const containerRef = useRef(null);
  const animationRef = useRef(null);
  const indexRef = useRef(0);
  const [isPanning, setIsPanning] = useState(false);
  const [scale, setScale] = useState(1);
  const [translate, setTranslate] = useState({ x: 0, y: 0 });
  const pixelsPerSecond = 600;
  const elapsedTimeRef = useRef(0);
  const lastTimestampRef = useRef(null);
  const isPausedRef = useRef(false);
  const lastPanPositionRef = useRef({ x: 0, y: 0 });

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
      if (onEnded) onEnded();
    }
  };

  const handleWheel = (e) => {
    e.preventDefault();
    const scaleFactor = 1.1;
    if (e.deltaY < 0) {
      setScale((prevScale) => Math.min(prevScale * scaleFactor, 50));
    } else {
      setScale((prevScale) => Math.max(prevScale / scaleFactor, 0.25));
    }
  };

  const startPanning = (e) => {
    if (e.button !== 2) return;
    e.preventDefault();
    setIsPanning(true);
    lastPanPositionRef.current = { x: e.clientX, y: e.clientY };
  };

  const pan = (e) => {
    if (!isPanning) return;
    const dx = e.clientX - lastPanPositionRef.current.x;
    const dy = e.clientY - lastPanPositionRef.current.y;
    setTranslate((prevTranslate) => ({
      x: prevTranslate.x + dx,
      y: prevTranslate.y + dy,
    }));
    lastPanPositionRef.current = { x: e.clientX, y: e.clientY };
  };

  const stopPanning = (e) => {
    if (e.button !== 2) return;
    setIsPanning(false);
  };

  const saveCanvasAsImage = () => {
    const canvas = canvasRef.current;
    const image = canvas.toDataURL('image/png');
    const link = document.createElement('a');
    link.href = image;
    link.download = 'whiteboard.png';
    link.click();
  };

  useImperativeHandle(ref, () => ({
    pause: () => {
      isPausedRef.current = true;
    },
    resume: () => {
      isPausedRef.current = false;
      if (!animationRef.current) {
        animationRef.current = requestAnimationFrame(drawPixelsInBatches);
      }
    },
    seek: (time) => {
      const canvas = canvasRef.current;
      const ctx = canvas.getContext('2d');

      const newIndex = Math.min(Math.floor(time * pixelsPerSecond), coordinates.length);
      indexRef.current = newIndex;
      elapsedTimeRef.current = time * 1000;

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
    clearAll: () => {
      const canvas = canvasRef.current;
      const ctx = canvas.getContext('2d');
      ctx.clearRect(0, 0, canvas.width, canvas.height);
    },

    finishPixels: () => {
      const canvas = canvasRef.current;
      const ctx = canvas.getContext('2d');

      coordinates.forEach(([x, y]) => {
        ctx.fillStyle = 'white';
        ctx.fillRect(x, y, 1, 1);
      });

      if (animationRef.current) {
        cancelAnimationFrame(animationRef.current);
      }

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

      indexRef.current = coordinates.length;
      elapsedTimeRef.current = coordinates.length / pixelsPerSecond * 1000;
    },
  }));

  useEffect(() => {
    const canvas = canvasRef.current;

    indexRef.current = 0;
    elapsedTimeRef.current = 0;
    lastTimestampRef.current = null;

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
    <div
      ref={containerRef}
      onWheel={handleWheel}
      onMouseDown={startPanning}
      onMouseMove={pan}
      onMouseUp={stopPanning}
      onMouseLeave={stopPanning}
      onContextMenu={(e) => e.preventDefault()}
      style={{ overflow: 'hidden', cursor: isPanning ? 'grabbing' : 'grab', width: '100%', height: '100%', display: 'flex', flexDirection: 'column', alignItems: 'center', justifyContent: 'center' }}
    >
      <button onClick={saveCanvasAsImage} style={{ marginBottom: '10px', backgroundColor: '#3498db', color: 'white', borderRadius: '5px', padding: '5px 10px', border: 'none', cursor: 'pointer' }}>Save as PNG</button>
      <canvas
        ref={canvasRef}
        width={3400}
        height={4400}
        style={{
          transform: `scale(${scale}) translate(${translate.x}px, ${translate.y}px)`,
          transformOrigin: '0 0',
          border: '2px solid #444',
          borderRadius: '15px',
          boxShadow: '0 4px 8px rgba(0, 0, 0, 0.3)',
          backgroundColor: '#1c1c1c'
        }}
      />
    </div>
  );
});

export default Whiteboard;