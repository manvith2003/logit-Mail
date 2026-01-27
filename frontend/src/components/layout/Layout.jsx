import React, { useState } from 'react';
import Header from './Header';
import Sidebar from './Sidebar';

const Layout = (props) => {
  const { children, activeFolder, onFolderChange } = props;
  const [isSidebarOpen, setIsSidebarOpen] = useState(true);
  // const [activeFolder, setActiveFolder] = useState('inbox'); // Removed internal state

  const toggleSidebar = () => {
    setIsSidebarOpen(!isSidebarOpen);
  };

  return (
    <div className="min-h-screen bg-white">
      <Header toggleSidebar={toggleSidebar} onSearch={props.onSearch} />
      
      <div className="pt-16 flex h-screen overflow-hidden">
        <Sidebar 
            isOpen={isSidebarOpen} 
            activeFolder={activeFolder}
            onFolderChange={onFolderChange}
            onComposeClick={props.onComposeClick}
        />
        
        <main className={`flex-1 overflow-auto bg-white rounded-tl-2xl transition-all duration-300 ${isSidebarOpen ? 'ml-64' : 'ml-0'}`}>
          {children}
        </main>
      </div>
    </div>
  );
};

export default Layout;
