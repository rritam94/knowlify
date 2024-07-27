import React, { useEffect, useState, useCallback } from 'react';
import _ from 'lodash';
import AudioPlayer from './play';
import Whiteboard from './whiteboard';

const Lecture = ({ actions, currentSlide }) => {
  const [audioBytes, setAudioBytes] = useState(null);
  const [idx, setIdx] = useState(0);
  const [coords, setCoords] = useState([]);
  const [audioKey, setAudioKey] = useState(0);
  const [whiteboardKey, setWhiteboardKey] = useState(0);
  const [isPlaying, setIsPlaying] = useState(false);
  const [isDrawing, setIsDrawing] = useState(false);

  const moveToNextAction = useCallback(() => {
    setIdx(prevIdx => prevIdx + 1);
  }, []);

  const handleAudioEnd = useCallback(() => {
    setIsPlaying(false);
    setAudioBytes(null);
    moveToNextAction();
  }, [moveToNextAction]);

  const handleDrawingEnd = useCallback(() => {
    setIsDrawing(false);
    moveToNextAction();
  }, [moveToNextAction]);

  useEffect(() => {
    setIdx(0);
    setAudioBytes(null);
    setCoords([]);
    setIsPlaying(false);
    setIsDrawing(false);
    setWhiteboardKey(prev => prev + 1);
  }, [currentSlide]);

  useEffect(() => {
    if (isPlaying || isDrawing) return;

    const action = actions[currentSlide];

    if (Array.isArray(action) && idx < action.length) {
      const currentAction = action[idx];
      if (typeof currentAction === 'string') {
        setAudioBytes(atob(currentAction));
        setAudioKey(prevKey => prevKey + 1);
        setIsPlaying(true);
      } else if (typeof currentAction === 'object') {
        if(currentAction.length == 2){
          setCoords(currentAction[0]);
          setIsDrawing(true);
          setAudioBytes(atob(currentAction[1]));
          setAudioKey(prevKey => prevKey + 1);
          setIsPlaying(true);
        }
        else{
          setCoords(currentAction);
          setIsDrawing(true);
        }
        
      }
    } else if (typeof action === 'string' && idx === 0) {
      setAudioBytes(atob(action));
      setAudioKey(prevKey => prevKey + 1);
      setIsPlaying(true);
    }
  }, [currentSlide, idx, actions, isPlaying, isDrawing]);

  return (
    <div>
      {audioBytes && <AudioPlayer key={audioKey} audioBytes={audioBytes} onEnded={handleAudioEnd} />}
      <Whiteboard 
        key={whiteboardKey} 
        coordinates={coords} 
        onEnded={handleDrawingEnd} 
        clearOnUpdate={false} 
      />
    </div>
  );
};

export default Lecture;