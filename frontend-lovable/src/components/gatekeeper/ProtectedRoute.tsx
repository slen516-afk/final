import { useState, useEffect, ReactNode } from 'react';
import { useNavigate } from 'react-router-dom';
import { useAppState } from '@/contexts/AppContext';
import GatekeeperOverlay from './GatekeeperOverlay';
import AuthModal from '../auth/AuthModal';

interface ProtectedRouteProps {
  children: ReactNode;
}

const ProtectedRoute = ({ children }: ProtectedRouteProps) => {
  const { isLoggedIn } = useAppState();
  const [showGatekeeper, setShowGatekeeper] = useState(false);
  const [showAuthModal, setShowAuthModal] = useState(false);
  const navigate = useNavigate();

  useEffect(() => {
    if (!isLoggedIn) {
      setShowGatekeeper(true);
    } else {
      setShowGatekeeper(false);
    }
  }, [isLoggedIn]);

  const handleLoginClick = () => {
    setShowAuthModal(true);
  };

  const handleAuthModalClose = (isOpen: boolean) => {
    setShowAuthModal(isOpen);
    if (!isOpen && !isLoggedIn) {
      // Navigate back to previous page when closing auth modal without logging in
      navigate(-1);
    }
  };

  return (
    <>
      {children}
      <GatekeeperOverlay 
        open={showGatekeeper} 
        onOpenChange={setShowGatekeeper}
        onLoginClick={handleLoginClick}
      />
      <AuthModal 
        open={showAuthModal} 
        onOpenChange={handleAuthModalClose}
      />
    </>
  );
};

export default ProtectedRoute;
