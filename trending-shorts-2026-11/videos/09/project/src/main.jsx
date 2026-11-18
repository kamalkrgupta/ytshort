import React from 'react';
import { createRoot } from 'react-dom/client';
import '@fontsource-variable/inter';
import './theme.css';
import { Player } from './engine/Player.jsx';
import { scenes } from './scenes/index.js';

// No <StrictMode>: its double-mount in dev would start every scene animation twice.
createRoot(document.getElementById('root')).render(<Player scenes={scenes} />);
