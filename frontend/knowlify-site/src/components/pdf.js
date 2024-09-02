import React, { useState, useEffect } from 'react';

const PdfUpload = ({ className, setSlides, setActions, setCurrentSlideJson, setLoading }) => {
  const [file, setFile] = useState(null);
  const [uploadStatus, setUploadStatus] = useState('');
  const [uploadCompleted, setUploadCompleted] = useState(false); // Track upload completion

  const handleFileChange = (event) => {
    setFile(event.target.files[0]);
  };

  const handleUpload = async () => {
    if (file) {
      const formData = new FormData();
      formData.append('pdf', file);

      setLoading(true); // Show loading icon when the upload starts

      try {
        const response = await fetch('http://localhost:5000/generate_slides', {
          method: 'POST',
          body: formData,
        });

        if (response.ok) {
          const jsonResponse = await response.json();
          setUploadStatus('File uploaded successfully');
          setSlides(jsonResponse.slides);
          setActions(jsonResponse.actions);
          setCurrentSlideJson(jsonResponse.json);
          setUploadCompleted(true); // Hide buttons after successful upload
        } else {
          const errorResponse = await response.json();
          setUploadStatus(`File upload failed: ${errorResponse.error}`);
        }
      } catch (error) {
        setUploadStatus(`Error uploading file: ${error.message}`);
      } finally {
        setLoading(false); // Hide loading icon when the upload finishes
      }
    }
  };

  useEffect(() => {
    console.log(uploadStatus);
  }, [uploadStatus]);

  return (
    <div className={className}>
      {!uploadCompleted && ( // Only show buttons if upload is not completed
        <>
          <input className="button" type="file" accept="application/pdf" onChange={handleFileChange} />
          <button className="button" onClick={handleUpload}>
            Upload PDF
          </button>
        </>
      )}
    </div>
  );
};

export default PdfUpload;
