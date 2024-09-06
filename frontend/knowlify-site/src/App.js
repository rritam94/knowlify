import React, { useState } from 'react';
import PdfUpload from './components/pdf';
import AudioPlayer from './components/play';
import Slideshow from './components/slideshow';
import Lecture from './components/lecture';
import Question from './components/questions';
import './App.css';

function App() {
  const [actions, setActions] = useState([]);
  const [slides, setSlides] = useState([]);
  const [currentSlide, setCurrentSlide] = useState(0);
  const [idx, setIdx] = useState(0);
  const [currentSlideJson, setCurrentSlideJson] = useState({});
  const [loading, setLoading] = useState(false);

  const onSlideChange = (newSlide) => {
    setCurrentSlide(newSlide);
    console.log('Slide changed to:', newSlide);
  };

  const handleUpdate = (newSlides, newActions) => {
    if (!Array.isArray(newSlides)) {
      console.error('Expected newSlides to be an array, but got:', newSlides);
      return;
    }

    if (!Array.isArray(newActions)) {
      console.error('Expected newActions to be an array, but got:', newActions);
      return;
    }

    setSlides((prevSlides) => [
      ...prevSlides.slice(0, currentSlide + 1),
      ...newSlides,
      ...prevSlides.slice(currentSlide + 1)
    ]);

    setActions((prevActions) => [
      ...prevActions.slice(0, currentSlide + 1),
      ...newActions,
      ...prevActions.slice(currentSlide + 1)
    ]);
  };

  return (
    <div className="App">
      <div className="top-bar">
        <div className="top-bar-section">
          <Slideshow
            slides={slides}
            currentSlide={currentSlide}
            onSlideChange={onSlideChange}
            setIdx={setIdx}
          />
        </div>
        <div className="top-bar-section">
          <div className="upload-container">
            <PdfUpload 
              className="upload-button" 
              setSlides={setSlides}
              setActions={setActions}
              setCurrentSlideJson={setCurrentSlideJson}
              setLoading={setLoading}
            />
            {loading && <div className="loading-icon"></div>}
          </div>
        </div>
        <div className="top-bar-section">
          <Question currentSlideJson={currentSlideJson} onUpdate={handleUpdate} />
        </div>
      </div>

      <div className="whiteboard-area">
        <Lecture actions={actions} currentSlide={currentSlide} idx={idx} setIdx={setIdx} />
      </div>

      <div className="right-side">
        <AudioPlayer currentSlide={currentSlide} />
      </div>
    </div>
  );
}

export default App;