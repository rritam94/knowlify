import React, { useEffect, useState, useCallback, useRef } from 'react';
import AudioPlayer from './play';
import Whiteboard from './whiteboard';

const Lecture = ({ actions = [], currentSlide = 0, idx, setIdx }) => {
  const [audioBytes, setAudioBytes] = useState(null);
  const [coords, setCoords] = useState([]);
  const [audioKey, setAudioKey] = useState(0);
  const [whiteboardKey, setWhiteboardKey] = useState(0);
  const [isPaused, setIsPaused] = useState(false);
  const [currentTime, setCurrentTime] = useState(0);
  const [duration, setDuration] = useState(0);
  const [audioFinished, setAudioFinished] = useState(false);
  const [whiteboardFinished, setWhiteboardFinished] = useState(false);
  const [isSeeking, setIsSeeking] = useState(false);
  const [isAudioEnded, setIsAudioEnded] = useState(false);
  const audioPlayerRef = useRef(null);
  const whiteboardRef = useRef(null);
  const actionRef = useRef(null);

  const handleAudioEnd = useCallback(() => {
    setAudioFinished(true);
    setIsAudioEnded(true);
  }, []);

  const handleDrawingEnd = useCallback(() => {
    setWhiteboardFinished(true);
  }, []);

  const handlePauseResume = () => {
    setIsPaused(prevPaused => !prevPaused);
    if (whiteboardRef.current) {
      if (isPaused) {
        whiteboardRef.current.resume();
        if (audioPlayerRef.current && !isAudioEnded) {
          audioPlayerRef.current.resume();
        }
      } else {
        whiteboardRef.current.pause();
        if (audioPlayerRef.current && !isAudioEnded) {
          audioPlayerRef.current.pause();
        }
      }
    }
  };

  const handleSeek = (time) => {
    if (isNaN(time)) return; // Ensure time is a valid number

    setIsSeeking(true);
    setCurrentTime(time);
    setIsAudioEnded(false);

    if (audioPlayerRef.current) {
      audioPlayerRef.current.seek(time);
      if (!isPaused) {
        audioPlayerRef.current.resume();
      }
    }

    if (whiteboardRef.current) {
      whiteboardRef.current.seek(time);
    }
  };

  const resetAction = useCallback(() => {
    if (audioPlayerRef.current) {
      audioPlayerRef.current.stop();
    }
    
    setAudioBytes(null);
    setCoords([]);
    setAudioKey(prev => prev + 1);
    setIsPaused(false);
    actionRef.current = null;
    setCurrentTime(0);
    setDuration(0);
    setAudioFinished(false);
    setWhiteboardFinished(false);
    setIsAudioEnded(false);
  }, []);

  const handleNextAction = useCallback(() => {
    if (actions[currentSlide] && idx < actions[currentSlide].length - 1) {
      whiteboardRef.current.finishPixels();
      setIdx(prevIdx => prevIdx + 1);
      resetAction();
    }
  }, [actions, currentSlide, idx, setIdx, resetAction]);

  const handlePreviousAction = useCallback(() => {
    if (idx > 0) {
      whiteboardRef.current.removePixels();
      setIdx(prevIdx => prevIdx - 1);
      resetAction();
    }
  }, [idx, setIdx, resetAction]);

  useEffect(() => {
    if (isSeeking) {
      setIsPaused(false);
      setIsSeeking(false);
    }
  }, [isSeeking]);

  useEffect(() => {
    if (whiteboardRef.current) {
      whiteboardRef.current.clearAll();
    }
    resetAction();
    setIdx(0);
  }, [currentSlide, resetAction, setIdx]);

  useEffect(() => {
    if (isPaused || actionRef.current) return;

    const action = actions[currentSlide];
    
    if (Array.isArray(action) && idx < action.length) {
      const currentAction = action[idx];
      actionRef.current = currentAction;

      if (typeof currentAction === 'string') {
        setAudioBytes(atob(currentAction));
        setWhiteboardFinished(true); 
      } 
      
      else if (Array.isArray(currentAction)) {

        if (currentAction.length === 2) {
          setCoords(currentAction[0]);
          setAudioBytes(atob(currentAction[1]));
        } 
        
        else {
          setAudioFinished(true); 
        }
      }
    } 
    
    else if (typeof action === 'string') {
      actionRef.current = action;
      setAudioBytes(atob(action));
      setWhiteboardFinished(true); 
    }
  }, [currentSlide, idx, actions, isPaused]);

  useEffect(() => {
    const interval = setInterval(() => {
      if (!isPaused) {
        let audioDuration = 0;
        let whiteboardDuration = 0;

        if (audioPlayerRef.current) {
          audioDuration = audioPlayerRef.current.getDuration();
          audioDuration = isNaN(audioDuration) ? 0 : audioDuration; // Ensure valid number
        }

        if (whiteboardRef.current) {
          whiteboardDuration = whiteboardRef.current.getDuration();
          whiteboardDuration = isNaN(whiteboardDuration) ? 0 : whiteboardDuration; // Ensure valid number
        }

        const maxDuration = Math.max(audioDuration, whiteboardDuration);
        setDuration(maxDuration);

        setCurrentTime(prevTime => {
          const newTime = Math.min(prevTime + 0.1, maxDuration);
          return isNaN(newTime) ? 0 : newTime; // Ensure newTime is not NaN
        });
      }
    }, 100);

    return () => clearInterval(interval);
  }, [isPaused]);

  useEffect(() => {
    if (audioFinished && whiteboardFinished) {
      actionRef.current = null;
      setIdx(prevIdx => prevIdx + 1);
      resetAction();
    }
  }, [audioFinished, whiteboardFinished, setIdx, resetAction]);

  return (
    <div>
      {/* Top bar with control buttons and seek bar */}
      <div className="top-bar">
        <button className="left-arr" onClick={handlePreviousAction} disabled={idx === 0}>
          &larr; Previous
        </button>
        <button className="pause" onClick={handlePauseResume}>
          {isPaused ? '| |' : '>'}
        </button>
        <input
          type="range"
          min={0}
          max={duration}
          value={currentTime}
          step={0.001}
          onChange={(e) => handleSeek(parseFloat(e.target.value))}
          className="seek-bar"
        />
        <div className="timer">{`${currentTime.toFixed(1)}/${duration.toFixed(1)} seconds`}</div>
        <button className="right-arr" onClick={handleNextAction} disabled={actions[currentSlide] && idx >= actions[currentSlide].length - 1}>
          Next &rarr;
        </button>
      </div>

      {audioBytes && (
        <AudioPlayer
          key={audioKey}
          audioBytes={audioBytes}
          onEnded={handleAudioEnd}
          ref={audioPlayerRef}
          isPaused={isPaused}
          isAudioEnded={isAudioEnded}
          currentTime={currentTime}
        />
      )}
      <Whiteboard 
        key={whiteboardKey} 
        coordinates={coords} 
        onEnded={handleDrawingEnd} 
        ref={whiteboardRef}
      />
      <div className="pause-container">
        <button className="pause" onClick={handlePauseResume}>
          {isPaused ? '| |' : '>'}
        </button>
      </div>


      <div style={{ marginTop: '10px' }}>
        <input
          type="range"
          min={0}
          max={duration}
          value={currentTime}
          step={0.001}
          onChange={(e) => handleSeek(parseFloat(e.target.value))}
          style={{ width: '100%' }}
        />
        <div className ="timer">{`${currentTime.toFixed(1)}/${duration.toFixed(1)} seconds`}</div>
      </div>

      <div style={{ marginTop: '10px' }}>
        <button className = "left-arr" onClick={handlePreviousAction} disabled={idx === 0}>
          &larr; Previous
        </button>
        <button className = "right-arr" onClick={handleNextAction} disabled={actions[currentSlide] && idx >= actions[currentSlide].length - 1}>
          Next &rarr;
        </button>
      </div>
    </div>
  );
};

export default Lecture;