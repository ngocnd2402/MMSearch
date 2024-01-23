import React, { useState, useEffect, useCallback, useRef } from 'react';
import { useResultData } from '@/context/provider';
import { HOST_URL } from '@/constants/api';
import { fetchCsvData } from '@/utils/fetchCsvData';
import Video from './Video';
import { ArrowBack, ArrowForward, Plus, Minus, PlayCircle, Popout } from './Icons';

const Gallery = () => {
  const {
    resultData, setResultData, topK,
    relevantImages, setRelevantImages, addRelevantImage,
    irrelevantImages, setIrrelevantImages, addIrrelevantImage
  } = useResultData();
  const [clickedFrame, setClickedFrame] = useState(null);
  const [nearbyFrames, setNearbyFrames] = useState([]);
  const [videoTime, setVideoTime] = useState(0);
  const [showVideo, setShowVideo] = useState(false);
  const [isModalOpen, setIsModalOpen] = useState(false);
  const videoModalRef = useRef(null);
  const modalRef = useRef(null);

  // store image name when clicked on an image
  useEffect(() => {
    if (resultData && resultData.length > 0) {
      handleImageClick(resultData[0].frame);
    }
  }, [resultData]);

  // get frame index 
  const getFrameIndex = useCallback((frame) => parseInt(frame.split('/')[2].split('.')[0], 10), []);

  // show information like nearby frames, image's name,... when clicked on an image
  const handleImageClick = useCallback(async (frame) => {
    try {
      setClickedFrame(frame);
      const frameParts = frame.split('/');
      
      const csvUrl = `${HOST_URL}mapframe/${frameParts[1]}.csv`;
      const csvData = await fetchCsvData(csvUrl);
      // setAllFrames(csvData.row[3]);
      const frameIdx = getFrameIndex(frame);
      const n = csvData.findIndex(row => parseInt(row[3], 10) === frameIdx);
      if (n !== -1) {
        const nValue = parseInt(csvData[n][0], 10);
        displayNearbyFrames(nValue, csvData);
        const clickedFrameData = csvData[n];
        if (clickedFrameData) {
          setVideoTime(parseFloat(clickedFrameData[1]));
        }
      }
    } catch (err) {
      console.error('Failed to handle image click:', err);
    }
  }, [setClickedFrame, setVideoTime, setNearbyFrames]);

  // display 6 nearby frames of a chosen image (3 previous, 3 next)
  const displayNearbyFrames = useCallback((nValue, frames) => {
    let display = [];
    const range = 3;
    const totalFrames = frames.length;
    const idx = frames.findIndex(row => parseInt(row[0], 10) === nValue);
    if (idx === -1) {
      return [];
    }
    for (let i = -range; i <= range; i++) {
      let targetN = ((parseInt(frames[idx][0], 10) + i + totalFrames) % totalFrames) || totalFrames;
      const frameRow = frames.find(row => parseInt(row[0], 10) === targetN);
      if (frameRow) {
        display.push(frameRow);
      }
    }
    setNearbyFrames(display.map(row => ({
      frameIdx: row[3],
      ptsTime: row[1],
    })));
  }, [clickedFrame, nearbyFrames])

  // find all the nearby frames of a clicked image
  const findNearbyFrame = useCallback((offset) => {
    const currentIdx = getFrameIndex(clickedFrame);
    const totalFrames = nearbyFrames.length;
    const currentNearbyIdx = nearbyFrames.findIndex(item => parseInt(item.frameIdx, 10) === currentIdx);
    if (currentNearbyIdx !== -1) {
      const newNearbyIdx = (currentNearbyIdx + offset + totalFrames) % totalFrames;
      const newFrame = nearbyFrames[newNearbyIdx];
      const newFrameSrc = `${clickedFrame.split('/')[0]}/${clickedFrame.split('/')[1]}/${newFrame.frameIdx.padStart(7, '0')}.jpg`;
      return newFrameSrc;
    }
    return null;
  }, [clickedFrame, nearbyFrames]);

  // show previous nearby frame when clicked previous
  const handlePrev = useCallback(() => {
    const newFrameSrc = findNearbyFrame(-1);
    if (newFrameSrc) handleImageClick(newFrameSrc);
  }, [findNearbyFrame, handleImageClick]);

  // show next nearby frame when clicked next
  const handleNext = useCallback(() => {
    const newFrameSrc = findNearbyFrame(1);
    if (newFrameSrc) handleImageClick(newFrameSrc);
  }, [findNearbyFrame, handleImageClick]);


  // check if image added to not double it
  const isImageAdded = useCallback((frame) => {
    return relevantImages.includes(frame) || irrelevantImages.includes(frame);
  }, [relevantImages, irrelevantImages]);


  // add irrelevant image
  const handleAddRelevantImage = (frame) => {
    if (!isImageAdded(frame)) {
      addRelevantImage(frame);
    } else {
      setRelevantImages((prev) => prev.filter((img) => img !== frame));
    }
  };

  // add irrelevant image
  const handleAddIrrelevantImage = (frame) => {
    if (!isImageAdded(frame)) {
      addIrrelevantImage(frame);
    } else {
      setIrrelevantImages((prev) => prev.filter((img) => img !== frame));
    }
  };

  // useEffect(() => {
  //   const newImages = checkedImages.filter(img => !prevCheckedRef.current.includes(img));
  //   const removedImages = prevCheckedRef.current.filter(img => !checkedImages.includes(img));

  //   newImages.forEach(addCheckedImage);
  //   removedImages.forEach(removeCheckedImage);

  //   // Update the ref to the current state
  //   prevCheckedRef.current = checkedImages;
  // }, [checkedImages, addCheckedImage, removeCheckedImage]);

  // handle right click to search similar image
  const handleImageContextMenu = async (e, imagePath) => {
    e.preventDefault();
    const requestBody = new FormData();
    requestBody.append("image_path", imagePath);
    requestBody.append("topk", topK);
    try {
      const response = await fetch(`${HOST_URL}image_search`,{
        method: "POST",
        body: requestBody,
      });
      if (!response.ok) {
        throw new Error("Failed to fetch results from the API.");
      }
      const resultData = await response.json();
      setResultData(resultData);
    } catch (error) {
      console.error("Error fetching data:", error);
    }
  };

  // Show video modal when clicked play video
  const handlePlayVideo = () => {
    setShowVideo(true);
  };

  // Close video modal when clicked play video
  const handleCloseVideo = () => {
    setShowVideo(false);
  };

  const handleClickOutside = useCallback(event => {
    if (!videoModalRef.current?.contains(event.target)) {
      setShowVideo(false);
    }
    if (!modalRef.current?.contains(event.target)) {
      setIsModalOpen(false);
    }
  }, []);

  // Close when clicked outside video modal
  useEffect(() => {
    document.addEventListener("mousedown", handleClickOutside);
    return () => document.removeEventListener("mousedown", handleClickOutside);
  }, [handleClickOutside]);

  // Function to submit an answer
  const submitAnswer = async (imagePath) => {
    let item = imagePath.split("/")[1];
    let frame = parseInt(imagePath.split("/")[2], 10);
    let session = "node01uyvv5h7d6xvv15o628610ok3w73";
    let url = `https://eventretrieval.one/api/v1/submit?item=${item}&frame=${frame}&session=${session}`;
    try {
      let response = await fetch(url, { method: "GET", headers: { Authorization: `Bearer ${session}` } });
      if (response.ok) {
        showNoti("Success! Result submitted.", true);
        // Log the response data
        const data = await response.json();
      } else {
        showNoti("Error submitting the result.", false);
        // Log the error response data
        const errorData = await response.json();
        console.log(errorData)
      }
    } catch (error) {
      console.error("An error occurred:", error);
    }
  };

  // Show result after submitting
  // const showNoti = (message, isSuccess) => {
  //   let notification = document.getElementById("Noti");
  //   notification.textContent = message;
  //   notification.style.display = "block";
  //   notification.style.backgroundColor = isSuccess ? "#4CAF50" : "#CE2029";
  //   setTimeout(() => {
  //     notification.style.display = "none";
  //   }, 1000);
  // };


  //  Pop out a clicked image
  const handleOpenModal = () => {
    setIsModalOpen(true);
  };

  // Close image modal
  const closeModal = () => {
    setIsModalOpen(false);
  };

  return (
    <div className='w-2/3 flex flex-col h-screen justify-between bg-blue-100'>
      <div className="grid grid-cols-2 overflow-y-auto flex-grow-0" style={{ maxHeight: `${Math.min(100 * 7 / 8, 100)}vh` }}>
        {resultData && resultData.map((item, index) => (
          <div key={index} className="relative">
            <img
              src={`${HOST_URL}frame/${item.frame}`}
              alt={`Image ${index}`}
              className={`w-full object-cover cursor-pointer box-border ${clickedFrame === item.frame ? 'outline outline-[12px] -outline-offset-[12px] outline-red-600' : ''}`}
              onClick={() => handleImageClick(item.frame)}
              onContextMenu={(event) => handleImageContextMenu(event, item.frame)}
            />
            <button
              className={`absolute top-1 right-1 cursor-pointer rounded-sm ${relevantImages.includes(item.frame) ? 'bg-green-500 text-white border border-green-500' : 'text-green-500 border border-green-500 bg-white hover:bg-green-500 hover:text-white'}`}
              onClick={() => handleAddRelevantImage(item.frame)}
            >
              <Plus />
            </button>
            <button
              className={`absolute top-1 left-1 cursor-pointer rounded-sm ${irrelevantImages.includes(item.frame) ? 'bg-red-500 text-white border border-red-500' : 'text-red-500 border border-red-500 bg-white hover:bg-red-500 hover:text-white'}`}
              onClick={() => handleAddIrrelevantImage(item.frame)}
            >
              <Minus />
            </button>
            <button className='absolute bottom-1 right-1 text-[8px] text-white bg-blue-600 rounded-sm p-0.5 hover:bg-blue-700' onClick={submitAnswer}>
              Submit
            </button>
          </div>
        ))}
      </div>
      {clickedFrame && (
        <>
          <div className='flex flex-col bg-white rounded-t-lg rounded-r-lg'>
            <div className="flex justify-between p-2 items-center">
              <div className='flex flex-row gap-2 items-center'>
                <p className='text-base'>{clickedFrame.split('/')[1]}, {getFrameIndex(clickedFrame)}</p>
                <button onClick={handleOpenModal}>
                  <Popout className={`cursor-pointer rounded-sm text-black text-lg`} />
                </button>
              </div>
              <button
                onClick={handlePlayVideo}
                className="p-2 w-fit bg-blue-600 text-white rounded-full cursor-pointer hover:bg-blue-700 transition duration-300"
              >
                <PlayCircle />
              </button>
              <div className='flex gap-4'>
                <button
                  onClick={handlePrev}
                  className="text-blue-600 hover:text-blue-700 cursor-pointer font-medium"
                >
                  <ArrowBack />
                </button>
                <button
                  onClick={handleNext}
                  className="text-blue-600 hover:text-blue-700 cursor-pointer font-medium"
                >
                  <ArrowForward />
                </button>
              </div>
            </div>
            <div className="grid grid-cols-7 p-4 bg-gray-900">
              {nearbyFrames.map((item, index) => {
                const imgSrc = `${clickedFrame.split('/')[0]}/${clickedFrame.split('/')[1]}/${(item.frameIdx).padStart(7, '0')}.jpg`;
                return (
                  <div key={index} className="relative">
                    <img
                      src={`${HOST_URL}frame/${imgSrc}`}
                      alt={`Nearby Frame ${index}`}
                      className={`w-full object-cover cursor-pointer box-border ${getFrameIndex(clickedFrame) == item.frameIdx ? 'outline outline-4 -outline-offset-4 outline-blue-600' : ''}`}
                      onClick={() => handleImageClick(imgSrc)}
                    />
                  </div>
                );
              })}
            </div>
          </div>
          {showVideo && (
            <div className="fixed inset-0 bg-black bg-opacity-50 z-50 flex justify-center items-center">
              <div ref={videoModalRef} className="rounded relative">
                <button onClick={handleCloseVideo} className="absolute top-2 right-2 text-xl text-white px-2.5 py-0.5 rounded-full bg-red-500">&times;</button>
                <Video path={clickedFrame.split('/')[1]} videoTime={videoTime} />
              </div>
            </div>
          )}
          {isModalOpen && (
            <div className="fixed inset-0 bg-black bg-opacity-50 z-50 flex justify-center items-center">
              <div className="rounded relative" ref={modalRef}>
                <button onClick={closeModal} className="absolute top-2 right-2 text-xl text-white px-2.5 py-0.5 rounded-full bg-red-500">&times;</button>
                <img src={`${HOST_URL}frame/${clickedFrame}`} alt="Modal Content" className="max-w-full max-h-full" />
              </div>
            </div>
          )}
        </>
      )}
    </div>
  )
};

export default Gallery;