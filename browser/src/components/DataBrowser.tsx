import { Box, Grid, IconButton, ListItemButton, ListItemText, Paper } from "@mui/material";
import { Context, gatherKinds } from "../model/Context";
import { ContextNode } from "./ContextNode";
import { useEffect, useState } from "react";
import axios from "axios";
import { SERVICE_PREFIX } from "../config";
import { callGuard } from "../common/guard";
import { AddInfo } from "../common/info";
import ToggleButton from '@mui/material/ToggleButton';

import SyncIcon from '@mui/icons-material/Sync';

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

export function DataBrowser(props: { addInfo: AddInfo }) {
    const [roots, setRoots] = useState<string[]>([]);
    const [selectedCtx, setSelectedCtx] = useState<Context | null>(null);
    let [opened, setOpened] = useState<Set<string>>(new Set());
    const [kinds, setKinds] = useState<Set<string>>(new Set());

    function refresh() {
        callGuard(async () => {
            const response = await axios.get(SERVICE_PREFIX + "/contexts/list");
            if (response === null) {
                return;
            }
            const rs = response.data as string[];
            rs.sort();
            setRoots(rs);
            if (selectedCtx === null && rs.length > 0) {
                selectRoot(rs[0]);
            } else if (selectedCtx !== null && rs.find((x) => x === selectedCtx.uid)) {
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
            <Paper>
                {roots.map((root) =>
                    <ListItemButton selected={selectedCtx !== null && root === selectedCtx.uid} key={root} component="a" onClick={() => selectRoot(root)}>
                        <ListItemText primary={root.slice(0, 40)} primaryTypographyProps={{ fontSize: '80%' }} />
                    </ListItemButton>
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
            {selectedCtx && <ContextNode context={selectedCtx} depth={0} opened={opened} setOpen={setOpen} />}
            {roots.length === 0 && !selectedCtx && <span>No context registed in Data Browser</span>}
        </Grid>
    </Grid >
}