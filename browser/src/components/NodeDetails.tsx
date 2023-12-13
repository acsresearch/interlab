import { Button, Dialog, DialogActions, DialogContent, DialogTitle } from "@mui/material";
import { TracingNode } from "../model/TracingNode";
import { JsonView, defaultStyles } from 'react-json-view-lite';
import 'react-json-view-lite/dist/index.css';



export function NodeDetailsDialog(props: { node: TracingNode, onClose: () => void }) {
    return <Dialog open={true} fullWidth>
        <DialogTitle>Node details</DialogTitle>
        <DialogContent>
            <JsonView data={props.node} shouldInitiallyExpand={(level) => level === 0} style={defaultStyles} />
        </DialogContent>
        <DialogActions>
            <Button variant="outlined" onClick={() => props.onClose()}>Cancel</Button>
        </DialogActions>
    </Dialog >
}

