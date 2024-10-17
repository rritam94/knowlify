import React, { useState, useEffect, useRef } from 'react';
import { v4 as uuidv4 } from 'uuid';
import io from 'socket.io-client';

const PdfUpload = ({ className, setSlides, setActions, setCurrentSlideJson }) => {
  const [file, setFile] = useState(null);
  const [uploadStatus, setUploadStatus] = useState('');
  const [uuidStorage, setUUID] = useState('');
  const socketRef = useRef(null);
  const [log, setLog] = useState('');

  useEffect(() => {
    let generatedUUID = uuidv4();
    const modifiedText = generatedUUID.replaceAll('-', "_");
    setUUID(modifiedText);

    socketRef.current = io('wss://knowlify-backend-production.up.railway.app', {
      transports: ['websocket', 'polling'],
      secure: true
    });

    socketRef.current.on('connect', () => {
      socketRef.current.emit('join', modifiedText);
      setupSocketListeners(modifiedText);
    });

    return () => {
      if (socketRef.current) {
        socketRef.current.disconnect();
      }
    };
  }, []);

  const setupSocketListeners = (uuid) => {
    setUploadStatus('title_data' + uuid);
    socketRef.current.on('title_data', (data) => {
      console.log('Title JK: ' + data.title);
      setCurrentSlideJson(data.content);
      setLog("in title");
      setUploadStatus(log);
      setSlides((prevSlides) => {
        if (!Array.isArray(prevSlides)) {
          console.error('Expected prevSlides to be an array, but got:', prevSlides);
          return [];
        }

        const updatedSlides = [...prevSlides];
        updatedSlides.push({
          title: data.title,       
          bulletPoints: []
        });

        return updatedSlides;
      });
      console.log(data);
    });

    socketRef.current.on('bullet_points_data', (data) => {
      setCurrentSlideJson(data.content);
      setLog(log + " and bullet points");
      setUploadStatus(log);
      setSlides((prevSlides) => {
        if (!Array.isArray(prevSlides)) {
          console.error('Expected prevSlides to be an array, but got:', prevSlides);
          return [];
        }

        const updatedSlides = [...prevSlides];
        if (updatedSlides[data.slide_number]) {
          setCurrentSlideJson(data.content)
          updatedSlides[data.slide_number].points = data.bullet_points;
          console.log(updatedSlides[data.slide_number])
        }
        return updatedSlides;
      });
      console.log(data);
    });

    // socketRef.current.on('start_data' + uuid, (data) => {
    //   setCurrentSlideJson(data.content);
    //   setActions((prevActions) => {
    //     const updatedActions = prevActions == null ?  [] : [...prevActions];
    //     let action = [data.start];
    //     updatedActions.push(action);
    //     return updatedActions;
    //   });
    //   console.log(data);
    // });

    // socketRef.current.on('during_writing_data' + uuid, (data) => {
    //   setCurrentSlideJson(data.content);
    //   setActions((prevActions) => {
    //     if (!Array.isArray(prevActions)) {
    //       console.error('Expected prevActions to be an array, but got:', prevActions);
    //       return [];
    //     }

    //     const updatedActions = [...prevActions];
    //     updatedActions[data.slide_number].push([data.coords, data.during_writing]);
    //     return updatedActions;
    //   });
    //   console.log(data);
    // });

    // socketRef.current.on('pause_data' + uuid, (data) => {
    //   setCurrentSlideJson(data.content);
    //   setActions((prevActions) => {
    //     if (!Array.isArray(prevActions)) {
    //       console.error('Expected prevActions to be an array, but got:', prevActions);
    //       return [];
    //     }

    //     const updatedActions = [...prevActions];
    //     updatedActions[data.slide_number].push(data.pause);
    //     return updatedActions;
    //   });
    //   console.log(data);
    // });

    // socketRef.current.on('stop_data' + uuid, (data) => {
    //   setCurrentSlideJson(data.content);
    //   setActions((prevActions) => {
    //     if (!Array.isArray(prevActions)) {
    //       console.error('Expected prevActions to be an array, but got:', prevActions);
    //       return [];
    //     }

    //     const updatedActions = [...prevActions];
    //     updatedActions[data.slide_number].push(data.stop);
    //     return updatedActions;
    //   });
    //   console.log(data);
    // });
  };

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
        } else {
          const errorResponse = await response.json();
          setUploadStatus(`File upload failed: ${errorResponse.error}`);
        }
      } catch (error) {
        setUploadStatus(`Error uploading file: ${error.message}`);
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