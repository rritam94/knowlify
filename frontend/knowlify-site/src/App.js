import React, { useState, useEffect } from 'react';
import PdfUpload from './components/pdf';
import AudioPlayer from './components/play';
import Slideshow from './components/slideshow';
import Lecture from './components/lecture';
import './App.css'

function App() {
  const [actions, setActions] = useState([]);
  const [slides, setSlides] = useState([]);
  const [currentSlide, setCurrentSlide] = useState(0);

  const onSlideChange = (newSlide) => {
    setCurrentSlide(newSlide);
    console.log('Slide changed to:', newSlide);
  };

  return (
    <div className="App">
      <div className="left-side">
        <Slideshow
          slides={slides}
          currentSlide={currentSlide}
          onSlideChange={onSlideChange} 
        />
        <PdfUpload className="upload-button" setSlides={setSlides} setActions={setActions} />
      </div>
      <div className="right-side">
        <Lecture actions={actions} currentSlide={currentSlide} />
      </div>
    </div>
  );
}

export default App;