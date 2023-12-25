"use client";

import axios from 'axios';
import Logos from "./Logos";
import React, { useState, useRef } from "react";
import SearchCard from "../SearchCard";
import { useResultData } from "@/context/provider";
import { HOST_URL } from "@/constants/api";
import Slider from '@mui/material/Slider';
import { blue } from "@mui/material/colors";
import Reranking from "../Reranking";

const Sidebar = () => {
  const { topK, setTopK, setResultData, query, relevantImages, removeRelevantImage, irrelevantImages, removeIrrelevantImage, sketchData, setRelevantImages, setIrrelevantImages } = useResultData();
  const [isModalOpen, setIsModalOpen] = useState(false);
  const [modalImageSrc, setModalImageSrc] = useState("");

  const modalRef = useRef()

  const handleTopKChange = (e) => {
    const newValue = parseInt(e.target.value, 10);
    if (!isNaN(newValue)) {
      setTopK(newValue);
    }
  };

  const handleImageClick = (imageSrc) => {
    setModalImageSrc(imageSrc);
    setIsModalOpen(true);
  };

  const closeModal = () => {
    setIsModalOpen(false);
  };

  const handleClickOutside = (e) => {
    if (modalRef.current && !modalRef.current.contains(e.target)) {
      closeModal();
    }
  };

  const handleReranking = async () => {
    const requestData = {
      original_query: sketchData || query,
      relevant_images: relevantImages,
      irrelevant_images: irrelevantImages,
      topk: topK
    };

    try {
      const response = await axios.post(`${HOST_URL}rerank_search`, requestData, { headers: { "Content-Type": "application/json" } });
      setResultData(response.data);
    } catch (error) {
      console.error('Error during reranking:', error);
    }
  }

  const isReranking = relevantImages.length === 0 && irrelevantImages.length === 0;

  const handleClear = () => {
    setRelevantImages([]);
    setIrrelevantImages([]);
  }

  return (
    <>
      <aside className="z-40 w-1/3 h-screen transition-transform -translate-x-full sm:translate-x-0 bg-blue-100 mx-2">
        <div className="h-full overflow-y-auto">
          <div className="flex justify-center mt-2">
            <Logos />
          </div>
          <div className="flex flex-col gap-2">
            <div className="flex flex-col gap-1 px-4">
              <div className="flex flex-row gap-2 justify-between items-center">
                <label
                  htmlFor="topk"
                  className="block text-sm font-medium text-gray-900"
                >
                  Top K
                </label>
                <input
                  id="topk"
                  type="number"
                  value={topK}
                  onChange={handleTopKChange}
                  min="1"
                  max="500"
                  className="border rounded-md px-1 py-1 text-gray-900 text-xs"
                />
              </div>
              <Slider
                id="topk"
                value={topK}
                onChange={handleTopKChange}
                max={500}
                min={1}
                sx={{
                  color: blue,
                }}
              />
            </div>
            <SearchCard topk={topK} />
            <div className="flex flex-col gap-2 bg-white p-4 rounded-lg">
              <div className='flex'>
                <button className='text-xs font-medium text-blue-700' onClick={handleClear}>
                  Clear
                </button>
              </div>
              <Reranking
                relevantImages={relevantImages}
                removeRelevantImage={removeRelevantImage}
                irrelevantImages={irrelevantImages}
                removeIrrelevantImage={removeIrrelevantImage}
                handleImageClick={handleImageClick}
                handleClear={handleClear}
              />
              <button className="bg-blue-600 text-white p-3 rounded-full mt-2 hover:bg-blue-700" disabled={isReranking} onClick={handleReranking}>Reranking</button>
            </div>
          </div>
          {/* Add new feature here */}
        </div>
      </aside>
      {isModalOpen && (
        <div className="fixed inset-0 bg-black bg-opacity-50 z-50 flex justify-center items-center" onClick={handleClickOutside}>
          <div className="rounded relative" ref={modalRef}>
            <button onClick={closeModal} className="absolute top-2 right-2 text-xl text-white px-2.5 py-0.5 rounded-full bg-red-500">&times;</button>
            <img src={modalImageSrc} alt="Modal Content" className="max-w-full max-h-full" />
          </div>
        </div>
      )}
    </>
  );
};
export default Sidebar;