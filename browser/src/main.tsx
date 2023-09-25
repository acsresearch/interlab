import React from 'react'
import ReactDOM from 'react-dom/client'
import App from './App.tsx'
import './index.css'
import { SingleContextScreen } from './components/SingleContextScreen.tsx';
import { Context } from './model/Context.ts';

declare global {
  interface Window {
    initInterlab: unknown | undefined;
  }
}


function initInterlab(root: string, context?: Context) {
  ReactDOM.createRoot(document.getElementById(root)!).render(
    <React.StrictMode>
      {context ? <SingleContextScreen context={context} /> : <App />}
    </React.StrictMode>,
  )
}


window.initInterlab = initInterlab