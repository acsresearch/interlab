import { Box, CircularProgress, Grid, IconButton, ListItemButton, ListItemText, Paper } from "@mui/material";
import { Context, gatherKinds } from "../model/Context";
import { ContextNode } from "./ContextNode";
import { useEffect, useState } from "react";
import axios from "axios";
import { SERVICE_PREFIX } from "../config";
import { callGuard } from "../common/guard";
import { AddInfo } from "../common/info";
import ToggleButton from '@mui/material/ToggleButton';

import SyncIcon from '@mui/icons-material/Sync';
import DoneIcon from '@mui/icons-material/Done';
import ErrorIcon from '@mui/icons-material/Error';
import { TagChip } from "./TagChip";

// type Root = {
//     name: string,
//     uuid: string,
// }

export enum OpenerMode {
    Toggle,
    Open,
    Close
}

export type Opener = (keys: string | string[], mode: OpenerMode) => void


function ListItem(props: { root: Context, selectedCtx: Context | null, selectRoot: (uid: string) => void }) {
    const { root, selectedCtx, selectRoot } = props;
    const primary = root.uid.slice(0, 40);
    let icon;
    let color;

    if (root.state === "open") {
        icon = <span style={{ paddingRight: 5 }}><CircularProgress size="1em" /></span>;
        color = "green";
    } else if (root.state === "error") {
        icon = <ErrorIcon sx={{ fontSize: "90%", paddingRight: 0.5, color: "red" }} />
        color = "red";
    } else {
        icon = <DoneIcon sx={{ fontSize: "90%", paddingRight: 0.5 }} />
    }

    return (
        <ListItemButton selected={selectedCtx !== null && root.uid === selectedCtx.uid} key={root.uid} component="a" onClick={() => selectRoot(root.uid)}>
            {icon} <ListItemText primary={<span>{primary} {root.tags?.map((t, i) => <TagChip key={i} tag={t} />)}</span>} primaryTypographyProps={{ fontSize: '80%', color: color }} />
        </ListItemButton>
    )
}

export function DataBrowser(props: { addInfo: AddInfo }) {
    const [roots, setRoots] = useState<Context[]>([]);
    const [selectedCtx, setSelectedCtx] = useState<Context | null>(null);
    let [opened, setOpened] = useState<Set<string>>(new Set());
    const [kinds, setKinds] = useState<Set<string>>(new Set());

    function refresh() {
        callGuard(async () => {
            const response1 = await axios.get(SERVICE_PREFIX + "/contexts/list");
            if (response1 === null) {
                return;
            }
            const uids = response1.data as string[];

            const forget_open = roots.filter(c => c.state !== 'open');
            const local_uids = new Set(forget_open.map(c => c.uid));
            const to_download: string[] = [];
            for (const uid of uids) {
                if (!local_uids.has(uid)) {
                    to_download.push(uid);
                }
            }
            const response2 = await axios.post(SERVICE_PREFIX + "/contexts/roots", { "uids": to_download });
            if (response2 === null) {
                return;
            }
            const new_roots = response2.data as Context[];
            const uids_set = new Set(uids);

            const final_roots = forget_open.filter((c) => uids_set.has(c.uid)).concat(new_roots);
            final_roots.sort()

            final_roots.sort((a, b) => {
                if (a.uid < b.uid) {
                    return -1;
                }
                if (a.uid > b.uid) {
                    return 1;
                }
                return 0;
            });

            setRoots(final_roots);

            if (selectedCtx === null && final_roots.length > 0) {
                selectRoot(final_roots[0].uid);
            } else if (selectedCtx !== null && final_roots.find((x) => x.uid === selectedCtx.uid)) {
                selectRoot(selectedCtx.uid);
            } else {
                setSelectedCtx(null);
            }
        }, props.addInfo);
    }

    function selectRoot(root: string) {
        callGuard(async () => {
            const response = await axios.get(SERVICE_PREFIX + "/contexts/uid/" + root);
            const ctx = response.data as Context;
            setSelectedCtx(ctx);
            setOpened((op) => {
                let o = new Set(op);
                o.add(root);
                if (newKinds.size !== kinds.size) {
                    newKinds.forEach((k) => {
                        if (!kinds.has(k)) {
                            o.add(k);
                        }
                    })
                }
                return o;
            })
            const newKinds = new Set(kinds);
            gatherKinds(ctx, newKinds);
            if (newKinds.size !== kinds.size) {
                setKinds(newKinds);
            }
        }, props.addInfo)
    }

    function setOpen(keys: string | string[], mode: OpenerMode) {
        setOpened((op) => {
            let o = new Set(op);
            if (!Array.isArray(keys)) {
                keys = [keys]
            }
            if (mode === OpenerMode.Toggle) {
                for (const key of keys) {
                    if (!o.delete(key)) {
                        o.add(key)
                    }
                }
            } else if (mode === OpenerMode.Open) {
                for (const key of keys) {
                    o.add(key)
                }
            } else {
                for (const key of keys) {
                    o.delete(key)
                }
            }
            return o;
        })

    }

    let sortedKinds = Array.from(kinds);

    // eslint-disable-next-line react-hooks/exhaustive-deps
    useEffect(() => { refresh() }, []);

    return <Grid container>
        <Grid item xs={2}>
            <IconButton onClick={refresh}><SyncIcon /></IconButton>
            <Paper style={{ maxHeight: "calc(100vh - 40px)", overflow: 'auto' }}>
                {roots.map((root) => <ListItem key={root.uid} root={root} selectedCtx={selectedCtx} selectRoot={selectRoot} />
                    // <ListItemButton selected={selectedCtx !== null && root.uid === selectedCtx.uid} key={root.uid} component="a" onClick={() => selectRoot(root.uid)}>
                    //     <ListItemText primary={root.uid.slice(0, 40)} primaryTypographyProps={{ fontSize: '80%' }} />
                    // </ListItemButton>
                )}
            </Paper>
        </Grid>
        <Grid item xs={9}>
            <Box
                m={1} //margin
                display="flex"
                justifyContent="flex-start"
                alignItems="flex-start"
            >
                {sortedKinds.map((kind) => <ToggleButton value={""} selected={opened.has(kind)} onChange={() => setOpen(kind, OpenerMode.Toggle)} key={kind}>{kind}</ToggleButton>)}
            </Box>
            {selectedCtx && <div style={{ maxHeight: "calc(100vh - 40px)", overflow: 'auto' }}><ContextNode context={selectedCtx} depth={0} opened={opened} setOpen={setOpen} /></div>}
            {roots.length === 0 && !selectedCtx && <span>No context registed in Data Browser</span>}
        </Grid>
    </Grid >
}