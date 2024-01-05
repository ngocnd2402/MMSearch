import React, { useState, useCallback, useEffect, useRef, useMemo } from 'react';
import { useResultData } from "@/context/provider";

const Circle = ({ id, cx, cy, colorStr, onMouseDown }) => {
    const [isHovered, setIsHovered] = useState(false);
    const [isActive, setIsActive] = useState(false);

    const handleMouseDown = (e) => {
        onMouseDown(e, id);
        setIsActive(true);
    };

    const handleMouseEnter = () => setIsHovered(true);
    const handleMouseLeave = () => setIsHovered(false);
    const handleMouseUp = () => setIsActive(false);

    const highlightRadius = 5 * 2;

    return (
        <>
            { (isHovered || isActive) && (
                <circle
                    cx={cx}
                    cy={cy}
                    r={highlightRadius}
                    fill={colorStr}
                    fillOpacity={0.3}
                />
            )}
            <circle
                cx={cx}
                cy={cy}
                r={5}
                fill={colorStr}
                onMouseDown={handleMouseDown}
                onMouseEnter={handleMouseEnter}
                onMouseLeave={handleMouseLeave}
                onMouseUp={handleMouseUp}
                className="cursor-grab"
            />
        </>
    );
};

const DynamicLine = ({ point1, point2, colorStr }) => {
    return (
        <line x1={point1.cx} y1={point1.cy} x2={point2.cx} y2={point2.cy} stroke={colorStr} strokeWidth={5} />
    );
};

const Pose = () => {
    const svgRef = useRef(null);
    const { setPoseData } = useResultData();

    const [points, setPoints] = useState([
        { id: 0, cx: 160, cy:30, colorStr: "#E92EFB" },
        { id: 1, cx: 132, cy: 60, colorStr: "#FF2079" },
        { id: 2, cx: 188, cy: 60, colorStr: "#FF2079"},
        { id: 3, cx: 108, cy: 98, colorStr: "#FE6F61"},
        { id: 4, cx: 216, cy: 106, colorStr: "#FE6F61"},
        { id: 5, cx: 112, cy: 164, colorStr: "#FEEC2D"},
        { id: 6, cx: 208, cy: 164, colorStr: "#FEEC2D"},
        { id: 7, cx: 144, cy: 154, colorStr: "#00FF2E"},
        { id: 8, cx: 184, cy: 154, colorStr: "#00FF2E"},
        { id: 9, cx: 126, cy: 230, colorStr: "#00DDFF"},
        { id: 10, cx: 196, cy: 230, colorStr: "#00DDFF"},
        { id: 11, cx: 122, cy: 300, colorStr: "#057DFF"},
        { id: 12, cx: 200, cy: 300, colorStr: "#057DFF"},
        { id: 13, cx: 160, cy: 60, colorStr: "#E92EFB" },
    ]);
    
    const [isDragging, setIsDragging] = useState(false);
    const [draggingPointId, setDraggingPointId] = useState(null);

    const normalizePoints = useCallback(() => {
        const svgRect = svgRef.current.getBoundingClientRect();
        const normalizedData = points.flatMap(point => {
          const cx = parseFloat((point.cx / svgRect.width).toFixed(3));
          const cy = parseFloat((point.cy / svgRect.height).toFixed(3));
          return [cx, cy];
        });
        setPoseData(normalizedData);
      }, [points, setPoseData]);
      

    useEffect(() => {
        normalizePoints();
    }, [normalizePoints])

    const onMouseDown = useCallback((e, id) => {
        setIsDragging(true);
        setDraggingPointId(id);
        e.stopPropagation();
    }, []);

    const onMouseMove = useCallback((e) => {
        if (isDragging) {
            const svgRect = svgRef.current.getBoundingClientRect();
            setPoints(prevPoints => prevPoints.map(point => {
                if (point.id === draggingPointId) {
                    return {
                        ...point,
                        cx: e.clientX - svgRect.left,
                        cy: e.clientY - svgRect.top
                    };
                }
                return point;
            }));
        }
    }, [isDragging, draggingPointId]);

    const onMouseUp = useCallback(() => {
        setIsDragging(false);
        setDraggingPointId(null);
    }, []);

    useEffect(() => {
        if (isDragging) {
            window.addEventListener('mousemove', onMouseMove);
            window.addEventListener('mouseup', onMouseUp);
        } else {
            window.removeEventListener('mousemove', onMouseMove);
            window.removeEventListener('mouseup', onMouseUp);
        }
        return () => {
            window.removeEventListener('mousemove', onMouseMove);
            window.removeEventListener('mouseup', onMouseUp);
        };
    }, [isDragging, onMouseMove, onMouseUp]);

    useEffect(() => {
        const handleGlobalMouseUp = () => {
            if (isDragging) setIsDragging(false);
        };

        window.addEventListener('mouseup', handleGlobalMouseUp);
        return () => window.removeEventListener('mouseup', handleGlobalMouseUp);
    }, [isDragging]);

    const lines = useMemo(() => {
        const lineConnections = [
            { startId: 0, endId: 13, colorStr: "#E92EFB" },
            { startId: 13, endId: 1, colorStr: "#FF2079" },
            { startId: 13, endId: 2, colorStr: "#FF2079" },
            { startId: 7, endId: 8, colorStr: "#00FF2E" },
            { startId: 1, endId: 7, colorStr: "#00FF2E" },
            { startId: 2, endId: 8, colorStr: "#00FF2E" },
            { startId: 7, endId: 9, colorStr: "#00DDFF" },
            { startId: 9, endId: 11, colorStr: "#057DFF" },
            { startId: 8, endId: 10, colorStr: "#00DDFF" },
            { startId: 10, endId: 12, colorStr: "#057DFF" },
            { startId: 1, endId: 3, colorStr: "#FE6F61" },
            { startId: 3, endId: 5, colorStr: "#FEEC2D" },
            { startId: 2, endId: 4, colorStr: "#FE6F61" },
            { startId: 4, endId: 6, colorStr: "#FEEC2D" },
        ];
        return lineConnections.map(({ startId, endId, colorStr }) => {
            const point1 = points.find(p => p.id === startId);
            const point2 = points.find(p => p.id === endId);
            return point1 && point2 ? (
                <DynamicLine key={`${startId}-${endId}`} point1={point1} point2={point2} colorStr={colorStr} />
            ) : null;
        });
    }, [points]);

    const setArmsFolded = () => {
        setPoints([
            { id: 0, cx: 160, cy:30, colorStr: "#E92EFB" },
            { id: 1, cx: 130, cy: 72, colorStr: "#FF2079" },
            { id: 2, cx: 194, cy: 68, colorStr: "#FF2079"},
            { id: 3, cx: 120, cy: 128, colorStr: "#FE6F61"},
            { id: 4, cx: 208, cy: 122, colorStr: "#FE6F61"},
            { id: 5, cx: 184, cy: 120, colorStr: "#FEEC2D"},
            { id: 6, cx: 146, cy: 132, colorStr: "#FEEC2D"},
            { id: 7, cx: 136, cy: 154, colorStr: "#00FF2E"},
            { id: 8, cx: 184, cy: 154, colorStr: "#00FF2E"},
            { id: 9, cx: 120, cy: 230, colorStr: "#00DDFF"},
            { id: 10, cx: 200, cy: 230, colorStr: "#00DDFF"},
            { id: 11, cx: 118, cy: 300, colorStr: "#057DFF"},
            { id: 12, cx: 202, cy: 300, colorStr: "#057DFF"},
            { id: 13, cx: 160, cy: 60, colorStr: "#E92EFB" },
        ])
    }

    const setUpSideDown = () => {
        setPoints([
            { id: 0, cx: 152, cy: 246, colorStr: "#E92EFB" },
            { id: 1, cx: 142, cy: 216, colorStr: "#FF2079" },
            { id: 2, cx: 176, cy: 218, colorStr: "#FF2079"},
            { id: 3, cx: 118, cy: 200, colorStr: "#FE6F61"},
            { id: 4, cx: 186, cy: 250, colorStr: "#FE6F61"},
            { id: 5, cx: 140, cy: 138, colorStr: "#FEEC2D"},
            { id: 6, cx: 172, cy: 294, colorStr: "#FEEC2D"},
            { id: 7, cx: 142, cy: 160, colorStr: "#00FF2E"},
            { id: 8, cx: 180, cy: 158, colorStr: "#00FF2E"},
            { id: 9, cx: 146, cy: 102, colorStr: "#00DDFF"},
            { id: 10, cx: 188, cy: 102, colorStr: "#00DDFF"},
            { id: 11, cx: 160, cy: 38, colorStr: "#057DFF"},
            { id: 12, cx: 198, cy: 38, colorStr: "#057DFF"},
            { id: 13, cx: 160, cy: 218, colorStr: "#E92EFB" },
        ])
    }

    const setTouchHead = () => {
        setPoints([
            { id: 0, cx: 168, cy: 134, colorStr: "#E92EFB" },  // Nose (head slightly lifted)
            { id: 1, cx: 132, cy: 162, colorStr: "#FF2079" },  // Left Shoulder
            { id: 2, cx: 196, cy: 164, colorStr: "#FF2079" },  // Right Shoulder
            { id: 3, cx: 120, cy: 148, colorStr: "#FE6F61" },  // Left Elbow (straight arms)
            { id: 4, cx: 222, cy: 156, colorStr: "#FE6F61" },  // Right Elbow
            { id: 5, cx: 152, cy: 134, colorStr: "#FEEC2D" },  // Left Wrist/Hand (directly under shoulders)
            { id: 6, cx: 192, cy: 132, colorStr: "#FEEC2D" },  // Right Wrist/Hand
            { id: 7, cx: 142, cy: 228, colorStr: "#00FF2E" },  // Left Hip
            { id: 8, cx: 186, cy: 230, colorStr: "#00FF2E" },  // Right Hip
            { id: 9, cx: 128, cy: 264, colorStr: "#00DDFF" },  // Left Knee (legs straight)
            { id: 10, cx: 188, cy: 270, colorStr: "#00DDFF" }, // Right Knee
            { id: 11, cx: 116, cy: 320, colorStr: "#057DFF" }, // Left Ankle/Foot (feet together)
            { id: 12, cx: 208, cy: 320, colorStr: "#057DFF" }, // Right Ankle/Foot
            { id: 13, cx: 168, cy: 164, colorStr: "#E92EFB" }, // Neck (aligned with the back)
        ]);
    }

    const setDefault = () => {
        setPoints([
            { id: 0, cx: 160, cy:30, colorStr: "#E92EFB" },
            { id: 1, cx: 132, cy: 60, colorStr: "#FF2079" },
            { id: 2, cx: 188, cy: 60, colorStr: "#FF2079"},
            { id: 3, cx: 108, cy: 98, colorStr: "#FE6F61"},
            { id: 4, cx: 216, cy: 106, colorStr: "#FE6F61"},
            { id: 5, cx: 112, cy: 164, colorStr: "#FEEC2D"},
            { id: 6, cx: 208, cy: 164, colorStr: "#FEEC2D"},
            { id: 7, cx: 144, cy: 154, colorStr: "#00FF2E"},
            { id: 8, cx: 184, cy: 154, colorStr: "#00FF2E"},
            { id: 9, cx: 126, cy: 230, colorStr: "#00DDFF"},
            { id: 10, cx: 196, cy: 230, colorStr: "#00DDFF"},
            { id: 11, cx: 122, cy: 300, colorStr: "#057DFF"},
            { id: 12, cx: 200, cy: 300, colorStr: "#057DFF"},
            { id: 13, cx: 160, cy: 60, colorStr: "#E92EFB" },
        ]);
    }
 
    return (
        <>
            <svg ref={svgRef} className='w-full' height={336} style={{ border: '1px solid #9c9c9c' }}>
                {lines}
                {points.map(point => (
                    <Circle 
                        key={point.id} 
                        id={point.id}
                        cx={point.cx} 
                        cy={point.cy} 
                        r={point.r} 
                        colorStr={point.colorStr}
                        onMouseDown={onMouseDown}
                    />
                ))}
            </svg>
            <div>
                <p className='text-xs mt-2'>Try some poses</p>
                <div className='flex gap-2 mt-2 font-medium text-xs'>
                    <button className='border border-blue-400 bg-gray-50 rounded-md p-1.5' onClick={setDefault}>Default</button>
                    <button className='border border-blue-400 bg-gray-50 rounded-md p-1.5' onClick={setArmsFolded}>Hands folded</button>
                    <button className='border border-blue-400 bg-gray-50 rounded-md p-1.5' onClick={setUpSideDown}>Upside down</button>
                    <button className='border border-blue-400 bg-gray-50 rounded-md p-1.5' onClick={setTouchHead}>Touch head</button>
                </div>
            </div>        
        </>
    );
};

export default Pose;