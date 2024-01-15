import React from 'react'
import ReactDOM from 'react-dom/client'
import App from './App.tsx'
import './index.css'
import { SingleNodeScreen } from './components/SingleNodeScreen.tsx';
import { TracingNode } from './model/TracingNode.ts';

declare global {
  interface Window {
    initTreeTraceBrowser: unknown | undefined;
  }
}


function initTreeTraceBrowser(root: string, node?: TracingNode) {
  ReactDOM.createRoot(document.getElementById(root)!).render(
    <React.StrictMode>
      {node ? <SingleNodeScreen node={node} /> : <App />}
    </React.StrictMode>,
  )
}


window.initTreeTraceBrowser = initTreeTraceBrowser