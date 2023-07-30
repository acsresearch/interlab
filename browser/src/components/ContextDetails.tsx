import { Button, Dialog, DialogActions, DialogContent, DialogTitle } from "@mui/material";
import { Context } from "../model/Context";
import { JsonView, allExpanded, darkStyles, defaultStyles } from 'react-json-view-lite';
import 'react-json-view-lite/dist/index.css';



export function ContextDetailsDialog(props: { context: Context, onClose: () => void }) {
    return <Dialog open={true} fullWidth>
        <DialogTitle>Context details</DialogTitle>
        <DialogContent>
            <JsonView data={props.context} shouldInitiallyExpand={(level) => level === 0} style={defaultStyles} />
        </DialogContent>
        <DialogActions>
            <Button variant="outlined" onClick={() => props.onClose()}>Cancel</Button>
        </DialogActions>
    </Dialog >
}

