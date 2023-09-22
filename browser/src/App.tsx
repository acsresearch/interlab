import { useState } from 'react';
import { DataBrowser } from './components/DataBrowser';
import { InfoMessage, Severity } from './common/info';
import { Alert, Snackbar } from '@mui/material';
import { RouterProvider, createBrowserRouter } from 'react-router-dom';
import { Console } from './components/Console';

function App() {
  const [info, setInfo] = useState<InfoMessage[]>([]);

  function addInfo(severity: Severity, message: string) {
    setInfo((i) => [...i, { severity, message }]
    )
  }

  const onErrorClose = () => {
    setInfo((i) => i.slice(1));
  }

  const router = createBrowserRouter([
    {
      path: "/",
      element: <DataBrowser addInfo={addInfo} />,
    },
    {
      path: "console",
      element: <Console addInfo={addInfo} />,
    },
  ]);

  return (
    <div className="App">
      <RouterProvider router={router} />
      <Snackbar open={info.length > 0} autoHideDuration={6000} onClose={onErrorClose} anchorOrigin={{ vertical: "top", horizontal: "center" }}>
        {info.length > 0 ? <Alert onClose={onErrorClose} severity={info[0]?.severity} sx={{ width: '100%' }}>
          {info[0]?.message}
        </Alert> : undefined}
      </Snackbar>
    </div>
  );
}

export default App;
