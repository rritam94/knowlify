import React, { useState } from 'react';
import SpeechRecognition, { useSpeechRecognition } from 'react-speech-recognition';

const Question = ({ onUpdate, currentSlideJson }) => {
  const [isListening, setIsListening] = useState(false);
  const [backendResponse, setBackendResponse] = useState(null);

  const {
    transcript,
    resetTranscript,
    browserSupportsSpeechRecognition
  } = useSpeechRecognition();

  if (!browserSupportsSpeechRecognition) {
    return <span>Browser doesn't support speech recognition.</span>;
  }

  const handleListen = () => {
    setIsListening(true);
    SpeechRecognition.startListening({ continuous: true });
  };

  const handleStopListening = async () => {
    setIsListening(false);
    SpeechRecognition.stopListening();

    try {
      const response = await fetch('http://localhost:5000/answer_question', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ 
            'slide': JSON.stringify(currentSlideJson), 
            transcript 
        }),
      });

      if (!response.ok) {
        throw new Error('Network response was not ok');
      }

      const data = await response.json();
      setBackendResponse(data);
      
      onUpdate(data.slides, data.actions);
    } catch (error) {
      console.error('Error:', error);
    }

    resetTranscript();
  };

  return (
    <div>
      <h2>Ask a question</h2>
      <button onClick={isListening ? handleStopListening : handleListen}>
        {isListening ? 'Stop Listening' : 'Start Listening'}
      </button>
      
    </div>
  );
};

export default Question;