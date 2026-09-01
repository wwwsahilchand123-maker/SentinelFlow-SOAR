import React, { useState, useEffect } from 'react';
import { Shield, Bell, Zap, LogOut, CheckCircle2, AlertTriangle, Play } from 'lucide-react';
import { useAuth } from '../../context/AuthContext';
import { notificationService, simulationService } from '../../services/api';
import { NotificationItem } from '../../types';

export const Navbar: React.FC = () => {
  const { user, logout } = useAuth();
  const [notifications, setNotifications] = useState<NotificationItem[]>([]);
  const [showNotifs, setShowNotifs] = useState(false);
  const [isSimulating, setIsSimulating] = useState(false);
  const [simMessage, setSimMessage] = useState<string | null>(null);

  const fetchNotifs = async () => {
    try {
      const data = await notificationService.getNotifications();
      setNotifications(data);
    } catch (err) {
      console.error(err);
    }
  };

  useEffect(() => {
    fetchNotifs();
    const interval = setInterval(fetchNotifs, 15000);
    return () => clearInterval(interval);
  }, []);

  const unreadCount = notifications.filter(n => !n.is_read).length;

  const handleQuickSim = async (scenario: string) => {
    try {
      setIsSimulating(true);
      await simulationService.triggerScenario(scenario);
      setSimMessage(`Triggered simulation: ${scenario.replace('-', ' ')}`);
      setTimeout(() => {
        setSimMessage(null);
        fetchNotifs();
      }, 3000);
    } catch (err) {
      console.error(err);
    } finally {
      setIsSimulating(false);
    }
  };

  const markAllRead = async () => {
    try {
      await notificationService.markAllRead();
      setNotifications(notifications.map(n => ({ ...n, is_read: true })));
    } catch (err) {
      console.error(err);
    }
  };

  return (
    <header className="h-16 border-b border-gray-800 bg-dark-900/90 backdrop-blur-md px-6 flex items-center justify-between sticky top-0 z-40">
      {/* Left section: Brand & System Status */}
      <div className="flex items-center space-x-4">
        <div className="flex items-center space-x-2.5">
          <div className="w-9 h-9 rounded-xl bg-gradient-to-tr from-cyan-600 to-cyan-400 flex items-center justify-center shadow-lg shadow-cyan-500/20">
            <Shield className="w-5 h-5 text-dark-900 stroke-[2.5]" />
          </div>
          <div>
            <h1 className="font-extrabold text-lg text-white tracking-wider flex items-center gap-1.5">
              SENTINEL<span className="text-cyan-400">FLOW</span>
              <span className="text-[10px] px-1.5 py-0.5 rounded bg-cyan-950/80 text-cyan-400 border border-cyan-800/60 font-mono font-semibold">SOAR v1.0</span>
            </h1>
          </div>
        </div>

        <div className="hidden lg:flex items-center space-x-2 pl-6 border-l border-gray-800 text-xs">
          <span className="w-2 h-2 rounded-full bg-emerald-400 animate-ping"></span>
          <span className="text-gray-400 font-mono">SOC STATUS:</span>
          <span className="text-emerald-400 font-semibold uppercase tracking-wider">DEFCON 4 • ACTIVE MONITORING</span>
        </div>
      </div>

      {/* Middle/Right: Quick Attack Simulators & Actions */}
      <div className="flex items-center space-x-3">
        {simMessage && (
          <div className="text-xs bg-cyan-950/80 border border-cyan-500/40 text-cyan-300 px-3 py-1.5 rounded-lg flex items-center space-x-2 animate-bounce">
            <Zap className="w-3.5 h-3.5" />
            <span>{simMessage}</span>
          </div>
        )}

        <div className="hidden md:flex items-center space-x-1.5 bg-dark-800/80 p-1 rounded-xl border border-gray-800">
          <button
            onClick={() => handleQuickSim('brute-force')}
            disabled={isSimulating}
            className="px-2.5 py-1 text-xs font-semibold text-gray-300 hover:text-cyan-400 hover:bg-gray-700/50 rounded-lg transition-colors flex items-center space-x-1.5"
            title="Simulate SSH/RDP Brute Force attack"
          >
            <Play className="w-3 h-3 text-cyan-400 fill-cyan-400" />
            <span>Sim: Brute Force</span>
          </button>
          <button
            onClick={() => handleQuickSim('phishing')}
            disabled={isSimulating}
            className="px-2.5 py-1 text-xs font-semibold text-gray-300 hover:text-orange-400 hover:bg-gray-700/50 rounded-lg transition-colors flex items-center space-x-1.5"
            title="Simulate Spear Phishing campaign"
          >
            <Play className="w-3 h-3 text-orange-400 fill-orange-400" />
            <span>Sim: Phishing</span>
          </button>
        </div>

        {/* Notifications Dropdown */}
        <div className="relative">
          <button
            onClick={() => setShowNotifs(!showNotifs)}
            className="p-2 rounded-xl text-gray-400 hover:text-white hover:bg-gray-800 transition-colors relative"
          >
            <Bell className="w-5 h-5" />
            {unreadCount > 0 && (
              <span className="absolute top-1 right-1 w-4 h-4 rounded-full bg-cyan-500 text-dark-900 font-extrabold text-[10px] flex items-center justify-center">
                {unreadCount}
              </span>
            )}
          </button>

          {showNotifs && (
            <div className="absolute right-0 mt-2 w-80 sm:w-96 glass-panel bg-dark-800 border border-gray-700 rounded-2xl shadow-2xl p-4 z-50 animate-in fade-in zoom-in-95 duration-150">
              <div className="flex items-center justify-between pb-3 border-b border-gray-800">
                <div className="flex items-center space-x-2">
                  <Bell className="w-4 h-4 text-cyan-400" />
                  <h4 className="text-sm font-bold text-white">Analyst Notifications</h4>
                </div>
                {unreadCount > 0 && (
                  <button
                    onClick={markAllRead}
                    className="text-xs text-cyan-400 hover:underline font-medium"
                  >
                    Mark all read
                  </button>
                )}
              </div>

              <div className="max-h-72 overflow-y-auto mt-2 space-y-2">
                {notifications.length === 0 ? (
                  <p className="text-xs text-gray-500 text-center py-6">No security alerts or messages</p>
                ) : (
                  notifications.map((n) => (
                    <div
                      key={n.id}
                      className={`p-2.5 rounded-xl border text-xs transition-all ${
                        n.is_read
                          ? 'bg-gray-900/40 border-gray-800 text-gray-400'
                          : 'bg-cyan-950/30 border-cyan-800/40 text-gray-200'
                      }`}
                    >
                      <div className="flex items-start justify-between">
                        <span className="font-semibold text-white">{n.title}</span>
                        <span className="text-[10px] text-gray-500 uppercase">{n.severity}</span>
                      </div>
                      <p className="mt-1 text-gray-300">{n.message}</p>
                    </div>
                  ))
                )}
              </div>
            </div>
          )}
        </div>

        {/* User Profile & Logout */}
        <div className="flex items-center space-x-3 pl-3 border-l border-gray-800">
          <div className="text-right hidden sm:block">
            <p className="text-xs font-bold text-white leading-none">{user?.full_name || user?.username}</p>
            <span className="text-[10px] font-mono text-cyan-400 uppercase font-semibold">{user?.role}</span>
          </div>
          <button
            onClick={logout}
            className="p-2 rounded-xl text-gray-400 hover:text-red-400 hover:bg-gray-800 transition-colors"
            title="Sign Out"
          >
            <LogOut className="w-5 h-5" />
          </button>
        </div>
      </div>
    </header>
  );
};
