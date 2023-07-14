import { Divider, Fab, Grid, Input, Paper, Stack, TextField } from "@mui/material";
import { AddInfo } from "../common/info";
import { MutableRefObject, useRef, useState } from "react";
import SendIcon from '@mui/icons-material/Send';
import { useWebSocket } from "react-use-websocket/dist/lib/use-websocket";
import { WS_SERVICE } from "../config";
import { Item } from "./Item";
import { flushSync } from "react-dom";


type Message = {
    id: number,
    text: string,
}


function MessageView(props: { messages: Message[], msgList: MutableRefObject<HTMLDivElement | null> }) {
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
                {props.messages.map((m, i) => <Item key={m.id}><div style={{ whiteSpace: "pre-wrap" }}>{m.text}</div></Item>)}
            </Stack>
        </Paper>
    )
}


function UserInput(props: { enabled: boolean, onSubmit: (text: string) => void }) {
    const [input, setInput] = useState<string>("");

    function submit() {
        props.onSubmit(input)
        setInput("")
    }

    return (
        <Stack>
            <Grid container style={{ margin: '10px' }}>
                <Grid item xs={11}>
                    <TextField label={props.enabled ? "Input" : "Input disabled"} fullWidth value={input} multiline={true} disabled={!props.enabled}
                        onChange={(e) => setInput(e.target.value)} onKeyDown={(e) => { if (e.ctrlKey && e.key === 'Enter') { submit(); } }} />
                </Grid>
                <Grid item xs={1}>
                    <Fab disabled={!props.enabled} color="primary" aria-label="add" onClick={() => submit()}><SendIcon /></Fab>
                </Grid>
            </Grid>
        </Stack>)
}


export function Console(props: { addInfo: AddInfo }) {
    const msgList = useRef<HTMLDivElement | null>(null);
    const [title, setTitle] = useState<string | null>(null);
    const [messages, setMessages] = useState<Message[]>([]);
    const [enabledInput, setEnabledInput] = useState<boolean>(false);

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
            console.log(msgs);

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


    return <>
        {title && <div>{title}</div>}
        <MessageView msgList={msgList} messages={messages} />
        <UserInput enabled={enabledInput} onSubmit={sendMessage} />
    </>
}