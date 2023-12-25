"use client";

import Logos from "./Logos";
import React, { useState, useRef } from "react";
import SearchCard from "../SearchCard";
import { useResultData } from "@/context/provider";
import Slider from '@mui/material/Slider';
import { blue } from "@mui/material/colors";

const Sidebar = () => {
  const { topK, setTopK, setResultData, query } = useResultData();
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

  return (
    <>
      <aside className="z-40 w-1/4 h-screen transition-transform -translate-x-full sm:translate-x-0 bg-blue-100 mx-2">
        <div className="h-full overflow-y-auto">
          <div className="flex justify-center mb-1">
            <Logos />
          </div>
          <div className="flex flex-col gap-2">
            <div className="flex flex-col gap-1">
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
                sx={{
                  color: blue,
                }}
                max={500}
                min={1}
              />
            </div>
            <SearchCard topk={topK} />
          </div>
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