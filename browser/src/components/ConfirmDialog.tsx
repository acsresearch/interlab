import { Button, Dialog, DialogActions, DialogContent, DialogTitle } from "@mui/material";
import React from "react";


export function ConfirmDialog(props: { open: boolean, title?: string, confirmText: string, onConfirm: (v: boolean) => void, children: React.ReactNode }) {
    return <Dialog
        open={props.open}
        onClose={() => props.onConfirm(false)}
        aria-labelledby="confirm-dialog"
    >
        {props.title && <DialogTitle id="confirm-dialog">{props.title}</DialogTitle>}
        <DialogContent>{props.children}</DialogContent>
        <DialogActions>
            <Button
                variant="outlined"
                onClick={() => props.onConfirm(false)}
            >
                Cancel
            </Button>
            <Button
                variant="contained"
                onClick={() => props.onConfirm(true)}
            >
                {props.confirmText}
            </Button>
        </DialogActions>
    </Dialog>
}