import React, { useState, useEffect } from 'react';
import { HOST_URL } from '@/constants/api';

const Video = ({path, videoTime}) => {
  const [embedUrl, setEmbedUrl] = useState("");

  useEffect(() => {
    const fetchVideoUrl = async () => {
      try {
        const response = await fetch(`${HOST_URL}metadata/${path}.json`);
        const data = await response.json();
        if (data.watch_url) {
          const videoId = data.watch_url.split('v=')[1].split('&')[0]; // Extract the video ID
          const embedLink = `https://www.youtube.com/embed/${videoId}?autoplay=1&start=${Math.floor(videoTime)}`;
          setEmbedUrl(embedLink);
        }
      } catch (error) {
        console.error("Error fetching video URL:", error);
      }
    };

    fetchVideoUrl();
  }, [path, videoTime]);

  return (
    <>
      {embedUrl && (
        <iframe
          width="1280"
          height="720"
          src={embedUrl}
          frameBorder="0"
          allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture"
          allowFullScreen
        ></iframe>
      )}
    </>
  );
};

export default Video;