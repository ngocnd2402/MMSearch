import React, { useState, useCallback } from "react";
import { useResultData } from "@/context/provider";
import Canvas from "../Canvas";
import { HOST_URL } from "@/constants/api";
import Sketch from "../Sketch";

const TextField = React.lazy(() => import('@mui/material/TextField'));

const SearchCard = ({ topk }) => {
  // State for clicked methods
  const [activeButtons, setActiveButtons] = useState(new Set(["query"])); 

  // State for storing user input with type and value
  const [inputValues, setInputValues] = useState([
    { type: "query", value: "" },
  ]); 

  // State for redo action
  const [redoStack, setRedoStack] = useState([]); 

  // State for handling using sketch
  const [sketchCanvasRef, setSketchCanvasRef] = useState(null);

  // const [object, setObject] = useState([]);

  const { setResultData, canvasData, setCanvasData, setQuery, setSketchData } = useResultData();

  // Make the button activate when clicked
  const handleButtonClick = useCallback((buttonType) => {
    setActiveButtons(prevActiveButtons => {
      const updatedActiveButtons = new Set(prevActiveButtons);
      if (updatedActiveButtons.has(buttonType)) {
        updatedActiveButtons.delete(buttonType);
      } else {
        updatedActiveButtons.add(buttonType);
      }
      return updatedActiveButtons;
    });

    setInputValues(prevInputValues => {
      const typeExists = prevInputValues.some(input => input.type === buttonType);
      if (typeExists) {
        return prevInputValues.filter(input => input.type !== buttonType);
      } else {
        return [...prevInputValues, { type: buttonType, value: "" }];
      }
    });
  }, []);

  // Close an input query
  const handleCloseClick = useCallback((type) => {
    setInputValues(prevInputValues => prevInputValues.filter(input => input.type !== type));
    setActiveButtons(prevActiveButtons => new Set([...prevActiveButtons].filter(activeType => activeType !== type)));
    if (type === "query") {
      setQuery("")
    } else if (type === "object") {
      setCanvasData([])
    } else if (type === "sketch") {
      setSketchData("")
    }
  }, []);

  // Update value when changed an input query 
  const handleInputChange = useCallback((index, e) => {
    setInputValues((prevInputValues) => {
      const newInputValues = [...prevInputValues];
      newInputValues[index].value = e.target.value;

      if (newInputValues[index].type === "query") {
        setQuery(e.target.value);
      }

      return newInputValues;
    });
  }, [inputValues, setQuery]);

  // Undo the action
  const handleUndo = useCallback(() => {
    if (inputValues.length > 1) {
      const removedItem = inputValues[inputValues.length - 1];
      setInputValues(inputValues.slice(0, -1));
      setRedoStack([...redoStack, removedItem]);

      const newActiveButtons = new Set([...activeButtons]);
      newActiveButtons.delete(removedItem.type);
      setActiveButtons(newActiveButtons);
    }
  }, [inputValues, redoStack, activeButtons]);

  // Redo the action
  const handleRedo = useCallback(() => {
    if (redoStack.length > 0) {
      const restoredItem = redoStack[redoStack.length - 1];
      setInputValues([...inputValues, restoredItem]);
      setRedoStack(redoStack.slice(0, -1));

      const newActiveButtons = new Set([...activeButtons, restoredItem.type]);
      setActiveButtons(newActiveButtons);
    }
  }, [inputValues, redoStack, activeButtons]);

  // Reset all input query to the beginning (only use text query)
  const handleReset = (e) => {
    e.preventDefault();
    setInputValues([{ type: "query", value: "" }]);
    setRedoStack([]);
    setActiveButtons(new Set(["query"]));
    setResultData(null)
    setCanvasData([])
  };

  // Logic to fetch result from API
  const fetchResults = async (queryValues) => {
    // Construct the API endpoint based on the type of query
    let apiEndpoint = `${HOST_URL}`;
    let requestBody = null;
    let headers = {};

    // Single search type handling
    if (queryValues.length === 1) {
      const { type, value } = queryValues[0];
      apiEndpoint += `${type}_search`;

      if (type === "object") {
        // For object search, use JSON request body
        requestBody = JSON.stringify({ query_input: value.map(coord => ({ ...coord })), topk });
        headers = { "Content-Type": "application/json" };
      } else {
        // For other types, use FormData
        requestBody = new FormData();
        requestBody.append("query", value);
        requestBody.append("topk", topk);
      }
    } else {
      apiEndpoint += "combine_search";
      requestBody = JSON.stringify({
        query: queryValues.map(q => q.value),
        methods: queryValues.map(q => q.type),
        topk,
      });
      headers = { "Content-Type": "application/json" };
    }

    try {
      const response = await fetch(apiEndpoint, {
        method: "POST",
        body: requestBody,
        headers: headers
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

  // Handle when clicked submit button
  const handleSubmit = async () => {
    let updatedSketchData = null;

    // Export the sketch data and update the sketchData state
    if (showSketchCanvas && sketchCanvasRef && sketchCanvasRef.current) {
      try {
        const imageData = await sketchCanvasRef.current.exportImage("jpeg");
        updatedSketchData = imageData; // Temporarily store the updated sketch data
        console.log(imageData);
      } catch (e) {
        console.error(e);
        return;
      }
    }

    // Update the sketchData state
    if (updatedSketchData) {
      setSketchData(updatedSketchData);
    }

    // Construct the query values for the search
    const queryValues = inputValues.filter(obj => obj.value !== "");

    // Check if 'object' search is active and canvasData is not empty
    if (activeButtons.has("object") && canvasData.length > 0) {
      queryValues.push({ type: "object", value: canvasData });
    }

    // Use the updated sketch data for the search
    if (activeButtons.has("sketch") && updatedSketchData !== null) {
      queryValues.push({ type: "sketch", value: updatedSketchData });
    }

    // Proceed with the search if there are valid query values
    if (queryValues.some(data => data.value !== "")) {
      await fetchResults(queryValues);
    }
  };

  const showCanvas = activeButtons.has("object");
  const showSketchCanvas = activeButtons.has("sketch");

  return (
    <div className="flex flex-col gap-2 bg-white p-4 rounded-lg">
      <div className="flex flex-col gap-2 relative">
        <div className="flex flex-row justify-between text-xs text-blue-600 font-semibold">
          <div className="flex flex-row gap-2">
            <button onClick={handleUndo} className="hover:text-blue-800">
              Undo
            </button>
            <button onClick={handleRedo} className="hover:text-blue-800">
              Redo
            </button>
          </div>
          <button className="cursor-pointer mb-1 hover:text-blue-800" onClick={handleReset}>
            Reset
          </button>
        </div>
        <div className="grid grid-cols-3 gap-3 text-gray-900 mb-2">
          {["query", "ocr", "asr", "object", "sketch"].map((type) => (
            <div
              key={type}
              className={`col-start self-stretch p-2 text-center rounded-md text-xs font-medium cursor-pointer ${inputValues.some((input) => input.type === type)
                ? "bg-blue-600 text-white"
                : "bg-blue-100"
                }`}
              onClick={() => handleButtonClick(type)}
            >
              <button className="uppercase">{type}</button>
            </div>
          ))}
        </div>
        {inputValues.map((input, index) => (input.type !== "object" && input.type !== "sketch" && input.type !== "pose" &&
          <div key={index}>
            <div className="flex relative items-center">
              <TextField
                id={`filled-multiline-flexible-${index}`}
                multiline
                maxRows={4}
                label={input.type}
                variant="outlined"
                value={input.value}
                onChange={(e) => handleInputChange(index, e)}
                placeholder={input.type}
                className="w-full text-xs rounded-md text-gray-900 border border-blue-600 focus:border-2 mt-2"
              />
              <button onClick={() => handleCloseClick(input.type)} className="absolute top-0 right-0 mt-3 mr-2 text-sm">
                &times;
              </button>
            </div>
          </div>
        ))}
        {showCanvas &&
          <div className="relative pt-2">
            <button onClick={() => handleCloseClick("object")} className="absolute top-0 right-0 cursor-pointer">
              &times;
            </button>
            <Canvas />
          </div>
        }
        {showSketchCanvas &&
          <div className="relative pt-5">
            <button onClick={() => handleCloseClick("sketch")} className="absolute top-0 right-0 cursor-pointer">
              &times;
            </button>
            <Sketch setCanvasRef={setSketchCanvasRef} />
          </div>
        }
        <button onClick={handleSubmit} className="bg-blue-600 text-white p-3 rounded-full mt-2 hover:bg-blue-700">Search</button>
      </div>
    </div>
  );
};

export default SearchCard;