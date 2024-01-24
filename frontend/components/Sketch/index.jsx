import React, { useEffect, useRef } from "react";
import {
    ReactSketchCanvas,
} from "react-sketch-canvas";
import { Undo, Redo, Edit, Eraser, Restart } from "./Icons";

const styles = {
    border: "0.0625rem solid #9c9c9c",
};

const Sketch = ({ setCanvasRef }) => {
    const canvasRef = useRef();

    const penHandler = () => {
        const eraseMode = canvasRef.current?.eraseMode;

        if (eraseMode) {
            eraseMode(false);
        }
    };

    const eraserHandler = () => {
        const eraseMode = canvasRef.current?.eraseMode;

        if (eraseMode) {
            eraseMode(true);
        }
    };

    const undoHandler = () => {
        const undo = canvasRef.current?.undo;

        if (undo) {
            undo();
        }
    };

    const redoHandler = () => {
        const redo = canvasRef.current?.redo;

        if (redo) {
            redo();
        }
    };

    const resetCanvasHandler = () => {
        const resetCanvas = canvasRef.current?.resetCanvas;

        if (resetCanvas) {
            resetCanvas();
        }
    };

    useEffect(() => {
        if (setCanvasRef) {
            setCanvasRef(canvasRef);
        }
    }, [setCanvasRef]);

    return (
        <div className="flex flex-col gap-2">
            <div className="flex flex-row justify-between">
                <div className="flex flex-row gap-1">
                    <button onClick={undoHandler} className="hover:text-blue-800">
                        <Undo />
                    </button>
                    <button onClick={redoHandler} className="hover:text-blue-800">
                        <Redo />
                    </button>
                    <button onClick={resetCanvasHandler} className="hover:text-blue-800">
                        <Restart />
                    </button>
                </div>
                <div className="flex flex-row gap-1">
                    <button onClick={penHandler} className="hover:text-blue-800">
                        <Edit />
                    </button>
                    <button onClick={eraserHandler} className="hover:text-blue-800">
                        <Eraser />
                    </button>
                </div>
            </div>
            <ReactSketchCanvas
                ref={canvasRef}
                style={styles}
                strokeWidth={2}
                strokeColor="#000000"
                canvasColor="#FFFFFF"
                height={250}
            />
        </div>
    );
}

export default Sketch;