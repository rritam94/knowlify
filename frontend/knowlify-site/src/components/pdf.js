import React, { useState, useEffect, useRef } from 'react';
import io from 'socket.io-client';

const PdfUpload = ({ className, setSlides, setActions, setCurrentSlide, currentSlide }) => {
  const [file, setFile] = useState(null);
  const [uploadStatus, setUploadStatus] = useState('');
  const socketRef = useRef(null); 

  useEffect(() => {
    socketRef.current = io('http://localhost:5000');

    socketRef.current.on('title_data', (data) => {
      setSlides((prevSlides) => {
        if (!Array.isArray(prevSlides)) {
          console.error('Expected prevSlides to be an array, but got:', prevSlides);
          return [];
        }

        const updatedSlides = [...prevSlides];
        updatedSlides.push(
          {
            title: data.title,       
            bulletPoints: []
          }
        )

        return updatedSlides;
      });
      console.log(data);
    });

    socketRef.current.on('bullet_points_data', (data) => {
      setSlides((prevSlides) => {
        if (!Array.isArray(prevSlides)) {
          console.error('Expected prevSlides to be an array, but got:', prevSlides);
          return [];
        }

        const updatedSlides = [...prevSlides];
        if (updatedSlides[data.slide_number]) {
          updatedSlides[data.slide_number].points = data.bullet_points;
          console.log(updatedSlides[data.slide_number])
        }
        return updatedSlides;
      });
      console.log(data);
    });

    socketRef.current.on('start_data', (data) => {
      setActions((prevActions) => {
        const updatedActions = prevActions == null ?  [] : [...prevActions];
        let action = [data.start];
        updatedActions.push(action);
        return updatedActions;
      });
      console.log(data);
    });


    socketRef.current.on('during_writing_data', (data) => {
      setActions((prevActions) => {
        if (!Array.isArray(prevActions)) {
          console.error('Expected prevActions to be an array, but got:', prevActions);
          return [];
        }

        const updatedActions = [...prevActions];
        updatedActions[data.slide_number].push([data.coords, data.during_writing]);
        return updatedActions;
      });
      console.log(data);
    });

    socketRef.current.on('pause_data', (data) => {
      setActions((prevActions) => {
        if (!Array.isArray(prevActions)) {
          console.error('Expected prevActions to be an array, but got:', prevActions);
          return [];
        }

        const updatedActions = [...prevActions];
        updatedActions[data.slide_number].push(data.pause);
        return updatedActions;
      });
      console.log(data);
    });

    socketRef.current.on('stop_data', (data) => {
      setActions((prevActions) => {
        if (!Array.isArray(prevActions)) {
          console.error('Expected prevActions to be an array, but got:', prevActions);
          return [];
        }

        const updatedActions = [...prevActions];
        updatedActions[data.slide_number].push(data.stop);
        return updatedActions;
      });
      console.log(data);
    });

    return () => {
      socketRef.current.disconnect();
    };
  }, []); 

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
          setUploadStatus('File upload Successful');
        } else {
          const errorResponse = await response.json();
          setUploadStatus(`File upload failed: ${errorResponse.error}`);
        }
      } catch (error) {
        setUploadStatus(`Error uploading file: ${error.message}`);
      }
    }
  };

  useEffect(() => {
    console.log(uploadStatus);
  }, [uploadStatus]);

  return (
    <div className={className}>
      <input className="button" type="file" accept="application/pdf" onChange={handleFileChange} />
      <button className="button" onClick={handleUpload}>Upload PDF</button>
    </div>
  );
};

export default PdfUpload;
