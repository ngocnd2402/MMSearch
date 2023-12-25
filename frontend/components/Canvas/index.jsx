import { useCallback, useEffect, useRef, useState } from 'react';
import { OBJECT_LABELS } from "@/constants/object_labels";
import { useResultData } from "@/context/provider";
import TextField from '@mui/material/TextField';
import Autocomplete from '@mui/material/Autocomplete';

const INIT_COORDS = { x: 0, y: 0 };

const Canvas = () => {
  const canvasRef = useRef(null);
  const [ctx, setCtx] = useState(null);
  const [isDrawing, setIsDrawing] = useState(false);
  const [initialCoords, setInitialCoords] = useState(INIT_COORDS);
  const [finalCoords, setFinalCoords] = useState(INIT_COORDS);
  const [selectionBoxes, setSelectionBoxes] = useState([]);
  const [normalizedCoords, setNormalizedCoords] = useState([]);
  const [selectedLabel, setSelectedLabel] = useState(null);

  const { updateCanvasData } = useResultData();

  // display grid background on the canvas
  const drawRuleOfThirdsGrid = useCallback(() => {
    if (!ctx) return;

    const width = canvasRef.current.width;
    const height = canvasRef.current.height;
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

  useEffect(() => {
    const canvas = canvasRef.current;
    setCtx(canvas.getContext('2d'));
    const aspectRatio = 720 / 1280;
    const currentWidth = canvas.offsetWidth;
    const calculatedHeight = currentWidth * aspectRatio;
    canvas.width = currentWidth;
    canvas.height = calculatedHeight;
    drawRuleOfThirdsGrid();
  }, [drawRuleOfThirdsGrid]);

  const colors = ['red', 'green', 'blue', 'yellow', 'purple', 'orange', 'brown', 'gray', 'black'];

  // draw a bbox of a chosen object
  const drawSelection = (coords, label, color) => {
    if (!ctx) return;

    const x = Math.min(coords.initialCoords.x, coords.finalCoords.x);
    const y = Math.min(coords.initialCoords.y, coords.finalCoords.y);
    const width = Math.abs(coords.initialCoords.x - coords.finalCoords.x);
    const height = Math.abs(coords.initialCoords.y - coords.finalCoords.y);

    ctx.beginPath();
    ctx.strokeStyle = color;
    ctx.lineWidth = 2;
    ctx.rect(x, y, width, height);
    ctx.stroke();

    if (label) {
      ctx.font = '12px Arial';
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
    setInitialCoords({
      x: e.clientX - rect.left,
      y: e.clientY - rect.top,
    });
    setIsDrawing(true);
  }, []);

  const redrawCanvas = () => {
    ctx.clearRect(0, 0, canvasRef.current.width, canvasRef.current.height);
    drawRuleOfThirdsGrid();
    selectionBoxes.forEach(box => {
      drawSelection(box.coords, box.label, box.color);
    });
  };

  useEffect(() => {
    if (ctx) {
      redrawCanvas();
    }
  }, [selectionBoxes, ctx]);

  const onMouseMove = useCallback((e) => {
    if (!isDrawing) return;
    const rect = canvasRef.current.getBoundingClientRect();
    setFinalCoords({
      x: e.clientX - rect.left,
      y: e.clientY - rect.top,
    });
    redrawCanvas();
    const tempColor = colors[(selectionBoxes.length) % colors.length];
    drawSelection({ initialCoords, finalCoords }, "", tempColor);
  }, [isDrawing, initialCoords, finalCoords, ctx, selectionBoxes.length]);

  const normalizeCoords = (coords, label, canvasWidth, canvasHeight) => {
    return {
      x: coords.initialCoords.x / canvasWidth,
      y: coords.initialCoords.y / canvasHeight,
      w: Math.abs(coords.initialCoords.x - coords.finalCoords.x) / canvasWidth,
      h: Math.abs(coords.initialCoords.y - coords.finalCoords.y) / canvasHeight,
      label: label
    };
  };

  const handleChangeLabel = (event, newValue) => {
    setSelectedLabel(newValue);
  };

  const onMouseUp = useCallback(() => {
    setIsDrawing(false);
    const label = selectedLabel;
    const color = colors[selectionBoxes.length % colors.length];
    const selection = {
      coords: { initialCoords, finalCoords },
      label: label,
      color: color,
    };
    const normalized = normalizeCoords(selection.coords, selection.label, canvasRef.current.width, canvasRef.current.height)
    setSelectionBoxes(prev => [...prev, selection]);
    setNormalizedCoords(prev => [...prev, normalized])
    setInitialCoords(INIT_COORDS);
    setFinalCoords(INIT_COORDS);
    updateCanvasData(prev => [...prev, normalized]);
  }, [initialCoords, finalCoords, selectionBoxes.length, selectedLabel, colors]);

  const clearSelection = () => {
    setSelectionBoxes([]);
    setNormalizedCoords([]);
    updateCanvasData([]);
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
          disablePortal
          disableClearable
          autoSelect
          autoHighlight
          options={OBJECT_LABELS}
          value={selectedLabel}
          onChange={handleChangeLabel}
          className='text-xs w-full'
          renderInput={(params) => <TextField {...params} label="Object" variant='standard' />}
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