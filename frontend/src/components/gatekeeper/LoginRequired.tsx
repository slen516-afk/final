import { useState, useEffect, useRef, ReactNode } from 'react';
import { useNavigate } from 'react-router-dom';
import { useAppState } from '@/contexts/AppContext';
import AuthModal from '../auth/AuthModal';

interface LoginRequiredProps {
  children: ReactNode;
}

/**
 * Simplified access control component.
 * Only checks isLoggedIn status and shows Login Modal if not logged in.
 */
const LoginRequired = ({ children }: LoginRequiredProps) => {
  const { isLoggedIn } = useAppState();
  const [showAuthModal, setShowAuthModal] = useState(false);
  const navigate = useNavigate();
  const isLoggedInRef = useRef(isLoggedIn);
  isLoggedInRef.current = isLoggedIn;

  useEffect(() => {
    if (!isLoggedIn) {
      setShowAuthModal(true);
    }
  }, [isLoggedIn]);

  const handleAuthModalClose = (isOpen: boolean) => {
    setShowAuthModal(isOpen);
    if (!isOpen && !isLoggedInRef.current) {
      navigate(-1);
    }
  };

  return (
    <>
      {children}
      <AuthModal 
        open={showAuthModal && !isLoggedIn} 
        onOpenChange={handleAuthModalClose}
      />
    </>
  );
};

export default LoginRequired;
