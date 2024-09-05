import React, { useState } from 'react';
import PdfUpload from './components/pdf';
import AudioPlayer from './components/play';
import Slideshow from './components/slideshow';
import Lecture from './components/lecture';
import Question from './components/questions';
import './App.css'

function App() {
  const [actions, setActions] = useState([]);
  const [slides, setSlides] = useState([]);
  const [currentSlide, setCurrentSlide] = useState(0);
  const [idx, setIdx] = useState(0);
  const [currentSlideJson, setCurrentSlideJson] = useState({});

  const onSlideChange = (newSlide) => {
    setCurrentSlide(newSlide);
    console.log('Slide changed to:', newSlide);
  };

  const handleUpdate = (newSlides, newActions) => {
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
      <div className="left-side">
        <Slideshow
          slides={slides}
          currentSlide={currentSlide}
          onSlideChange={onSlideChange}
          setIdx={setIdx} 
        />

        <PdfUpload 
          className="upload-button" 
          setSlides={(newSlides) => {
            setSlides((prevSlides) => [
              ...prevSlides.slice(0, currentSlide),
              ...newSlides
            ]);
          }}
          setActions={(newActions) => {
            setActions((prevActions) => [
              ...prevActions.slice(0, currentSlide),
              ...newActions
            ]);
          }}
          setCurrentSlideJson={setCurrentSlideJson}
        />
        <Question currentSlideJson={currentSlideJson} onUpdate={handleUpdate} />
      </div>
      <div className="right-side">
        <Lecture actions={actions} currentSlide={currentSlide} idx={idx} setIdx={setIdx} />
      </div>
    </div>
  );
}

export default App;
