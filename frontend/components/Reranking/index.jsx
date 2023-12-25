import React from 'react';
import { HOST_URL } from "@/constants/api";

const Reranking = ({ relevantImages, removeRelevantImage, irrelevantImages, removeIrrelevantImage, handleImageClick }) => {
  return (
    <>
      <div className="flex flex-col gap-2 bg-white p-2 rounded-lg">
        <div className="grid grid-cols-2 gap-4">

          {/* Relevant Images Section */}
          <div className="flex flex-col gap-2">
            <h3 className="text-sm self-center font-semibold">Relevant Images</h3>
            <div className="grid gap-2">
              {relevantImages.map((image, index) => (
                <div key={index} className="relative border rounded-md">
                  <button
                    className="absolute top-1 right-1 bg-red-500 text-white px-1.5 py-0.25 rounded-full"
                    onClick={() => removeRelevantImage(image)}
                  >
                    &times;
                  </button>
                  <img src={`${HOST_URL}frame/${image}`} alt={`Relevant Image ${index}`} className="w-full h-auto cursor-pointer" onClick={() => handleImageClick(`${HOST_URL}frame/${image}`)}
                  />
                </div>
              ))}
            </div>
          </div>

          {/* Irrelevant Images Section */}
          <div className="flex flex-col gap-2">
            <h3 className="text-sm self-center font-semibold">Irrelevant Images</h3>
            <div className="grid gap-2">
              {irrelevantImages.map((image, index) => (
                <div key={index} className="relative border rounded-md">
                  <button
                    className="absolute top-1 right-1 bg-red-500 text-white px-1.5 py-0.25 rounded-full"
                    onClick={() => removeIrrelevantImage(image)}
                  >
                    &times;
                  </button>
                  <img src={`${HOST_URL}frame/${image}`} alt={`Irrelevant Image ${index}`} className="w-full h-auto cursor-pointer" onClick={() => handleImageClick(`${HOST_URL}frame/${image}`)}
                  />
                </div>
              ))}
            </div>
          </div>
        </div>
      </div>
    </>
  );
};

export default Reranking;