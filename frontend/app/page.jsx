"use client"

import React from 'react';
import Gallery from "@/components/Gallery";
import Sidebar from "@/components/Sidebar";
import { ResultDataProvider } from '@/context/provider';

export default function Home() {
  return (
    <ResultDataProvider>
      <div className='flex bg-blue-100'>
        <Sidebar />
        <Gallery />     
      </div> 
    </ResultDataProvider>
  );
}