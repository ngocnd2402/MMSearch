import React, { useState, useCallback, useRef } from "react";
import { useResultData } from "@/context/provider";
import { HOST_URL } from "@/constants/api";
import Canvas from "../Canvas";
import Sketch from "../Sketch";
import Pose from "../Pose";

const TextField = React.lazy(() => import('@mui/material/TextField'));

const SearchCard = ({ topk }) => {
  // State for clicked methods
  const [activeButtons, setActiveButtons] = useState(new Set(["semantic"]));

  // State for storing user input with type and value
  const [inputValues, setInputValues] = useState([
    { type: "semantic", value: null },
  ]);

  // State for redo action
  const [redoStack, setRedoStack] = useState([]);

  // State for handling using sketch
  const [sketchCanvasRef, setSketchCanvasRef] = useState(null);

  // Ref for the file input
  const fileInputRef = useRef();

  const { setResultData, canvasData, setCanvasData, setQuery, sketchData, setSketchData, poseData, setPoseData } = useResultData();

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
    if (type === "semantic") {
      setQuery("")
    } else if (type === "object") {
      setCanvasData([])
    } else if (type === "sketch") {
      setSketchData("");
    } else if (type === "pose") {
      setPoseData([])
    }
  }, []);

  // Update value when changed an input query 
  const handleInputChange = useCallback((index, e) => {
    setInputValues((prevInputValues) => {
      const newInputValues = [...prevInputValues];
      newInputValues[index].value = e.target.value;

      if (newInputValues[index].type === "semantic") {
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
    setInputValues([{ type: "semantic", value: "" }]);
    setRedoStack([]);
    setActiveButtons(new Set(["semantic"]));
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

      if (type === "object" || type === "pose") {
        requestBody = JSON.stringify({ query_input: type === "pose" ? value : value.map(coord => ({ ...coord })), topk });
        headers = { "Content-Type": "application/json" };
      } else {
        requestBody = new FormData();
        requestBody.append("query", value);
        requestBody.append("topk", topk);
      }
    } else {
      // Combine search type handling
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

  // Handle file change for the sketch upload
  const handleSketchUpload = useCallback((e) => {
    const file = e.target.files[0];
    if (file) {
      const reader = new FileReader();
      reader.onload = (e) => {
        setSketchData(e.target.result);
      };
      reader.readAsDataURL(file);
    }
  }, []);

  // Handle when clicked submit button
  const handleSubmit = async () => {
    // Construct the query values for the search
    const queryValues = inputValues.filter(obj => obj.value !== "");

    // Check if 'object' search is active and canvasData is not empty
    if (activeButtons.has("object") && canvasData.length > 0) {
      queryValues.push({ type: "object", value: canvasData });
    }

    if (activeButtons.has("sketch")) {
      if (sketchData) {
        queryValues.push({ type: "sketch", value: sketchData });
      } else if (sketchCanvasRef && sketchCanvasRef.current) {
        const drawnSketchData = await sketchCanvasRef.current.exportImage("jpeg");
        console.log(drawnSketchData);
        queryValues.push({ type: "sketch", value: drawnSketchData });
      }
    }

    if (activeButtons.has("pose") && poseData && poseData.length > 0) {
      queryValues.push({ type: "pose", value: poseData });
    }

    // Proceed with the search if there are valid query values
    if (queryValues.some(data => data.value !== "")) {
      await fetchResults(queryValues);
    }
  };

  // const handleFilter = async () => {
  //   console.log(object)
  //   const requestBody = JSON.stringify({ object: object });
  //   try {
  //     const response = await fetch(`${HOST_URL}filter`, {
  //       method: 'POST',
  //       headers: {
  //         'Content-Type': 'application/json'
  //       },
  //       body: requestBody
  //     });

  //     if (!response.ok) {
  //       throw new Error(`HTTP error! status: ${response.status}`);
  //     }

  //     const result = await response.json();
  //     console.log('Filter results:', result);
  //   } catch (error) {
  //     console.error('Error during fetch:', error);
  //   }
  // }

  const showCanvas = activeButtons.has("object");
  const showSketchCanvas = activeButtons.has("sketch");
  const showPose = activeButtons.has("pose");

  // Function to clear the uploaded sketch
  const handleClearUploadedSketch = useCallback(() => {
    setSketchData("");
    if (fileInputRef.current) {
      fileInputRef.current.value = "";  // Reset the file input
    }
  }, []);

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
        <div className="grid grid-cols-6 gap-2 text-gray-900">
          {["semantic", "ocr", "asr", "object", "sketch", "pose"].map((type) => (
            <div
              key={type}
              className={`col-start self-stretch px-1 py-2 text-center rounded-md text-xs font-medium cursor-pointer ${inputValues.some((input) => input.type === type)
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
                color="primary"
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
            {!sketchData && (
              <Sketch setCanvasRef={setSketchCanvasRef} />
            )}
            {sketchData && (
              <img src={sketchData} className="w-full h-auto" alt="Uploaded" />
            )}
            <div className="flex justify-between gap-2 mt-2 items-end">
              <div className="w-full">
                <label htmlFor="sketchUpload" className="text-sm font-medium text-gray-700 mb-1">Upload sketch</label>
                <input
                  ref={fileInputRef}
                  type="file"
                  id="sketchUpload"
                  accept="image/*"
                  onChange={handleSketchUpload}
                  className="block w-full text-sm text-gray-900 rounded-md border border-gray-300 cursor-pointer focus:border-blue-500"
                />
              </div>
              <button
                onClick={handleClearUploadedSketch}
                className="bg-red-500 text-white text-xs p-1.5 rounded-md hover:bg-red-600"
              >
                Clear
              </button>
            </div>
          </div>
        }
        <button onClick={handleSubmit} className="bg-blue-600 text-white p-3 rounded-full mt-2 hover:bg-blue-700">Search</button>
      </div>
    </div>
  );
};

export default SearchCard;