import React, { useState } from 'react';
import { Calendar, X, Check } from 'lucide-react';
import { useToast } from '../context/ToastContext';
import { API_BASE_URL } from '../lib/api';

const NotificationBanner = ({ emails, userId, onActionComplete }) => {
    // Filter for action items
    const actionItems = emails.filter(e => e.action_required && !e.calendar_event_id);
    const { showToast } = useToast();
    const [loading, setLoading] = useState(false);

    if (!emails || !Array.isArray(emails) || actionItems.length === 0) return null;

    // Just show the first one to avoid clutter
    const item = actionItems[0];
    const eventDate = item.event_date ? new Date(item.event_date).toLocaleDateString() : 'Unknown Date';
    const title = item.event_title || item.subject;

    const handleAddCalendar = async () => {
        setLoading(true);
        try {
            const response = await fetch(`${API_BASE_URL}/calendar/events`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    user_id: userId,
                    title: title,
                    start_time: item.event_date || new Date().toISOString(), // Fallback
                    description: `Source Email: ${item.subject}\n\n${item.snippet}`
                })
            });

            if (response.ok) {
                const data = await response.json();
                showToast("Event added to Google Calendar!", { type: 'success' });
                // Dismiss action locally and on server
                handleDismiss(); 
                if (data.event_link) {
                    window.open(data.event_link, '_blank');
                }
            } else {
                throw new Error("Failed to add event");
            }
        } catch (error) {
            console.error(error);
            showToast("Failed to add to calendar", { type: 'error' });
        } finally {
            setLoading(false);
        }
    };

    const handleDismiss = async () => {
        // Optimistic UI update
        onActionComplete(item.id);

        try {
            await fetch(`${API_BASE_URL}/emails/${item.id}/dismiss_action?user_id=${userId}`, {
                method: 'POST'
            });
        } catch (error) {
            console.error("Failed to dismiss action", error);
        }
    };

    return (
        <div className="bg-indigo-50 border-b border-indigo-100 p-4 flex items-center justify-between animate-in slide-in-from-top-2">
            <div className="flex items-center gap-3">
                <div className="bg-indigo-100 p-2 rounded-full text-indigo-600">
                    <Calendar size={20} />
                </div>
                <div>
                    <h4 className="font-semibold text-indigo-900 text-sm">AI Detected Event</h4>
                    <p className="text-indigo-700 text-xs">
                        "{title}" on {eventDate}
                    </p>
                </div>
            </div>
            <div className="flex items-center gap-2">
                <button 
                    onClick={handleDismiss}
                    className="p-2 text-indigo-400 hover:text-indigo-600 hover:bg-indigo-100 rounded-lg transition-colors"
                    title="Dismiss"
                >
                    <X size={18} />
                </button>
                <button 
                    onClick={handleAddCalendar}
                    disabled={loading}
                    className="flex items-center gap-2 px-3 py-1.5 bg-indigo-600 hover:bg-indigo-700 text-white text-xs font-medium rounded-lg transition-colors shadow-sm"
                >
                    {loading ? 'Adding...' : (
                        <>
                            <Check size={14} />
                            Add to Calendar
                        </>
                    )}
                </button>
            </div>
        </div>
    );
};

export default NotificationBanner;
