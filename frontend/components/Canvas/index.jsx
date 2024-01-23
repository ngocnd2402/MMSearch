import { useCallback, useEffect, useRef, useState } from 'react';
import { OBJECT_LABELS } from "@/constants/object_labels";
import { useResultData } from "@/context/provider";

const Autocomplete = ({ options, label, onChange }) => {
  const [open, setOpen] = useState(false);
  const [query, setQuery] = useState('');
  const [filteredOptions, setFilteredOptions] = useState(options);
  const ref = useRef(null);

  useEffect(() => {
    setFilteredOptions(
      options.filter((option) =>
        option.toLowerCase().includes(query.toLowerCase())
      )
    );
  }, [query, options]);

  const handleInputChange = (e) => {
    setQuery(e.target.value);
    onChange(e.target.value);
  };

  const handleOptionClick = (value) => {
    setQuery(value);
    setOpen(false);
    onChange(value);
  };

  const handleKeyDown = (e) => {
    if (e.key === 'Enter' && filteredOptions.length > 0) {
      handleOptionClick(filteredOptions[0]);
    }
  };

  const clearInput = () => {
    setQuery('');
    onChange('');
    setOpen(true)
  };

  const handleClickOutside = (e) => {
    if (ref.current && !ref.current.contains(e.target)) {
      setOpen(false);
    }
  };

  useEffect(() => {
    document.addEventListener('mousedown', handleClickOutside);
    return () => {
      document.removeEventListener('mousedown', handleClickOutside);
    };
  }, []);

  return (
    <div className="relative w-full" ref={ref}>
      <p className='text-xs mb-1'>Select object</p>
      <div className="flex w-full">
        <input
          type="text"
          value={query}
          onChange={handleInputChange}
          onKeyDown={handleKeyDown}
          onFocus={() => setOpen(true)}
          className="relative w-full border-b border-gray-300 py-2 focus:outline-none focus:border-b focus:border-b-blue-500"
          placeholder={label}
        />
        {query && (
          <button onClick={clearInput} className="absolute right-0 py-1.5 px-3 text-gray-500 hover:bg-gray-100 hover:rounded-full">
            &times;
          </button>
        )}
      </div>
      {open && (
        <div className="absolute w-full rounded-b bg-white z-50 max-h-60 overflow-auto shadow">
          {filteredOptions.map((option, index) => (
            <div
              key={index}
              onClick={() => handleOptionClick(option)}
              className={`py-3 px-4 hover:bg-gray-100 cursor-pointer`}
            >
              {option}
            </div>
          ))}
        </div>
      )}
    </div>
  );
};

const INIT_COORDS = { x: null, y: null };

const Canvas = () => {
  const canvasRef = useRef(null);
  const [ctx, setCtx] = useState(null);
  const [isDrawing, setIsDrawing] = useState(false);
  const [initialCoords, setInitialCoords] = useState(INIT_COORDS);
  const [selectionBoxes, setSelectionBoxes] = useState([]);
  const [selectedLabel, setSelectedLabel] = useState('');

  const { setCanvasData } = useResultData();

  // display grid background on the canvas
  const drawRuleOfThirdsGrid = useCallback(() => {
    if (!ctx) return;

    const { width, height } = canvasRef.current;
    const oneThirdWidth = width / 3;
    const twoThirdsWidth = 2 * oneThirdWidth;
    const oneThirdHeight = height / 3;
    const twoThirdsHeight = 2 * oneThirdHeight;

    ctx.strokeStyle = '#000000';
    ctx.lineWidth = 0.5;

    ctx.beginPath();
    ctx.moveTo(oneThirdWidth, 0);
    ctx.lineTo(oneThirdWidth, height);
    ctx.moveTo(twoThirdsWidth, 0);
    ctx.lineTo(twoThirdsWidth, height);
    ctx.moveTo(0, oneThirdHeight);
    ctx.lineTo(width, oneThirdHeight);
    ctx.moveTo(0, twoThirdsHeight);
    ctx.lineTo(width, twoThirdsHeight);
    ctx.stroke();
  }, [ctx]);

  const colors = ['red', 'green', 'blue', 'yellow', 'blue', 'orange', 'brown', 'gray', 'black'];

  // draw a bbox of a chosen object
  const drawSelection = (coords, label, color) => {
    if (!ctx) return;

    const x = Math.min(coords.initialCoords.x, coords.finalCoords.x);
    const y = Math.min(coords.initialCoords.y, coords.finalCoords.y);
    const width = Math.abs(coords.initialCoords.x - coords.finalCoords.x);
    const height = Math.abs(coords.initialCoords.y - coords.finalCoords.y);

    drawRuleOfThirdsGrid();

    ctx.beginPath();
    ctx.strokeStyle = color;
    ctx.lineWidth = 2;
    ctx.rect(x, y, width, height);
    ctx.stroke();

    if (label) {
      ctx.font = '16px Arial';
      ctx.fillStyle = 'black';
      ctx.fillText(label, x, y - 5);
    }
  };

  useEffect(() => {
    ctx?.clearRect(0, 0, canvasRef.current.width, canvasRef.current.height);
    selectionBoxes.forEach(box => drawSelection(box.coords, box.label, box.color));
  }, [selectionBoxes, ctx]);

  const onMouseDown = useCallback((e) => {
    const rect = canvasRef.current.getBoundingClientRect();
    const x = e.clientX - rect.left;
    const y = e.clientY - rect.top;
    setInitialCoords({ x, y });
    setIsDrawing(true);
  }, []);

  const redrawCanvas = useCallback(() => {
    if (!ctx) return;

    ctx.clearRect(0, 0, canvasRef.current.width, canvasRef.current.height);
    drawRuleOfThirdsGrid();
    selectionBoxes.forEach(box => drawSelection(box.coords, box.label, box.color));
  }, [ctx, drawRuleOfThirdsGrid, drawSelection, selectionBoxes]);

  useEffect(() => {
    const canvas = canvasRef.current;
    const context = canvas.getContext('2d');
    setCtx(context);

    const resizeCanvas = () => {
      const aspectRatio = 720 / 1280;
      const currentWidth = canvas.offsetWidth;
      const calculatedHeight = currentWidth * aspectRatio;
      canvas.width = currentWidth;
      canvas.height = calculatedHeight;
      redrawCanvas();
    };

    resizeCanvas();
    window.addEventListener('resize', resizeCanvas);

    return () => {
      window.removeEventListener('resize', resizeCanvas);
    };
  }, [redrawCanvas]);

  const onMouseMove = useCallback((e) => {
    if (!isDrawing) return;

    const rect = canvasRef.current.getBoundingClientRect();
    const x = e.clientX - rect.left;
    const y = e.clientY - rect.top;
    const tempFinalCoords = { x, y };

    redrawCanvas();
    const tempColor = colors[selectionBoxes.length % colors.length];
    drawSelection({ initialCoords, finalCoords: tempFinalCoords }, "", tempColor);
  }, [isDrawing, initialCoords, selectionBoxes.length, ctx, colors, redrawCanvas]);

  const normalizeCoords = (coords, label, canvasWidth, canvasHeight) => {
    return {
      x: coords.initialCoords.x / canvasWidth,
      y: coords.initialCoords.y / canvasHeight,
      w: Math.abs(coords.initialCoords.x - coords.finalCoords.x) / canvasWidth,
      h: Math.abs(coords.initialCoords.y - coords.finalCoords.y) / canvasHeight,
      label: label
    };
  };

  const handleChangeLabel = (newValue) => {
    setSelectedLabel(newValue);
  };

  const onMouseUp = useCallback((e) => { 
    setIsDrawing(false);
    if (!initialCoords.x || !initialCoords.y) return;
  
    const rect = canvasRef.current.getBoundingClientRect();
    const x = e.clientX - rect.left;
    const y = e.clientY - rect.top;
    const finalCoords = { x, y };
  
    const label = selectedLabel;
    const color = colors[selectionBoxes.length % colors.length];
    const selection = {
      coords: { initialCoords, finalCoords },
      label: label,
      color: color,
    };
    const normalized = normalizeCoords(selection.coords, selection.label, canvasRef.current.width, canvasRef.current.height);
  
    setSelectionBoxes(prev => [...prev, selection]);
    setCanvasData(prev => [...prev, normalized]);
    setInitialCoords(INIT_COORDS);
  }, [initialCoords, selectionBoxes.length, selectedLabel, colors, normalizeCoords, setCanvasData]);
  
  const clearSelection = () => {
    setSelectionBoxes([]);
    setCanvasData([]);
  };

  const CtrlZ = () => {
    setSelectionBoxes(prev => prev.slice(0, prev.length - 1));
  };

  return (
    <div className="flex flex-col gap-2">
      <div className="flex gap-8 items-end">
        <div className='flex gap-2 flex-row text-blue-600 text-xs'>
          <button onClick={CtrlZ} className="cursor-pointer font-semibold hover:text-blue-800">Undo</button>
          <button onClick={clearSelection} className="cursor-pointer font-semibold hover:text-blue-600">Clear</button>
        </div>
        <Autocomplete
          options={OBJECT_LABELS}
          value={selectedLabel}
          onChange={handleChangeLabel}
          className='w-full text-base'
        />
      </div>
      <canvas
        ref={canvasRef}
        onMouseDown={onMouseDown}
        onMouseMove={onMouseMove}
        onMouseUp={onMouseUp}
        className="border border-blue-700 w-full border-solid bg-white"
      >
      </canvas>
    </div>
  );
};

export default Canvas;