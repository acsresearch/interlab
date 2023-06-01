import React, { useState } from 'react';
import './App.css';
import { DataBrowser } from './components/DataBrowser';
import { InfoMessage, Severity } from './common/info';
import { info } from 'console';
import { Alert, Snackbar } from '@mui/material';

function App() {
  const [info, setInfo] = useState<InfoMessage[]>([]);

  function addInfo(severity: Severity, message: string) {
    setInfo((i) => [...i, { severity, message }]
    )
  }

  const onErrorClose = () => {
    setInfo((i) => i.slice(1));
  }

  return (
    <div className="App">
      <DataBrowser addInfo={addInfo} />
      <Snackbar open={info.length > 0} autoHideDuration={6000} onClose={onErrorClose} anchorOrigin={{ vertical: "top", horizontal: "center" }}>
        {info.length > 0 ? <Alert onClose={onErrorClose} severity={info[0]?.severity} sx={{ width: '100%' }}>
          {info[0]?.message}
        </Alert> : undefined}
      </Snackbar>
    </div>
  );
}

export default App;
