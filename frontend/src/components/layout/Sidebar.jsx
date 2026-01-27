import React from 'react';
import { Pen, Inbox, Star, Clock, Send, File, ChevronDown, Trash2, AlertOctagon } from 'lucide-react';

const SidebarItem = ({ icon: Icon, label, count, active, onClick }) => (
  <div 
    onClick={onClick}
    className={`flex items-center justify-between pl-6 pr-4 py-1.5 rounded-r-full cursor-pointer mr-2 select-none ${
        active 
        ? 'bg-blue-50 text-blue-700 font-bold' 
        : 'text-gray-700 hover:bg-gray-100'
    }`}
  >
    <div className="flex items-center gap-4">
      <Icon size={20} className={active ? 'text-blue-700' : 'text-gray-500'} />
      <span className="text-sm">{label}</span>
    </div>
    {count && (
      <span className={`text-xs ${active ? 'text-blue-700 font-bold' : 'text-gray-500 font-medium'}`}>
        {count}
      </span>
    )}
  </div>
);

const Sidebar = ({ isOpen, activeFolder, onFolderChange, onComposeClick }) => {
    // If sidebar is 'closed', we might hide it or show mini-version. 
    // Gmail behavior: Collapsed = icons only. For MVP, let's keep it simple.
    
    if (!isOpen) return null; // Or mini-sidebar implementation

    return (
        <aside className="w-64 flex-shrink-0 bg-white h-screen pt-20 pb-4 fixed left-0 top-0 overflow-y-auto pr-2 z-40">
            <div className="pl-2 mb-6">
                <button 
                    onClick={onComposeClick}
                    className="flex items-center gap-3 bg-blue-100 hover:shadow-md hover:bg-blue-100 text-gray-800 font-medium py-4 px-6 rounded-2xl transition-all shadow-sm"
                >
                    <Pen size={20} className="text-gray-700" />
                    <span>Compose</span>
                </button>
            </div>

            <div className="flex flex-col gap-1">
                <SidebarItem 
                    icon={Inbox} 
                    label="Inbox" 
                    count={12} 
                    active={activeFolder === 'inbox'} 
                    onClick={() => onFolderChange('inbox')}
                />
                <SidebarItem 
                    icon={Star} 
                    label="Starred" 
                    active={activeFolder === 'starred'} 
                    onClick={() => onFolderChange('starred')}
                />
                <SidebarItem 
                    icon={Clock} 
                    label="Snoozed" 
                    active={activeFolder === 'snoozed'} 
                    onClick={() => onFolderChange('snoozed')}
                />
                <SidebarItem 
                    icon={Send} 
                    label="Sent" 
                    active={activeFolder === 'sent'} 
                    onClick={() => onFolderChange('sent')}
                />
                <SidebarItem 
                    icon={File} 
                    label="Drafts" 
                    active={activeFolder === 'drafts'} 
                    onClick={() => onFolderChange('drafts')}
                />
                 <SidebarItem 
                    icon={Trash2} 
                    label="Trash" 
                    active={activeFolder === 'trash'} 
                    onClick={() => onFolderChange('trash')}
                />
                 <SidebarItem 
                    icon={AlertOctagon} 
                    label="Spam" 
                    active={activeFolder === 'spam'} 
                    onClick={() => onFolderChange('spam')}
                />
                <SidebarItem 
                    icon={ChevronDown} 
                    label="More" 
                />
            </div>

            {/* Labels Section */}
            <div className="mt-8">
                <div className="px-6 py-2 flex justify-between items-center group cursor-pointer text-gray-700 hover:text-gray-900">
                    <h3 className="text-sm font-medium">Labels</h3>
                    <span className="opacity-0 group-hover:opacity-100 text-lg">+</span>
                </div>
                {/* Placeholder labels */}
            </div>
        </aside>
    );
};

export default Sidebar;
