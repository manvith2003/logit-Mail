import React from 'react';
import { Menu, Search, Settings, HelpCircle, Grip, LogOut } from 'lucide-react';
import { useNavigate } from 'react-router-dom';

const Header = ({ toggleSidebar, onSearch }) => {
  const [isProfileOpen, setIsProfileOpen] = React.useState(false);
  const navigate = useNavigate();

  const handleLogout = () => {
    localStorage.removeItem('magic_mail_user_id');
    navigate('/login');
  };

  return (
    <header className="flex items-center justify-between px-4 py-2 bg-white border-b border-gray-200 fixed w-full top-0 z-50 h-16">
      {/* Left: Logo & Menu */}
      <div className="flex items-center gap-4 w-60">
        <button 
          onClick={toggleSidebar}
          className="p-2 hover:bg-gray-100 rounded-full text-gray-600"
        >
          <Menu size={24} />
        </button>
        <div className="flex items-center gap-2 cursor-pointer">
          {/* Replaced with text/icon for now, can be an image logo */}
          <div className="w-8 h-8 flex items-center justify-center bg-indigo-600 text-white rounded font-bold text-xl">
            M
          </div>
          <span className="text-xl text-gray-600 font-medium">MagicMail</span>
        </div>
      </div>

      {/* Center: Search */}
      <div className="flex-1 max-w-3xl px-4">
        <div className="relative group">
          <div className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
            <Search size={20} className="text-gray-500 group-focus-within:text-gray-700" />
          </div>
          <input
            type="text"
            className="block w-full pl-12 pr-4 py-3 bg-gray-100 border-transparent rounded-lg focus:bg-white focus:border-transparent focus:ring-0 focus:shadow-md transition-shadow placeholder-gray-600 text-gray-700 sm:text-base outline-none"
            placeholder="Search mail (AI enabled)"
            onChange={(e) => onSearch(e.target.value)}
          />
          <div className="absolute inset-y-0 right-0 pr-3 flex items-center pointer-events-none">
             {/* Optional: Filter icon */}
          </div>
        </div>
      </div>

      {/* Right: Actions & Profile */}
      <div className="flex items-center gap-2 pl-4 w-auto justify-end relative">
        <button className="p-2 hover:bg-gray-100 rounded-full text-gray-600">
          <HelpCircle size={24} />
        </button>
        <button className="p-2 hover:bg-gray-100 rounded-full text-gray-600">
          <Settings size={24} />
        </button>
        <button className="p-2 hover:bg-gray-100 rounded-full text-gray-600">
            <Grip size={24} />
        </button>
        <div className="ml-2 relative">
           <div 
              onClick={() => setIsProfileOpen(!isProfileOpen)}
              className="w-8 h-8 rounded-full bg-purple-600 flex items-center justify-center text-white font-medium cursor-pointer select-none ring-2 ring-white hover:ring-gray-200"
            >
              U
           </div>
           
           {/* Dropdown */}
           {isProfileOpen && (
               <div className="absolute right-0 top-12 w-48 bg-white rounded-lg shadow-xl border border-gray-100 py-1 z-50">
                   <div className="px-4 py-3 border-b border-gray-100">
                       <p className="text-sm font-bold text-gray-900">User</p>
                       <p className="text-xs text-gray-500 truncate">user@example.com</p>
                   </div>
                   <button 
                        onClick={handleLogout}
                        className="w-full text-left px-4 py-2 text-sm text-red-600 hover:bg-gray-50 flex items-center gap-2"
                   >
                       <LogOut size={16} />
                       Sign Out
                   </button>
               </div>
           )}
        </div>
      </div>
    </header>
  );
};

export default Header;
