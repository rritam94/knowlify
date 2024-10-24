import React, { useState, useEffect, useRef, useCallback } from 'react';
import { v4 as uuidv4 } from 'uuid';
import io from 'socket.io-client';

const PdfUpload = ({ className, setSlides, setActions, setCurrentSlideJson }) => {
  const [file, setFile] = useState(null);
  const [uploadStatus, setUploadStatus] = useState('');
  const [uuidStorage, setUUID] = useState('');
  const socketRef = useRef(null);
  const [log, setLog] = useState('');

  const setupSocketListeners = useCallback((socket) => {
    setUploadStatus(socket);
    socket.on('title_data', (data) => {
      console.log('Title received:', data.title);
      // setCurrentSlideJson(data.content);
      setLog(prevLog => prevLog + " Title received");
      setUploadStatus(prevStatus => prevStatus + " Title received");
      setSlides(prevSlides => [
        ...prevSlides,
        {
          title: data.title,
          bulletPoints: []
        }
      ]);
    });

    socket.on('bullet_points_data', (data) => {
      setCurrentSlideJson(data.content);
      setLog(prevLog => prevLog + " Bullet points received");
      setUploadStatus(prevStatus => prevStatus + " Bullet points received");
      setSlides(prevSlides => {
        const updatedSlides = [...prevSlides];
        if (updatedSlides[data.slide_number]) {
          updatedSlides[data.slide_number] = {
            ...updatedSlides[data.slide_number],
            points: data.bullet_points
          };
        }
        return updatedSlides;
      });
    });

    // Add other event listeners here...
  }, [setCurrentSlideJson, setSlides]);

  useEffect(() => {
    const generatedUUID = uuidv4().replaceAll('-', "_");
    setUUID(generatedUUID);

    const socket = io('https://knowlify-backend-production.up.railway.app', {
      transports: ['websocket', 'polling'],
      secure: true
    });

    socket.on('connect', () => {
      console.log('Connected to server');
      socket.emit('join', generatedUUID);
      setupSocketListeners(socket);
    });

    socket.on('connect_error', (error) => {
      console.error('Connection error:', error);
    });

    socketRef.current = socket;

    return () => {
      if (socket) {
        socket.disconnect();
      }
    };
  }, [setupSocketListeners]);

  const handleFileChange = (event) => {
    setFile(event.target.files[0]);
  };

  const handleUpload = async () => {
    if (file) {
      const formData = new FormData();
      formData.append('pdf', file);
      formData.append('uuid', uuidStorage);

      try {
        const response = await fetch('https://knowlify-backend-production.up.railway.app/generate_slides', {
          method: 'POST',
          body: formData,
        });

        if (response.ok) {
          setUploadStatus('File upload Successful');
        } 
        
        else {
          const errorResponse = await response.json();
          setUploadStatus(`File upload failed: ${errorResponse.error}`);
        }
      } catch (error) {
        setUploadStatus(`Kill me`);
      }
    }
  };
  
  return (
    <div className={className}>
      <input className="button" type="file" accept="application/pdf" onChange={handleFileChange} />
      <button className="button" onClick={handleUpload}>Upload PDF</button>
      {uploadStatus && (
        <div>
          <h2>Upload Status:</h2>
          <p>{uploadStatus}</p>
        </div>
      )}
    </div>
  );
};

export default PdfUpload;