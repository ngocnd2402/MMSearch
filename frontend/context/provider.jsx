import React, { createContext, useState, useContext } from 'react';

const ResultDataContext = createContext();

export const useResultData = () => useContext(ResultDataContext);

export const ResultDataProvider = ({ children }) => {
  const [resultData, setResultData] = useState([]);
  const [query, setQuery] = useState(null);

  return (
    <ResultDataContext.Provider value={{ resultData, setResultData, query, setQuery }}>
      {children}
    </ResultDataContext.Provider>
  );
};