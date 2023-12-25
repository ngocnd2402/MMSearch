import React, { createContext, useState, useContext } from 'react';

const ResultDataContext = createContext();

export const useResultData = () => useContext(ResultDataContext);

export const ResultDataProvider = ({ children }) => {
  const [resultData, setResultData] = useState([]);
  const [relevantImages, setRelevantImages] = useState([]);
  const [irrelevantImages, setIrrelevantImages] = useState([]);
  const [canvasData, setCanvasData] = useState([]);
  const [query, setQuery] = useState(null);

  const addRelevantImage = (image) => {
    setRelevantImages(prev => [...prev, image]);
  };

  const removeRelevantImage = (image) => {
    setRelevantImages(prev => prev.filter(img => img !== image));
  };

  const addIrrelevantImage = (image) => {
    setIrrelevantImages(prev => [...prev, image]);
  };

  const removeIrrelevantImage = (image) => {
    setIrrelevantImages(prev => prev.filter(img => img !== image))
  }

  return (
    <ResultDataContext.Provider value={{ resultData, setResultData, query, setQuery, relevantImages, setRelevantImages, addRelevantImage, removeRelevantImage, irrelevantImages, setIrrelevantImages, addIrrelevantImage, removeIrrelevantImage, canvasData, updateCanvasData }}>
      {children}
    </ResultDataContext.Provider>
  );
};