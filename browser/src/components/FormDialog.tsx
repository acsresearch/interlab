import { Button, Dialog, DialogActions, DialogContent } from "@mui/material";
import Form from '@rjsf/mui';
import { RJSFSchema } from "@rjsf/utils";
import validator from '@rjsf/validator-ajv8';
import React from "react";


export function FormDialog(props: { schema: RJSFSchema | null, onClose: (result?: string, send?: boolean) => void }) {
    const [formData, setFormData] = React.useState(null);

    function onSubmit(send: boolean) {
        // TODO FORM validation
        const data = JSON.stringify(formData);
        props.onClose(data, send);
    }


    return <Dialog open={props.schema !== null} fullWidth>
        <DialogContent>
            <Form schema={props.schema!} validator={validator} formData={formData} onChange={(e) => setFormData(e.formData)}>
                <DialogActions>
                    <Button variant="outlined" onClick={() => props.onClose()}>Cancel</Button>
                    <Button variant="outlined" onClick={() => onSubmit(false)}>Make JSON</Button>
                    <Button variant="contained" onClick={() => onSubmit(true)}>Send message</Button>
                </DialogActions>
            </Form>
        </DialogContent>
    </Dialog >
}