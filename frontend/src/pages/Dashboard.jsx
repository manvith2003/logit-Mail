import React, { useEffect, useState } from 'react';
import { useSearchParams, useNavigate } from 'react-router-dom';
import { RefreshCcw } from 'lucide-react';
import { syncEmails, getEmails, starEmail, unstarEmail, trashEmail, untrashEmail, addToCalendar, dismissEmailAction } from '../lib/api';
import { useToast } from '../context/ToastContext';
import { useDebounce } from '../hooks/useDebounce';
import Layout from '../components/layout/Layout';
import EmailList from '../components/email/EmailList';
import EmailDetail from '../components/email/EmailDetail';
import ComposeModal from '../components/email/ComposeModal';
import NotificationBanner from '../components/NotificationBanner';

const Dashboard = () => {
  const [searchParams] = useSearchParams();
  const navigate = useNavigate();
  const urlUserId = searchParams.get('user_id');
  
  const [userId, setUserId] = useState(null);
  const [emails, setEmails] = useState([]);
  const [activeFolder, setActiveFolder] = useState('inbox');
  const [loading, setLoading] = useState(false);
  const [syncing, setSyncing] = useState(false);
  const [syncLimit, setSyncLimit] = useState(50);
  const [debugError, setDebugError] = useState(null);
  const [selectedEmail, setSelectedEmail] = useState(null);
  const [isComposeOpen, setIsComposeOpen] = useState(false);
  
  const [searchQuery, setSearchQuery] = useState('');
  const [page, setPage] = useState(0); 
  const limit = 100; 
  
  const debouncedSearchQuery = useDebounce(searchQuery, 500);

  useEffect(() => {
    // 1. Check URL first (fresh login)
    if (urlUserId) {
      localStorage.setItem('magic_mail_user_id', urlUserId);
      setUserId(urlUserId);
      // Clean URL
      navigate('/dashboard', { replace: true });
    } else {
      // 2. Check localStorage (persistent session)
      const storedUserId = localStorage.getItem('magic_mail_user_id');
      if (storedUserId) {
        setUserId(storedUserId);
      } else {
        // Not logged in
        navigate('/login');
      }
    }
  }, [urlUserId, navigate]);

  useEffect(() => {
    // Reset page when folder/search changes
    setPage(0);
  }, [activeFolder, debouncedSearchQuery]);

  useEffect(() => {
    if (userId) {
      fetchEmails();
      // Trigger silent sync on load (Limit 50 to prevent lagging)
      syncEmails(userId, activeFolder, 50).catch(err => console.error("Auto-sync failed", err));
    }
  }, [userId, activeFolder, debouncedSearchQuery, page]); 

  const fetchEmails = async () => {
    setLoading(true);
    setDebugError(null);
    try {
      const skip = page * limit;
      console.log("Fetching emails:", { userId, activeFolder, debouncedSearchQuery, limit, skip });
      const data = await getEmails(userId, activeFolder, debouncedSearchQuery, limit, skip);
      if (Array.isArray(data)) {
          setEmails(data);
      } else {
          console.warn("API returned non-array data:", data);
          setEmails([]);
      }
    } catch (error) {
      console.error(error);
      setDebugError(error.toString());
    } finally {
      setLoading(false);
    }
  };

  const handleSync = async () => {
    setSyncing(true);
    try {
      await syncEmails(userId, activeFolder, syncLimit);
      await fetchEmails(); 
    } catch (error) {
      console.error(error);
      alert('Failed to sync emails. You might need to re-login to grant permissions.');
    } finally {
      setSyncing(false);
    }
  };

  const { showToast } = useToast();

  const handleStar = async (email) => {
      // Optimistic Update
      const isStarred = email.labelIds?.includes('STARRED');
      const newLabels = isStarred 
          ? (email.labelIds || []).filter(l => l !== 'STARRED')
          : [...(email.labelIds || []), 'STARRED'];
          
      setEmails(emails.map(e => e.id === email.id ? { ...e, labelIds: newLabels } : e));

      try {
          if (isStarred) {
              await unstarEmail(userId, email.message_id);
          } else {
              await starEmail(userId, email.message_id);
          }
      } catch (error) {
          console.error("Failed to star/unstar", error);
          // Revert on error (could implement better rollback)
          fetchEmails();
      }
  };

  const handleDelete = async (email) => {
      // Optimistic Update: Remove from list
      const previousEmails = [...emails];
      setEmails(emails.filter(e => e.id !== email.id));

      // Show Toast with Undo
      showToast("Email moved to trash", {
          action: {
              label: "Undo",
              onClick: async () => {
                  // Undo UI
                  setEmails(previousEmails);
                  try {
                      await untrashEmail(userId, email.message_id);
                  } catch (e) {
                      console.error("Undo failed", e);
                  }
              }
          }
      });

      try {
          await trashEmail(userId, email.message_id);
      } catch (error) {
          console.error("Failed to delete", error);
          setEmails(previousEmails); // Revert UI immediately if delete fails
      }
  };

  const [composeInitialData, setComposeInitialData] = useState({});

  const handleReply = (email) => {
      // Extract raw email address
      let replyTo = email.sender || '';
      if (replyTo.includes('<')) {
          replyTo = replyTo.split('<')[1].replace('>', '');
      }
      
      setComposeInitialData({
          to: replyTo,
          subject: email.subject.startsWith('Re:') ? email.subject : `Re: ${email.subject}`,
          body: `\n\n\nOn ${new Date(email.received_at).toLocaleString()}, ${email.sender} wrote:\n> ${email.snippet || ''}...`
      });
      setIsComposeOpen(true);
  };

  const handleComposeOpen = () => {
      setComposeInitialData({});
      setIsComposeOpen(true);
  };

    const handleActionComplete = (emailId) => {
        setEmails(emails.map(e => e.id === emailId ? { ...e, action_required: false } : e));
    };



    const handleAddToCalendar = async (email) => {
        if (!email.event_title || !email.event_date) return;
        try {
          showToast('Adding to Google Calendar...', 'info');
          const result = await addToCalendar(userId, email.event_title, email.event_date, email.snippet || email.subject);
          
          showToast('Event added successfully! 📅', 'success');
          
          // Clear "Action Required" status locally and on server
          setEmails(emails.map(e => e.id === email.id ? { ...e, action_required: false } : e));
          
          try {
             await dismissEmailAction(userId, email.id);
          } catch(ignore) { console.warn("Failed to sync dismissal", ignore); }

          if (result.event_link) {
             window.open(result.event_link, '_blank');
          }
        } catch (error) {
          console.error(error);
          showToast('Failed to add to calendar.', 'error');
        }
    };

    if (!userId) {
        return <div className="flex items-center justify-center h-screen text-gray-500">Checking authentication...</div>;
    }

    console.log("Dashboard Render. Emails:", emails?.length);

  return (
    <Layout 
        onComposeClick={handleComposeOpen}
        activeFolder={activeFolder}
        onFolderChange={setActiveFolder}
        onSearch={setSearchQuery}
    >
        {/* Notification Banner for AI Events */}
        {emails.length > 0 && (
            <NotificationBanner 
                emails={emails} 
                userId={userId} 
                onActionComplete={handleActionComplete} 
            />
        )}

        {/* Toolbar Area */}
        {!selectedEmail && (
            <div className="flex justify-between items-center px-4 py-2 border-b border-gray-100 bg-white sticky top-0 z-10">
                <div className="flex items-center gap-2">
                    {/* Sync Button */}
                    <button 
                         onClick={handleSync}
                         disabled={syncing}
                         className={`p-2 rounded-full hover:bg-gray-100 transition-colors ${syncing ? 'animate-spin text-blue-600' : 'text-gray-600'}`}
                         title="Sync Emails"
                    >
                        <RefreshCcw size={18} />
                    </button>
                    <span className="text-sm text-gray-500">
                        {loading ? 'Loading...' : `${emails?.length || 0} items`}
                    </span>
                </div>
                
                <div className="flex items-center gap-2">
                     <span className="text-xs text-gray-400">
                        {(page * limit) + 1}-{ (page * limit) + (emails?.length || 0) }
                     </span>
                     <div className="flex">
                         <button 
                             onClick={() => setPage(Math.max(0, page - 1))}
                             disabled={page === 0}
                             className={`p-2 rounded-full ${page === 0 ? 'text-gray-300' : 'hover:bg-gray-100 text-gray-600'}`}
                         >
                            <span className="sr-only">Previous</span>‹
                         </button>
                         <button 
                             onClick={() => setPage(page + 1)}
                             disabled={(emails?.length || 0) < limit} 
                             className={`p-2 rounded-full ${(emails?.length || 0) < limit ? 'text-gray-300' : 'hover:bg-gray-100 text-gray-600'}`}
                         >
                            <span className="sr-only">Next</span>›
                         </button>
                     </div>
                </div>
            </div>
        )}

        {/* Debug Error Display */}
        {debugError && (
             <div className="mx-4 mt-4 bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded text-sm mb-4">
                 <strong>Debug Error:</strong> {debugError}
             </div>
        )}

        {/* content */}
        {loading && (!emails || emails.length === 0) ? (
             <div className="flex flex-col items-center justify-center h-full text-gray-500 pb-20">
                 <div className="animate-spin mb-4"><RefreshCcw size={24}/></div>
                 <p>Loading your inbox...</p>
             </div>
        ) : selectedEmail ? (
            <EmailDetail 
                email={selectedEmail} 
                onBack={() => setSelectedEmail(null)} 
                onReply={handleReply}
            />
        ) : (
            <EmailList 
                emails={emails} 
                onEmailClick={setSelectedEmail} 
                onStar={handleStar}
                onDelete={handleDelete}
                onAddToCalendar={handleAddToCalendar}
            />
        )}
        
        <ComposeModal 
            isOpen={isComposeOpen} 
            onClose={() => setIsComposeOpen(false)} 
            initialData={composeInitialData}
        />
    </Layout>
  );
};

export default Dashboard;
