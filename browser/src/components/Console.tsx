import { Button, Fab, IconButton, Paper, Stack, TextField } from "@mui/material";
import { AddInfo } from "../common/info";
import { MutableRefObject, useRef, useState } from "react";
import SendIcon from '@mui/icons-material/Send';
import { useWebSocket } from "react-use-websocket/dist/lib/use-websocket";
import { WS_SERVICE } from "../config";
import { Item } from "./Item";
import { flushSync } from "react-dom";
import DynamicFormIcon from '@mui/icons-material/DynamicForm';
import { FormDialog } from "./FormDialog";
import ArrowRightIcon from '@mui/icons-material/ArrowRight';
import ArrowDropDownIcon from '@mui/icons-material/ArrowDropDown';
import { RJSFSchema } from "@rjsf/utils";


const SCHEMA_FORMAT = /\n?SCHEMA\s*```json\n(.*)```\s*END_OF_SCHEMA\n?/gs;

type Message = {
    id: number,
    text: string,
}

function MessageBody(props: { text: string, setSchema: (schema: string) => void }) {
    const parts = props.text.split(SCHEMA_FORMAT);
    const [openIndex, setOpenIndex] = useState<number | null>(null);

    return <Item style={{ backgroundColor: "#EEE" }}>{parts.map((part, i) => {
        if (i % 2 === 0) {
            return <div key={i} style={{ whiteSpace: "pre-wrap" }}>{part}</div>
        } else {
            const open = i === openIndex;
            return (<Item key={i}>
                <IconButton size="small" onClick={() => setOpenIndex(open ? null : i)}>{open ? <ArrowDropDownIcon /> : <ArrowRightIcon />}</IconButton>
                Schema
                <Button style={{ marginLeft: 40 }} color="primary" startIcon={<DynamicFormIcon />} onClick={() => props.setSchema(part)}>Open form</Button>
                {open && <div key={i} style={{ whiteSpace: "pre-wrap" }}>{part}</div>}
            </Item>)
        }
    })}</Item >
}

function MessageView(props: { messages: Message[], msgList: MutableRefObject<HTMLDivElement | null>, setSchema: (schema: string) => void }) {
    return (
        <Paper style={{
            height: "150",
            marginLeft: '10px',
            marginRight: '10px',
            padding: '10px',
            overflow: "auto",
            minHeight: "calc(100vh - 210px)",
            maxHeight: "calc(100vh - 210px)",
        }}>
            <Stack ref={props.msgList}>
                {props.messages.map((m, i) => <MessageBody key={m.id} text={m.text} setSchema={props.setSchema} />)}
            </Stack>
        </Paper>
    )
}


function UserInput(props: { enabled: boolean, input: string, setInput: (text: string) => void, onSubmit: () => void }) {

    return (
        <Stack>
            <div style={{ margin: '10px' }}>
                <div style={{ float: "left", width: "calc(100% - 145px)" }}>
                    <TextField label={props.enabled ? "Input" : "Input disabled"} fullWidth value={props.input} multiline={true} disabled={!props.enabled}
                        onChange={(e) => props.setInput(e.target.value)} onKeyDown={(e) => { if (e.ctrlKey && e.key === 'Enter') { props.onSubmit(); } }} />
                </div>
                <div style={{ float: "right", width: 140 }}>
                    <Fab disabled={!props.enabled} color="primary" aria-label="add" onClick={props.onSubmit}><SendIcon /></Fab>
                </div>
            </div>
        </Stack>)
}


export function Console(props: { addInfo: AddInfo }) {
    const msgList = useRef<HTMLDivElement | null>(null);
    const [title, setTitle] = useState<string | null>(null);
    const [messages, setMessages] = useState<Message[]>([]);
    const [enabledInput, setEnabledInput] = useState<boolean>(false);
    const [schema, setSchema] = useState<RJSFSchema | null>(null);
    const [input, setInput] = useState<string>("");


    const { sendMessage } = useWebSocket(WS_SERVICE, {
        onError: (e) => {
            props.addInfo("error", "Web socket error");
            console.log(e);
        },
        onMessage: (m) => {
            let msgs = JSON.parse(m.data);
            if (!Array.isArray(msgs)) {
                msgs = [msgs]
            }
            let new_messages = messages;
            let messages_changed = false;

            for (const msg of msgs) {
                if (msg.type === "init") {
                    setTitle(msg.name)
                    setMessages([])
                    setEnabledInput(false);
                }
                if (msg.type === "message") {
                    new_messages = [...new_messages, { id: msg.id, text: msg.text }];
                    if (new_messages.length > 2 && msg.id <= new_messages[new_messages.length - 2].id) {
                        new_messages.sort((a, b) => {
                            if (a.id < b.id) return -1;
                            if (a.id > b.id) return 1;
                            return 0;
                        })
                    }
                    messages_changed = true;
                }
                if (msg.type === "input") {
                    setEnabledInput(msg.value);
                }
            }
            if (messages_changed) {
                setMessages(new_messages);
                flushSync(() => {
                    setMessages(new_messages);
                });
                msgList.current?.lastElementChild?.scrollIntoView(true);
            }
        }
    });

    function parseSchema(text: string) {
        let schema: RJSFSchema;
        try {
            schema = JSON.parse(text);
            setSchema(schema);
        } catch (e) {
            props.addInfo("error", "" + e);
        }

    }

    function finishDialog(text?: string, send?: boolean) {
        setSchema(null);
        if (text) {
            if (send) {
                setInput("");
                sendMessage(text);
            } else {
                setInput(text)
            }
        }
    }

    function submit() {
        sendMessage(input);
        setInput("")
    }


    return <>
        {title && <div>{title}</div>}
        <MessageView msgList={msgList} messages={messages} setSchema={parseSchema} />
        <UserInput enabled={enabledInput} onSubmit={submit} input={input} setInput={setInput} />
        {schema && <FormDialog onClose={finishDialog} schema={schema} />}
    </>
}