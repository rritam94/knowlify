import React from 'react';

const Slideshow = ({ slides, currentSlide, onSlideChange, setIdx }) => {
  if (!slides || slides.length === 0) {
    return <div>No slides available</div>;
  }

  const nextSlide = () => {
    const newSlide = (currentSlide + 1) % slides.length;
    onSlideChange(newSlide);
    setIdx(0); // Reset idx to 0
  };

  const prevSlide = () => {
    const newSlide = (currentSlide - 1 + slides.length) % slides.length;
    onSlideChange(newSlide);
    setIdx(0); // Reset idx to 0
  };

  return (
    <div className="slideshow-container">
      <div className="slideshow-content">
        <h2>{slides[currentSlide].title}</h2>
        {slides[currentSlide].points && slides[currentSlide].points.length > 0 && (
          <ul>
            {slides[currentSlide].points.map((point, index) => (
              <li key={index} style={{ marginBottom: '10px' }}>{point}</li>
            ))}
          </ul>
        )}
        <button className="prev" onClick={prevSlide} disabled={currentSlide === 0}>
          &lt;
        </button>
        <button className="next" onClick={nextSlide} disabled={currentSlide === slides.length - 1}>
          &gt;
        </button>
        <p>Slide {currentSlide + 1} of {slides.length}</p>
      </div>
    </div>
  );
};

export default Slideshow;