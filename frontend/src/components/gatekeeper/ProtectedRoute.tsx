import { useState, useEffect, useRef, ReactNode } from 'react';
import { useNavigate, useLocation } from 'react-router-dom';
import { useAppState } from '@/contexts/AppContext';
import GatekeeperOverlay from './GatekeeperOverlay';
import AuthModal from '../auth/AuthModal';

export type GateFlag =
  | 'isLoggedIn'
  | 'isResumeUploaded'
  | 'isPersonalityQuizDone'
  | 'isPersonalityTestDone'
  | 'isJobPreferenceQuizDone';

interface ProtectedRouteProps {
  children: ReactNode;
  /** Which flags must be satisfied. Defaults to ['isLoggedIn']. */
  requiredFlags?: GateFlag[];
}

const ProtectedRoute = ({
  children,
  requiredFlags = ['isLoggedIn'],
}: ProtectedRouteProps) => {
  const state = useAppState();
  const navigate = useNavigate();
  const location = useLocation();
  const [showAuthModal, setShowAuthModal] = useState(false);
  const isLoggedInRef = useRef(state.isLoggedIn);
  isLoggedInRef.current = state.isLoggedIn;
  // Track whether this component instance is still mounted
  const mountedRef = useRef(true);

  useEffect(() => {
    mountedRef.current = true;
    return () => {
      mountedRef.current = false;
    };
  }, []);

  const loginOnly = requiredFlags.length === 1 && requiredFlags[0] === 'isLoggedIn';

  // Determine which flags are missing
  const missingFlags = requiredFlags.filter((flag) => !state[flag]);
  const needsLogin = missingFlags.includes('isLoggedIn');
  const hasNonLoginMissing = missingFlags.some((f) => f !== 'isLoggedIn');

  const showGatekeeper = !needsLogin && hasNonLoginMissing && !loginOnly;

  useEffect(() => {
    if (needsLogin) {
      setShowAuthModal(true);
    }
  }, [needsLogin]);

  const handleAuthModalClose = (isOpen: boolean) => {
    setShowAuthModal(isOpen);
    if (!isOpen && !isLoggedInRef.current && mountedRef.current) {
      navigate(-1);
    }
  };

  const handleGatekeeperClose = (isOpen: boolean) => {
    if (!isOpen && mountedRef.current) {
      navigate(-1);
    }
  };

  const handleGatekeeperLogin = () => {
    setShowAuthModal(true);
  };

  return (
    <>
      {children}
      {showGatekeeper && (
        <GatekeeperOverlay
          open={showGatekeeper}
          onOpenChange={handleGatekeeperClose}
          onLoginClick={handleGatekeeperLogin}
          requiredFlags={requiredFlags}
        />
      )}
      <AuthModal
        open={showAuthModal}
        onOpenChange={handleAuthModalClose}
      />
    </>
  );
};

export default ProtectedRoute;
