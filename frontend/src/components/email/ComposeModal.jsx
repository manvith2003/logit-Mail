import React, { useState } from 'react';
import { X, Minus, Maximize2, Paperclip, Image, Smile, Trash2, MoreVertical } from 'lucide-react';
import { sendEmail } from '../../lib/api';

const ComposeModal = ({ isOpen, onClose, initialData = {} }) => {
  const [to, setTo] = useState(initialData.to || '');
  const [subject, setSubject] = useState(initialData.subject || '');
  const [body, setBody] = useState(initialData.body || '');
  const [isMinimized, setIsMinimized] = useState(false);

  if (!isOpen) return null;

  if (isMinimized) {
    return (
        <div className="fixed bottom-0 right-20 w-64 bg-white rounded-t-lg shadow-lg border border-gray-300 z-50 flex justify-between items-center px-4 py-2 cursor-pointer hover:bg-gray-50"
             onClick={() => setIsMinimized(false)}>
            <span className="font-bold text-sm truncate text-gray-700">
                {subject || 'New Message'}
            </span>
            <div className="flex gap-2">
                 <button onClick={(e) => { e.stopPropagation(); setIsMinimized(false); }}><Maximize2 size={14}/></button>
                 <button onClick={(e) => { e.stopPropagation(); onClose(); }}><X size={14}/></button>
            </div>
        </div>
    )
  }

  const handleSend = async () => {
      try {
          // Basic validation
          if (!to) {
              alert('Please specify a recipient.');
              return;
          }
           
          const userId = localStorage.getItem('magic_mail_user_id');
          if (!userId) {
              alert('User not found. Please log in.');
              return;
          }

          // Convert comma-separated strings to arrays
          const toList = to.split(',').map(e => e.trim()).filter(e => e);
          
          const payload = { 
              to: toList, 
              subject, 
              body 
          };
          
          await sendEmail(userId, payload);
          alert('Email sent successfully!');
          onClose();
      } catch (error) {
          console.error(error);
          alert('Failed to send email: ' + error.message);
      }
  };

  return (
    <div className="fixed bottom-0 right-16 w-[500px] h-[600px] bg-white rounded-t-xl shadow-2xl border border-gray-200 z-50 flex flex-col font-sans">
      {/* Header */}
      <div className="flex justify-between items-center px-4 py-3 bg-gray-900 text-white rounded-t-xl cursor-pointer" onClick={() => setIsMinimized(true)}>
        <h3 className="font-medium text-sm">New Message</h3>
        <div className="flex items-center gap-3">
            <button onClick={(e) => { e.stopPropagation(); setIsMinimized(true); }} className="hover:bg-gray-700 p-1 rounded"><Minus size={14} /></button>
            <button className="hover:bg-gray-700 p-1 rounded"><Maximize2 size={14} /></button>
            <button onClick={(e) => { e.stopPropagation(); onClose(); }} className="hover:bg-red-600 p-1 rounded"><X size={14} /></button>
        </div>
      </div>

      {/* Inputs */}
      <div className="flex flex-col flex-1 overflow-hidden">
          <div className="px-4 py-2 border-b border-gray-100 flex items-center">
              <span className="text-gray-500 text-sm w-12 text-left">To</span>
              <input 
                 type="text" 
                 className="flex-1 outline-none text-sm py-1"
                 value={to}
                 onChange={(e) => setTo(e.target.value)}
              />
          </div>
          <div className="px-4 py-2 border-b border-gray-100 flex items-center">
              <span className="text-gray-500 text-sm w-12 text-left">Subject</span>
              <input 
                 type="text" 
                 className="flex-1 outline-none text-sm py-1"
                 value={subject}
                 onChange={(e) => setSubject(e.target.value)}
              />
          </div>
          
          <textarea 
             className="flex-1 p-4 outline-none resize-none text-sm leading-relaxed"
             value={body}
             onChange={(e) => setBody(e.target.value)}
          />
      </div>

      {/* Footer / Toolbar */}
      <div className="p-3 flex items-center justify-between border-t border-gray-100">
          <div className="flex items-center gap-4">
              <button 
                  onClick={handleSend}
                  className="bg-blue-600 hover:bg-blue-700 text-white px-6 py-2 rounded-full font-medium text-sm transition-colors shadow-m"
              >
                  Send
              </button>
              <div className="flex gap-1 text-gray-500">
                  <button className="p-2 hover:bg-gray-100 rounded"><Paperclip size={18}/></button> 
                  <button className="p-2 hover:bg-gray-100 rounded"><Image size={18}/></button> 
                  <button className="p-2 hover:bg-gray-100 rounded"><Smile size={18}/></button> 
              </div>
          </div>
          <div>
               <button onClick={onClose} className="p-2 hover:bg-gray-100 rounded text-gray-500"><Trash2 size={18}/></button>
          </div>
      </div>
    </div>
  );
};

export default ComposeModal;
