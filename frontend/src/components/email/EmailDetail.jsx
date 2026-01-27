import React from 'react';
import { ArrowLeft, Printer, ExternalLink, Star, Reply, CornerUpLeft, MoreVertical } from 'lucide-react';

const EmailDetail = ({ email, onBack, onReply }) => {
  if (!email) return null;

  return (
    <div className="h-full flex flex-col bg-white">
        {/* Toolbar */}
        <div className="flex items-center justify-between px-4 py-3 border-b border-gray-100">
            <div className="flex items-center gap-4">
                <button onClick={onBack} className="p-2 hover:bg-gray-100 rounded-full text-gray-600">
                    <ArrowLeft size={20} />
                </button>
                <div className="flex gap-2">
                    <button className="p-2 hover:bg-gray-100 rounded-full text-gray-600"><Archive size={18}/></button>
                    <button className="p-2 hover:bg-gray-100 rounded-full text-gray-600"><Trash2 size={18}/></button>
                    <button className="p-2 hover:bg-gray-100 rounded-full text-gray-600"><Mail size={18}/></button>
                </div>
            </div>
            <div className="text-gray-500 text-sm">
                1 of 24
            </div>
        </div>

        <div className="flex-1 overflow-y-auto p-8 max-w-4xl mx-auto w-full">
            {/* Subject Header */}
            <div className="flex items-start justify-between mb-6">
                <h1 className="text-2xl font-normal text-gray-900">
                    {email.subject || '(No Subject)'}
                </h1>
                <div className="flex gap-2">
                   <span className="px-2 py-1 bg-gray-200 rounded text-xs text-gray-600 font-medium">Inbox</span>
                </div>
            </div>

            {/* Sender Info Row */}
            <div className="flex items-center justify-between mb-8">
                <div className="flex items-center gap-4">
                     <div className="w-10 h-10 rounded-full bg-blue-600 flex items-center justify-center text-white font-medium text-lg">
                        {email.sender ? email.sender.trim()[0].toUpperCase() : '?'}
                     </div>
                     <div>
                        <div className="flex items-center gap-2">
                             <span className="font-bold text-gray-900 text-sm">
                                {email.sender ? email.sender.split('<')[0].trim() : 'Unknown'}
                             </span>
                             <span className="text-gray-500 text-sm">
                                {email.sender.includes('<') ? `<${email.sender.split('<')[1]}` : ''}
                             </span>
                        </div>
                        <div className="text-xs text-gray-500">
                            to me
                        </div>
                     </div>
                </div>
                <div className="flex items-center gap-4 text-gray-500 text-sm">
                     <span>{new Date(email.received_at).toLocaleString()}</span>
                     <Star size={18} className="cursor-pointer hover:text-yellow-400" />
                     <button onClick={() => onReply(email)} className="p-1 hover:bg-gray-100 rounded">
                        <Reply size={18} className="cursor-pointer hover:text-gray-700" />
                     </button>
                     <MoreVertical size={18} className="cursor-pointer hover:text-gray-700" />
                </div>
            </div>

            {/* AI Summary Card (Our Feature) */}
            {(email.event_title || email.deadline || email.action_required) && (
                <div className="mb-8 bg-gradient-to-r from-indigo-50 to-white border border-indigo-100 rounded-xl p-5 shadow-sm">
                    <div className="flex items-center gap-2 mb-3">
                        <div className="p-1.5 bg-indigo-100 rounded-md">
                           <svg className="w-4 h-4 text-indigo-600" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 10V3L4 14h7v7l9-11h-7z" /></svg>
                        </div>
                        <h3 className="text-sm font-bold text-indigo-900">Magic Mail AI Analysis</h3>
                    </div>
                    
                    <div className="grid grid-cols-1 md:grid-cols-2 gap-6 pl-1">
                        {email.event_title && (
                            <div>
                                <span className="text-xs uppercase text-indigo-400 font-semibold tracking-wider">Event Detected</span>
                                <p className="text-gray-900 font-medium mt-0.5">{email.event_title}</p>
                                {email.event_date && (
                                    <p className="text-gray-600 text-sm mt-1 flex items-center gap-1">
                                        📅 {new Date(email.event_date).toLocaleString()}
                                    </p>
                                )}
                            </div>
                        )}
                         
                        {(email.deadline || email.action_required) && (
                            <div>
                                <span className="text-xs uppercase text-red-400 font-semibold tracking-wider">Attention</span>
                                {email.deadline && (
                                    <p className="text-red-700 font-medium mt-0.5 flex items-center gap-1">
                                        ⏰ Deadline: {new Date(email.deadline).toLocaleString()}
                                    </p>
                                )}
                                {email.action_required && !email.deadline && (
                                     <p className="text-gray-900 font-medium mt-0.5">Action is likely required.</p>
                                )}
                            </div>
                        )}
                    </div>
                </div>
            )}

            {/* Email Body */}
            <div className="prose prose-sm max-w-none text-gray-800 font-sans leading-relaxed whitespace-pre-wrap">
                {email.body_text || email.snippet}
            </div>

            {/* Bottom Actions */}
            <div className="mt-12 flex gap-4">
                 <button 
                    onClick={() => onReply(email)}
                    className="flex items-center gap-2 px-6 py-2 border border-gray-300 rounded-full text-gray-600 hover:bg-gray-50 text-sm font-medium transition-colors"
                 >
                    <Reply size={16} /> Reply
                 </button>
                 <button className="flex items-center gap-2 px-6 py-2 border border-gray-300 rounded-full text-gray-600 hover:bg-gray-50 text-sm font-medium transition-colors">
                    <CornerUpLeft size={16} /> Forward
                 </button>
            </div>
        </div>
    </div>
  );
};
import { Archive, Trash2, Mail } from 'lucide-react'; // Imports for the toolbar icons

export default EmailDetail;
