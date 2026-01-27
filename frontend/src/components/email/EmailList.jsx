import React, { useState, useRef } from 'react';
import { Star, Square, Archive, Trash2, MailOpen } from 'lucide-react';

const SwipeableEmailItem = ({ email, onClick, onStar, onDelete }) => {
  const [startX, setStartX] = useState(0);
  const [translateX, setTranslateX] = useState(0);
  const isSwiping = useRef(false);

  const onTouchStart = (e) => {
    setStartX(e.targetTouches[0].clientX);
    isSwiping.current = true;
  };

  const onTouchMove = (e) => {
    if (!isSwiping.current) return;
    const currentX = e.targetTouches[0].clientX;
    const diff = currentX - startX;
    
    // Only allow swiping left for now (Delete) behavior
    // Limit right swipe to 0 (no action) or small bounce
    if (diff < 0) { 
        setTranslateX(diff);
    }
  };

  const onTouchEnd = () => {
    isSwiping.current = false;
    if (translateX < -100) {
        // Swiped far enough - Trigger Delete
        setTranslateX(-500); // Animate out
        setTimeout(() => onDelete(email), 200); // Wait for animation
    } else {
        // Reset
        setTranslateX(0);
    }
  };

  const isUnread = !email.is_processed;
  const date = new Date(email.received_at);
  const isToday = date.toDateString() === new Date().toDateString();
  const dateStr = isToday 
    ? date.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }) 
    : date.toLocaleDateString([], { month: 'short', day: 'numeric' });

  const showRedBackground = translateX < -10; // Only show red if actually swiping

  return (
    <div 
        className={`relative overflow-hidden border-b border-gray-100 ${showRedBackground ? 'bg-red-500' : 'bg-white'}`} 
    >
        {/* Swipe Action Background (Delete Icon exposed on right) */}
        <div className={`absolute inset-y-0 right-0 w-full flex items-center justify-end px-6 text-white pointer-events-none transition-opacity ${showRedBackground ? 'opacity-100' : 'opacity-0'}`}>
             <Trash2 size={24} />
        </div>

        {/* Foreground Content */}
        <div 
            onClick={() => onClick(email)}
            onTouchStart={onTouchStart}
            onTouchMove={onTouchMove}
            onTouchEnd={onTouchEnd}
            style={{ transform: `translateX(${translateX}px)`, transition: isSwiping.current ? 'none' : 'transform 0.2s ease-out' }}
            className={`group flex items-center px-4 py-2.5 hover:shadow-sm hover:z-10 relative cursor-pointer bg-white ${
                isUnread ? 'bg-white' : 'bg-gray-50' // Changed bg-gray-50/50 to bg-gray-50 (Opaque)
            }`}
        >
            {/* 1. Checkbox & Star */}
            <div className="flex items-center gap-3 min-w-[60px] text-gray-400">
               <button onClick={(e) => e.stopPropagation()} className="hover:text-gray-600">
                 <Square size={18} />
               </button>
               <button onClick={(e) => { e.stopPropagation(); onStar(email); }} className="hover:text-yellow-400">
                 <Star size={18} className={email.labelIds?.includes('STARRED') ? "fill-yellow-400 text-yellow-400" : "text-gray-400"} />
               </button>
            </div>

            {/* 2. Sender */}
            <div className={`w-48 truncate pr-4 text-sm ${isUnread ? 'font-bold text-gray-900' : 'font-medium text-gray-700'}`}>
                {email.sender ? email.sender.split('<')[0].trim() : 'Unknown'}
            </div>

            {/* 3. Subject - Snippet */}
            <div className="flex-1 min-w-0 flex items-center text-sm">
                <span className={`truncate ${isUnread ? 'font-bold text-gray-900' : 'font-medium text-gray-600'}`}>
                    {email.subject || '(No Subject)'}
                </span>
                <span className="mx-2 text-gray-400">-</span>
                <span className="text-gray-500 truncate">
                    {email.snippet}
                </span>
                
                {/* AI Tags */}
                {email.event_title && (
                    <span className="ml-2 px-2 py-0.5 bg-green-100 text-green-700 text-xs rounded-full whitespace-nowrap">
                        Event
                    </span>
                )}
                {email.action_required && (
                    <span className="ml-2 px-2 py-0.5 bg-red-100 text-red-700 text-xs rounded-full whitespace-nowrap">
                        Action
                    </span>
                )}
            </div>

            {/* 4. Date / Actions */}
            <div className="w-24 text-right text-xs font-bold text-gray-500 group-hover:hidden whitespace-nowrap">
                {dateStr}
            </div>

            {/* Hover Actions (Desktop) */}
            <div className="hidden group-hover:flex items-center gap-2 pl-2 w-24 justify-end bg-white/80 backdrop-blur-sm">
                <button title="Archive" className="p-1.5 hover:bg-gray-200 rounded-full text-gray-600" onClick={(e) => e.stopPropagation()}>
                    <Archive size={16} />
                </button>
                <button title="Delete" className="p-1.5 hover:bg-gray-200 rounded-full text-gray-600" onClick={(e) => { e.stopPropagation(); onDelete(email); }}>
                    <Trash2 size={16} />
                </button>
                <button title="Mark as Read" className="p-1.5 hover:bg-gray-200 rounded-full text-gray-600" onClick={(e) => e.stopPropagation()}>
                    <MailOpen size={16} />
                </button>
            </div>
      </div>
    </div>
  );
};

const EmailList = ({ emails, onEmailClick, onStar, onDelete }) => {
  return (
    <div className="w-full">
      {emails.map((email) => (
         <SwipeableEmailItem 
            key={email.id} 
            email={email} 
            onClick={onEmailClick} 
            onStar={onStar} 
            onDelete={onDelete} 
         />
      ))}
    </div>
  );
};

export default EmailList;
