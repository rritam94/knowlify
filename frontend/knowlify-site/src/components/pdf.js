import React, { useState, useEffect } from 'react';

const PdfUpload = ({ className, setSlides, setActions, setCurrentSlideJson }) => {
  const [file, setFile] = useState(null);
  const [uploadStatus, setUploadStatus] = useState('');

  const handleFileChange = (event) => {
    setFile(event.target.files[0]);
  };

  const handleUpload = async () => {
    if (file) {
      const formData = new FormData();
      formData.append('pdf', file);

      try {
        const response = await fetch('http://localhost:5000/generate_slides', {
          method: 'POST',
          body: formData,
        });

        if (response.ok) {
          const jsonResponse = await response.json();
          // console.log(jsonResponse);
          setUploadStatus('File uploaded successfully');
          setSlides(jsonResponse.slides);
          setActions(jsonResponse.actions)
          setCurrentSlideJson(jsonResponse.json);
        } 
        
        else {
          const errorResponse = await response.json();
          setUploadStatus(`File upload failed: ${errorResponse.error}`);
        }
      } 
      
      catch (error) {
        setUploadStatus(`Error uploading file: ${error.message}`);
      }
    }
  };

  useEffect(() => {
    console.log(uploadStatus);
  }, [uploadStatus]);

  return (
    <div className={className}>
      <input className = "button" type="file" accept="application/pdf" onChange={handleFileChange} />
      <button className = "button" onClick={handleUpload}>Upload PDF</button>
    </div>
  );
};

export default PdfUpload;
